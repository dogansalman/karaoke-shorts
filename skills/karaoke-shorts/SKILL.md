---
name: karaoke-shorts
description: Turn a song (mp3/mp4, e.g. from Suno) into a vertical YouTube Shorts / Instagram Reels video with word-by-word karaoke lyrics aligned to the audio, an equalizer animation in instrumental gaps, a hook title, and trimming under the 3-minute Shorts limit. Can build the video from a still image + mp3. Works well for Turkish lyrics.
---

# Karaoke Shorts

Builds a vertical (1080x1920) music video ready for YouTube Shorts and Instagram Reels:

- **Karaoke lyrics**: word timings from faster-whisper, aligned to the user's own lyrics so the on-screen text is exactly what they wrote. Two modes: `highlight` (whole line visible, sung word fills with colour) and `reveal` (words appear as they are sung).
- **Instrumental gaps**: an equalizer animation fades in when the voice stops and fades out just before the next line.
- **Hook title**: two-line title (white line + coloured box) rendered with Pillow, so Turkish characters (ş, ğ, İ, ı) are safe.
- **Still image + mp3 → video** with a slow Ken Burns zoom.
- **Shorts length**: trims to 2:58 with a fade-out if needed.

Reply in the user's language. Scripts live in this skill's `scripts/` folder; below `SK` means that folder.

## Defaults (ask only if the user cares)
- Highlight colour `#E83454`, font Poppins Bold, lyric size 100, mode `highlight`, colour delay 0.2 s, equalizer label `music` (use the user's language, e.g. `müzik`).
- Hook shown for the first 3 s; full length if the user asks or the background is a still image.
- Never overwrite originals. Work files go in `_tmp/`, outputs next to the source.

## Step 0: Setup
- `ffmpeg -version` and `ffmpeg -filters | grep " ass "` (needs libass). macOS: `brew install ffmpeg`.
- `python3 -m pip install pillow faster-whisper`
- Font: download Poppins Bold into `_tmp/fonts/` (https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf). If the user wants another font, use any TTF that covers their language.
- Ask for the lyrics if not given (for Suno songs: the text pasted into Suno) and save as `_tmp/lyrics.txt`. Section tags like `[Chorus]` are ignored automatically. Without lyrics, pass `-` and show the user words that may be misheard.

## Step 1: No video? Build one from an image + audio
Crop to fill 9:16 (no black bars). The Ken Burns zoom must use the frame counter `in`; `zoom+...` resets on a looped still image and produces no motion.
```
ffmpeg -y -loop 1 -framerate 30 -i IMAGE -i SONG.mp3 -filter_complex "[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,zoompan=z='min(1+in*0.00002,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p[v]" -map "[v]" -map 1:a -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -shortest _tmp/source.mp4
```
Then use `_tmp/source.mp4` as INPUT. Get the duration: `ffprobe -v error -show_entries format=duration -of csv=p=0 INPUT`.

## Step 2: Word timings
```
ffmpeg -y -i INPUT -vn -ac 1 -ar 16000 _tmp/audio.wav
```
Recommended — isolate vocals first; it makes timings much tighter (first run downloads ~2 GB, tell the user once):
```
python3 -m pip install demucs
python3 -m demucs --two-stems=vocals -n htdemucs -o _tmp/sep _tmp/audio.wav
ffmpeg -y -i _tmp/sep/htdemucs/audio/vocals.wav -ac 1 -ar 16000 _tmp/vocals.wav
```
If demucs fails, continue with `_tmp/audio.wav`.
```
python3 SK/align_lyrics.py _tmp/vocals.wav _tmp/lyrics.txt NAME --lang tr
```
Produces `NAME.srt` and `NAME.json`. The first run downloads the Whisper model (~1.6 GB); an `HF_TOKEN` warning is not an error.
- Report any `ESTIMATED TIMING` lines.
- Suno lyrics often contain phonetic spellings written only for pronunciation (Turkish examples: `Siyo`→`CEO`, `Sivi`→`CV`, `hedşat`→`headshot`, `İks Pi`→`XP`, `Cunyır`→`Junior`). Replace them with the normal spelling in `NAME.json` and `NAME.srt`, and tell the user what you changed.

## Step 3: Karaoke subtitles
```
python3 SK/make_karaoke_ass.py NAME.json _tmp/lyrics.ass --duration DURATION --mode highlight --delay 0.2 --label müzik
```
If the user says the colouring runs ahead of the voice, raise `--delay` (0.3–0.4); if it lags, lower it (0 or negative). `--size` changes text size, `--color` the highlight colour.

## Step 4: Hook PNG (if requested)
```
python3 SK/make_hook.py "TOP LINE" "BOX LINE" _tmp/fonts/Poppins-Bold.ttf _tmp/hook.png
```
Open the PNG with Read and check it. Keep the hook between 13% and 87% of the height so Instagram's 3:4 profile-grid crop doesn't cut it.

## Step 5: Render
With hook (first 3 s; remove `enable=...` for full length):
```
ffmpeg -y -i INPUT -i _tmp/hook.png -filter_complex "[0:v][1:v]overlay=0:0:enable='between(t,0,3)',ass=_tmp/lyrics.ass:fontsdir=_tmp/fonts,format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k _tmp/rendered.mp4
```
Without hook: `-vf "ass=_tmp/lyrics.ass:fontsdir=_tmp/fonts,format=yuv420p"`.

## Step 6: Shorts length
YouTube treats vertical videos up to 3:00 as Shorts, but a file that reads 3:00 can be a few frames over. If longer than 178 s:
```
ffmpeg -y -i _tmp/rendered.mp4 -t 178 -vf "fade=t=out:st=176:d=2" -af "afade=t=out:st=176:d=2" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k OUTPUT.mp4
```
Otherwise copy `_tmp/rendered.mp4` to OUTPUT.

## Step 7: Verify (do not skip)
- `ffprobe`: duration < 178 s, 1080x1920.
- Extract and Read frames: the hook (t=1), one instrumental gap (two lines more than 2.5 s apart in NAME.json), and the middle of a word (is that word coloured?). Check special characters.
- Delete `_tmp/`; keep `NAME.srt` and `NAME.json` (usable in CapCut etc.).
- Tell the user the output path, duration and any estimated lines.

## Good practice
- Don't place real brand logos in generated visuals; use a parody design.
- Warn if a background contains drug symbols or other content platforms restrict.
- Remind the user to tick "Altered or synthetic content" on YouTube for realistic AI visuals.
