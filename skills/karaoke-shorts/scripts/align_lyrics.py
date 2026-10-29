#!/usr/bin/env python3
"""Find word-level timings in a song and align them to the known lyrics.

Writes NAME.srt (line subtitles) and NAME.json (word timings for karaoke).

    python3 align_lyrics.py vocals.wav lyrics.txt NAME [--lang tr] [--model large-v3-turbo]

Use "-" instead of lyrics.txt to transcribe without lyrics (text comes from Whisper).
Lines in brackets such as [Verse 1] or [Chorus] and empty lines are ignored.
"""
import argparse, json, re
from difflib import SequenceMatcher
from pathlib import Path


def norm(w):
    # Turkish-aware lowercase: İ->i, I->ı before lower(); strip punctuation
    w = w.replace("İ", "i").replace("I", "ı").lower()
    return re.sub(r"[^\w]", "", w)


def srt_time(t):
    ms = int(round(max(0, t) * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def read_lyrics(path):
    out = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        s = re.sub(r"\[[^\]]*\]", "", raw).strip()
        if s and norm(s):
            out.append(s)
    return out


def whisper_words(audio, lyrics, lang, model_name):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(
        audio, language=lang, word_timestamps=True, vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500}, condition_on_previous_text=False,
        initial_prompt=(" ".join(lyrics)[:400] if lyrics else None), beam_size=5)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in (s.words or []) if norm(w.word)]


def align(lyrics, words):
    """Similarity-scored Needleman-Wunsch alignment of lyric words to recognised words.
    Unmatched lyric words are interpolated between their timed neighbours."""
    tok = [(li, t) for li, line in enumerate(lyrics) for t in line.split() if norm(t)]
    lw = [norm(t) for _, t in tok]; tw = [norm(w[2]) for w in words]
    n, m, GAP = len(lw), len(tw), -0.4

    def sim(a, b):
        r = SequenceMatcher(None, a, b).ratio()
        return r if r >= 0.6 else -0.6

    S = [[0.0] * (m + 1) for _ in range(n + 1)]; B = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): S[i][0], B[i][0] = i * GAP, 1
    for j in range(1, m + 1): S[0][j], B[0][j] = j * GAP, 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d = S[i-1][j-1] + sim(lw[i-1], tw[j-1]); u = S[i-1][j] + GAP; l = S[i][j-1] + GAP
            S[i][j] = max(d, u, l); B[i][j] = 0 if S[i][j] == d else (1 if S[i][j] == u else 2)
    tm = [None] * n; i, j = n, m
    while i > 0 and j > 0:
        if B[i][j] == 0:
            if sim(lw[i-1], tw[j-1]) > 0: tm[i-1] = (words[j-1][0], words[j-1][1])
            i, j = i - 1, j - 1
        elif B[i][j] == 1: i -= 1
        else: j -= 1

    guessed = {}
    k = 0
    while k < n:
        if tm[k] is not None: k += 1; continue
        a = k
        while k < n and tm[k] is None: k += 1
        start = tm[a - 1][1] if a > 0 else (tm[k][0] - 0.4 * (k - a) if k < n else 0.0)
        end = tm[k][0] if k < n else start + 0.4 * (k - a)
        if end - start < 0.15 * (k - a): end = start + 0.3 * (k - a)
        total = sum(len(tok[q][1]) for q in range(a, k)); cur = start
        for q in range(a, k):
            d = (end - start) * len(tok[q][1]) / total
            tm[q] = (cur, cur + d * 0.9); cur += d
            guessed[tok[q][0]] = guessed.get(tok[q][0], 0) + 1

    lines = [{"start": None, "end": None, "words": []} for _ in lyrics]
    for (li, t), (s, e) in zip(tok, tm):
        lines[li]["words"].append({"w": t, "s": round(s, 3), "e": round(e, 3)})
    for ln in lines:
        ln["start"] = ln["words"][0]["s"]; ln["end"] = ln["words"][-1]["e"]
    mostly_guessed = [li for li, c in guessed.items() if c * 2 > len(lines[li]["words"])]
    return lines, sorted(mostly_guessed)


def free_lines(words, max_chars=42, max_gap=0.8):
    lines, cur = [], []
    for w in words:
        if cur and (w[0] - cur[-1][1] > max_gap or len(" ".join(x[2] for x in cur + [w])) > max_chars):
            lines.append(cur); cur = []
        cur.append(w)
    if cur: lines.append(cur)
    return [{"start": c[0][0], "end": c[-1][1], "words": [{"w": x[2], "s": x[0], "e": x[1]} for x in c]} for c in lines]


def write_outputs(lines, name):
    json.dump({"lines": lines}, open(name + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(name + ".srt", "w", encoding="utf-8") as f:
        for i, ln in enumerate(lines, 1):
            nxt = lines[i]["start"] if i < len(lines) else ln["end"] + 1
            e = min(max(ln["end"] + 0.3, ln["start"] + 1.0), nxt - 0.05)
            f.write(f"{i}\n{srt_time(ln['start'])} --> {srt_time(e)}\n{' '.join(w['w'] for w in ln['words'])}\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio"); ap.add_argument("lyrics", help='lyrics .txt, or "-" for none'); ap.add_argument("name")
    ap.add_argument("--lang", default="tr", help="Whisper language code (default: tr)")
    ap.add_argument("--model", default="large-v3-turbo", help="faster-whisper model (default: large-v3-turbo)")
    a = ap.parse_args()
    lyrics = read_lyrics(a.lyrics) if a.lyrics != "-" else None
    words = whisper_words(a.audio, lyrics, a.lang, a.model)
    if lyrics:
        lines, guessed = align(lyrics, words)
    else:
        lines, guessed = free_lines(words), []
    write_outputs(lines, a.name)
    print(f"{len(lines)} lines -> {a.name}.srt, {a.name}.json")
    for li in guessed:
        print("ESTIMATED TIMING:", lyrics[li])
