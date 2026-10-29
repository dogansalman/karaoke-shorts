# Karaoke Shorts 🎤

A Claude Code skill that turns a song into a vertical **YouTube Shorts / Instagram Reels** video with **word-by-word karaoke lyrics**.

Made for AI music (Suno and similar), works with any song, and handles **Turkish** lyrics properly (ş, ğ, İ, ı).

<p align="center"><img src="docs/demo.gif" width="300" alt="Karaoke Shorts demo"></p>

**[Türkçe açıklama aşağıda ↓](#türkçe)**

## What it does

- 🎯 **Karaoke lyrics synced to the voice.** Word timings come from Whisper and are aligned to *your* lyrics, so the on-screen text is exactly what you wrote, even when Whisper mishears a word.
  - `highlight` mode: the whole line is visible and the sung word fills with colour.
  - `reveal` mode: words appear one by one as they are sung.
- 🎚️ **Instrumental gaps get an equalizer animation** that fades in when the voice stops and fades out right before the next line.
- 🪝 **Hook title**: a two-line title (white line + coloured box) for the first seconds, Instagram-grid safe.
- 🖼️ **Still image + mp3 → video** with a slow Ken Burns zoom.
- ✂️ **Shorts-ready**: trims to 2:58 with a fade-out so YouTube keeps it a Short.
- 🎙️ **Optional vocal isolation** (demucs) for tighter timing on dense mixes.

## Install

In Claude Code:

```
/plugin marketplace add dogansalman/karaoke-shorts
/plugin install karaoke-shorts@karaoke-shorts
```

Then run `/reload-plugins` (or restart Claude Code).

Or copy the skill folder manually:

```
git clone https://github.com/dogansalman/karaoke-shorts
mkdir -p ~/.claude/skills
cp -r karaoke-shorts/skills/karaoke-shorts ~/.claude/skills/
```

Then restart Claude Code.

**Check it worked:** type `/` in Claude Code and look for `karaoke-shorts`, or ask *"Which skills do you have?"*

### Requirements

- `ffmpeg` with libass (macOS: `brew install ffmpeg`)
- Python 3.9+ with `pip install pillow faster-whisper`
- Optional: `pip install demucs` for vocal isolation
- First run downloads the Whisper model (~1.6 GB) and, if used, demucs (~2 GB). Everything runs locally; no API keys.

## Usage

Open Claude Code in the folder with your files and just ask:

```
song.mp3 and cover.jpg are in folder 4. Make a Shorts video with cover.jpg as the background,
karaoke lyrics in reveal mode and the hook "NEWLYWEDS ONLY" / "48 MONTHS OF INSTALLMENTS".
Lyrics:
...paste your lyrics...
```

Claude follows the skill: builds the video, aligns the lyrics, renders the karaoke subtitles and the equalizer, adds the hook, trims to Shorts length and checks a few frames before handing it back. You also get `.srt` and `.json` timing files you can reuse in CapCut or elsewhere.

### Example prompts

**Image + song → full Shorts video**
```
Use cover.jpg as the background and song.mp3 as the audio. Make a Shorts video with karaoke
lyrics in highlight mode. Lyrics:
...
```

**You already have a video**
```
Add word-by-word karaoke lyrics to clip.mp4 and trim it for Shorts. Lyrics:
...
```

**Words appear as they are sung, with a hook title**
```
Karaoke video from song.mp3 and bg.png, reveal mode. Hook for the first 3 seconds:
"WAIT FOR THE CHORUS" / "YOU'LL RELATE". Lyrics:
...
```

**Your own look**
```
Same as before but highlight colour #FFD23F, bigger text (size 120), and no "music" label
under the equalizer.
```

**Fixing the sync**
```
The colouring runs a bit ahead of the voice, shift it later and render again.
```

**Only the subtitle files (for CapCut, Premiere...)**
```
Just create the .srt and karaoke timing files from song.mp3, no video. Lyrics:
...
```

**No lyrics at hand**
```
Make a karaoke Shorts video from song.mp4. I don't have the lyrics, transcribe them
and show me words that might be misheard before rendering.
```

**Another language**
```
The song is in English. Make a karaoke Shorts video from track.mp3 and photo.jpg. Lyrics:
...
```

**Batch**
```
Folders 1 to 4 each have a song.mp3 and a cover image. Make a Shorts video for each, lyrics are
in the lyrics.txt file inside every folder.
```

Tuning:

- Colouring runs ahead of the voice? Say so; Claude raises `--delay` (default 0.2 s).
- Different colour, font or text size: `--color`, `--font`, `--size`.
- Lyrics in another language: `--lang en` (any Whisper language code).

## Scripts

The scripts also work on their own:

| Script | What it does |
|---|---|
| `align_lyrics.py` | Whisper word timings aligned to your lyrics → `.srt` + `.json` |
| `make_karaoke_ass.py` | `.json` → karaoke `.ass` subtitles + equalizer in instrumental gaps |
| `make_hook.py` | Two-line hook title as a transparent PNG |

Run any of them with `-h` for options.

---

## Türkçe

Bir şarkıyı, **kelime kelime renklenen karaoke sözlerle** dikey bir **YouTube Shorts / Instagram Reels** videosuna dönüştüren bir Claude Code skill'i.

Suno gibi yapay zeka müzik araçları için yapıldı, ama her şarkıyla çalışır. Türkçe karakterleri (ş, ğ, İ, ı) sorunsuz işler.

**Neler yapar:**

- 🎯 **Sesle senkron karaoke sözler.** Kelime zamanlarını Whisper bulur, metin birebir senin sözlerinden alınır. Whisper bir kelimeyi yanlış duysa bile ekranda doğrusu yazar.
  - `highlight`: satır ekranda durur, söylenen kelime renklenir.
  - `reveal`: kelimeler söylendikçe tek tek belirir.
- 🎚️ **Müzik aralarında ekolayzır animasyonu:** vokal susunca belirir, sözler başlamadan kaybolur.
- 🪝 **Kanca başlığı:** beyaz satır ve renkli kutudan oluşan, Instagram ızgarasına uygun iki satırlık başlık.
- 🖼️ **Görsel + mp3'ten video:** yavaş yakınlaşma efektiyle.
- ✂️ **Shorts'a hazır:** gerekirse 2:58'e kırpar ve sonuna fade out ekler.

**Gereksinimler** (bilgisayarına bir kere kurulur):

```
brew install ffmpeg
python3 -m pip install pillow faster-whisper
python3 -m pip install demucs   # isteğe bağlı: vokal ayırma, zamanlamayı iyileştirir
```

`brew` yoksa önce [Homebrew](https://brew.sh)'u kur. Windows'ta ffmpeg'i [ffmpeg.org](https://ffmpeg.org/download.html)'dan indir. İlk kullanımda Whisper modeli (~1,6 GB) ve kullanılırsa demucs (~2 GB) iner. Her şey kendi bilgisayarında çalışır, API anahtarı gerekmez.

**Kurulum, yol 1 (önerilen):** Claude Code'u aç ve şunları yaz:

```
/plugin marketplace add dogansalman/karaoke-shorts
/plugin install karaoke-shorts@karaoke-shorts
/reload-plugins
```

**Kurulum, yol 2 (elle):** Terminal'de:

```
git clone https://github.com/dogansalman/karaoke-shorts
mkdir -p ~/.claude/skills
cp -r karaoke-shorts/skills/karaoke-shorts ~/.claude/skills/
```

Sonra Claude Code'u kapatıp yeniden aç.

**Kontrol:** Claude Code'da `/` yaz, listede `karaoke-shorts` görünüyorsa kurulum tamam. Ya da Claude'a *"Hangi skill'lerin var?"* diye sor.

**Önemli:** Claude Code'u videolarının bulunduğu klasörde aç (`cd ~/Desktop/videolar` ve ardından `claude`). Claude sadece açıldığı klasördeki dosyalara erişebilir.

**Kullanım:** Dosyaların olduğu klasörde Claude Code'u aç ve ne istediğini yaz:

```
4 klasöründe song.mp3 ve kapak.jpg var. kapak.jpg arka planlı bir Shorts videosu yap,
karaoke sözler reveal modunda olsun, kanca: "YENİ EVLİLERE ÖZEL" / "TAKSİT 48 AY".
Sözler:
...sözleri buraya yapıştır...
```

**Örnek prompt'lar:**

Görsel + şarkıdan tam video:
```
kapak.jpg arka plan, sarki.mp3 ses olsun. Karaoke sözlü bir Shorts videosu yap, highlight modunda.
Sözler:
...
```

Hazır videoya altyazı:
```
klip.mp4'e kelime kelime karaoke altyazı ekle ve Shorts için kırp. Sözler:
...
```

Kelimeler söylendikçe belirsin, kanca başlığıyla:
```
sarki.mp3 ve arka.png'den karaoke video yap, reveal modunda. İlk 3 saniye kanca:
"NAKARATI BEKLE" / "KENDİNİ BULACAKSIN". Sözler:
...
```

Kendi görünümün:
```
Aynısını yap ama renk #FFD23F olsun, yazılar daha büyük (120) olsun, ekolayzırın altındaki
"müzik" yazısı olmasın.
```

Senkron düzeltme:
```
Renklendirme sesin biraz önünde gidiyor, biraz geciktirip tekrar oluştur.
```

Sadece altyazı dosyası (CapCut vb. için):
```
Video yapma, sadece sarki.mp3'ten .srt ve karaoke zamanlama dosyalarını çıkar. Sözler:
...
```

Sözler elinde yoksa:
```
sarki.mp4'ten karaoke Shorts videosu yap. Sözler elimde yok; sen çıkar, oluşturmadan önce
yanlış duyulmuş olabilecek kelimeleri bana göster.
```

Toplu iş:
```
1'den 4'e kadar klasörlerin her birinde bir sarki.mp3 ve bir kapak görseli var. Her biri için
Shorts videosu yap; sözler her klasördeki sozler.txt dosyasında.
```

**Suno ipucu:** Suno'ya telaffuz için fonetik yazdığın kelimeleri (ör. `Siyo` → CEO, `Sivi` → CV) Claude altyazıda normal yazımına çevirir.

## License

MIT. Poppins (downloaded at runtime, not bundled) is licensed under the SIL Open Font License. faster-whisper and demucs are MIT licensed.
