#!/usr/bin/env python3
"""Build a karaoke ASS subtitle file from word timings, plus an equalizer animation
in instrumental gaps (fades in after a lyric ends, fades out before the next one).

    python3 make_karaoke_ass.py NAME.json out.ass --duration 178 [--mode highlight|reveal]
        [--delay 0.2] [--color "#E83454"] [--font Poppins] [--size 100] [--label music]

Modes:
  highlight  whole line is visible, the sung word fills with --color
  reveal     words appear as they are sung, current word in --color, earlier words white
--delay shifts the colouring later (seconds); raise it if colouring runs ahead of the voice.
"""
import argparse, json, random

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("timings"); ap.add_argument("out")
ap.add_argument("--duration", type=float, default=None, help="video length in seconds (for the outro gap)")
ap.add_argument("--mode", choices=["highlight", "reveal"], default="highlight")
ap.add_argument("--delay", type=float, default=0.2)
ap.add_argument("--color", default="#E83454", help="highlight colour, #RRGGBB")
ap.add_argument("--font", default="Poppins")
ap.add_argument("--size", type=int, default=100, help="lyric font size at 1080x1920")
ap.add_argument("--label", default="music", help='text under the equalizer, "" for none')
ap.add_argument("--min-gap", type=float, default=2.5, help="show equalizer in gaps longer than this")
ap.add_argument("--width", type=int, default=1080); ap.add_argument("--height", type=int, default=1920)
a = ap.parse_args()

lines = json.load(open(a.timings, encoding="utf-8"))["lines"]
for ln in lines:
    for w in ln["words"]:
        w["s"] += a.delay; w["e"] += a.delay
dur = a.duration if a.duration else (lines[-1]["end"] + 3 if lines else 0)

W, H = a.width, a.height
sc = W / 1080
LYR_Y = int(H * 0.80)                     # lyric baseline, above the Shorts/Reels UI
hx = a.color.lstrip("#")
SUNG = f"&H00{hx[4:6]}{hx[2:4]}{hx[0:2]}".upper()   # ASS colours are BGR
WHITE = "&H00FFFFFF"


def t(x):
    x = max(0.0, x)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02}:{x % 60:05.2f}"


def esc(s):
    return s.replace("{", "(").replace("}", ")").replace("\\", "/")


head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lyric,{a.font},{int(a.size * sc)},{SUNG},{WHITE},&H00141414,&H96000000,-1,0,0,0,100,100,0,0,1,{8 * sc:.0f},{4 * sc:.0f},2,{int(60 * sc)},{int(60 * sc)},{H - LYR_Y},1
Style: Bar,{a.font},10,{WHITE},{WHITE},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []

# --- karaoke lines ---
LEAD = 0.25
for i, ln in enumerate(lines):
    st = ln["start"] - LEAD
    nxt = lines[i + 1]["start"] - LEAD if i + 1 < len(lines) else ln["end"] + 1.0
    en = min(ln["end"] + a.delay + 0.6, nxt - 0.02)
    parts, cur = [], st
    for w in ln["words"]:
        if a.mode == "reveal":
            s0 = int(round((w["s"] - st) * 1000)); e0 = int(round((w["e"] - st) * 1000))
            parts.append(f"{{\\alpha&HFF&\\1c{SUNG}&\\t({s0},{s0 + 90},\\alpha&H00&)\\t({e0},{e0 + 150},\\1c{WHITE}&)}}{esc(w['w'])} ")
            continue
        gap = w["s"] - cur
        if gap > 0.01:
            parts.append(f"{{\\k{int(round(gap * 100))}}}")
        d = max(0.05, w["e"] - max(w["s"], cur))
        parts.append(f"{{\\kf{int(round(d * 100))}}}{esc(w['w'])} ")
        cur = max(cur, w["s"]) + d
    ev.append(f"Dialogue: 1,{t(st)},{t(en)},Lyric,,0,0,0,,{{\\fad(150,120)}}" + "".join(parts).rstrip())

# --- equalizer in instrumental gaps ---
gaps, prev_end = [], 0.0
for ln in lines:
    if ln["start"] - prev_end >= a.min_gap:
        gaps.append((prev_end, ln["start"]))
    prev_end = max(prev_end, ln["end"])
if dur - prev_end >= a.min_gap:
    gaps.append((prev_end, dur))

random.seed(3)
NBAR, BW, GAPX, BH = 11, int(30 * sc), int(20 * sc), int(220 * sc)
EQ_Y = H // 2 + BH // 2                   # bars centred on screen
x0 = (W - (NBAR * BW + (NBAR - 1) * GAPX)) // 2
for gs, ge in gaps:
    g0, g1 = gs + 0.35, ge - 0.35
    if g1 - g0 < 1.5:
        continue
    L = g1 - g0
    for k in range(NBAR):
        x = x0 + k * (BW + GAPX) + BW // 2
        col = SUNG if k % 2 == 0 else WHITE
        tags, tt, step = [], 0, 220 + k * 7
        while tt < L * 1000:
            tags.append(f"\\t({tt},{tt + step},\\fscy{random.randint(18, 100)})")
            tt += step
        draw = f"m 0 0 l {BW} 0 l {BW} {BH} l 0 {BH}"
        ev.append(f"Dialogue: 0,{t(g0)},{t(g1)},Bar,,0,0,0,,{{\\an2\\pos({x},{EQ_Y})\\1c{col}&\\fscy30\\fad(500,500)\\p1{''.join(tags)}}}{draw}")
    if a.label:
        ev.append(f"Dialogue: 0,{t(g0)},{t(g1)},Lyric,,0,0,0,,{{\\an2\\pos({W // 2},{EQ_Y + int(90 * sc)})\\fs{int(56 * sc)}\\bord{int(3 * sc)}\\shad0\\1c{WHITE}&\\fad(500,500)}}{esc(a.label)}")

open(a.out, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
print(f"{len(lines)} lines, {len(gaps)} instrumental gaps -> {a.out}")
