# 🎥 PyVideoKit

A collection of Python scripts to automate common video and audio processing tasks using FFmpeg and SoX.
These scripts are designed to be easy to use, with support for drag-and-drop input and desktop notifications.

## ✨ Features

- 📼 **VHS Effect**: Apply a retro VHS visual and audio effect to your videos.
- ✂️ **Video Trimming**: Easily cut videos by specifying start and end timestamps (or via an interactive `rofi` prompt).
- 🔗 **Concatenation**: Join multiple video files together without re‑encoding.
- 🎬 **Fading**: Add fade-in and fade-out effects to video and audio.
- 🔊 **Audio Extraction**: Extract audio tracks from video files.
- 🔄 **Format Conversion**: Convert videos to FFV1 (lossless) or prepare them for YouTube (ProRes 422 HQ, 4K upscaling).
- 🔔 **Notifications**: Integrated `dunstify` support for desktop notifications on Linux.

## 📦 Requirements

- **Python 3.10+**
- **FFmpeg** and **FFprobe** (usually provided by the `ffmpeg` package)
- **SoX (Sound eXchange)** – used by the VHS audio pipeline
- **Dunst + dunstify** (optional, but recommended for notifications)
- **rofi** (optional, only required for `trim-video --interactive`)

---

## 📥 Installing dependencies

### 🐧 Fedora‑based distributions (Fedora, Nobara, etc.)

```bash
sudo dnf install ffmpeg sox dunst rofi python3 python3-pip
```

### 🐧 Debian‑based distributions (Debian, Ubuntu, Linux Mint, etc.)

```bash
sudo apt update
sudo apt install ffmpeg sox libsox-fmt-all dunst rofi python3 python3-pip
```

### 🐧 Arch‑based distributions (Arch Linux, EndeavourOS, Manjaro, etc.)

```bash
sudo pacman -S ffmpeg sox dunst rofi python python-pip
```

> 💡 `rofi` is only needed if you want the interactive trimming mode (`trim-video --interactive`).
> Without it, all tools work via normal command‑line arguments.

---

## 📦 Installing PyVideoKit

### 🏹 On Arch‑based systems

You can install PyVideoKit directly from the AUR.

1. **Using your favourite AUR helper** (e.g. `yay`, `paru`):

   ```bash
   yay -S pyvideokit
   # or
   paru -S pyvideokit
   ```

2. **Building manually from the AUR `PKGBUILD`**

   ```bash
   git clone https://aur.archlinux.org/pyvideokit.git
   cd pyvideokit
   makepkg -si
   ```

   This will:
   - Resolve and install build dependencies.
   - Build the package.
   - Install PyVideoKit and its runtime dependencies.

3. **Installing from a prebuilt `.pkg.tar.zst` (release asset)**

   ```bash
   sudo pacman -U pyvideokit-<version>-any.pkg.tar.zst
   ```

---

### 🐧 On other Linux distributions

Once the system dependencies are installed, you have several options:

#### 1. Install from a prebuilt wheel (`.whl`)

Download the `.whl` file from the release assets and run:

```bash
pip install ./pyvideokit-<version>-py3-none-any.whl
# or, if you really want a global install:
sudo pip install ./pyvideokit-<version>-py3-none-any.whl
```

> 🔐 Using `sudo pip` is not generally recommended; prefer virtualenvs or `pip install --user`
> if you don't want to touch the system Python.

#### 2. Build the wheel yourself or install directly from the source tree

From the project root:

```bash
# Option A: build a wheel
pip install build
python3 -m build
pip install dist/pyvideokit-*-py3-none-any.whl

# Option B: install directly from the source tree
pip install .
# or (system‑wide, not usually recommended)
sudo pip install .
```

#### 3. Use the scripts without installing a system package

If you prefer to keep things “portable” and decide yourself where to store the scripts:

1. Clone or download the repository.
2. Keep the `pyvideokit/` package directory (with all `.py` files and `__init__.py`) together.
3. Run the tools using the `-m` module syntax:

   ```bash
   # From the project root (where pyvideokit/ lives)
   python3 -m pyvideokit.apply_vhs_effect /path/to/video.mp4
   python3 -m pyvideokit.trim_video -i /path/to/video.mp4 --start 10 --end 20
   ```

You can move the `pyvideokit/` directory anywhere you like (e.g. `~/apps/pyvideokit`) and either:

- `cd` into its parent directory before running `python3 -m pyvideokit.<tool>`, or
- add that parent directory to your `PYTHONPATH`.

No `pip install` is required for this mode.

---

## 🚀 Usage

### ▶️ Using the installed commands

If you installed PyVideoKit via AUR or `pip`, you should have the following commands in your `$PATH`:

- `apply-vhs-effect`
- `trim-video`
- `concat-videos`
- `fade-video`
- `extract-audio`
- `convert-to-ffv1`
- `prepare-youtube`

Below are some common usage patterns.

#### 📼 VHS effect (`apply-vhs-effect`)

Apply the VHS video + audio effect to a file:

```bash
apply-vhs-effect /path/to/video.mp4
apply-vhs-effect /path/to/video.mp4 -o /output/dir/
```

- The final `.mkv` file will be created in the same directory as the input video, or in the directory specified with `-o`.
- If you call `apply-vhs-effect` **without arguments**, it will prompt for the path on the terminal (you can drag & drop a file there).
- The input file must have an audio stream.

#### ✂️ Trim video (`trim-video`)

Non‑interactive (pure CLI):

```bash
trim-video -i input.mp4 --start 10 --end 25
# or using HH:MM:SS(.sss)
trim-video -i input.mp4 --start 00:00:10.0 --end 00:00:25.0 -o /output/dir/
```

Interactive mode using `rofi`:

```bash
trim-video -i input.mp4 --interactive
```

You will be asked (via `rofi`) for the start and end timestamps. The output file is saved in the same directory with a timestamp‑based name (`YYYYMMDD_HHMMSS.ext`), or in the path specified with `-o`.

#### 🔗 Concatenate videos (`concat-videos`)

```bash
concat-videos clip1.mkv clip2.mkv clip3.mkv
concat-videos clip1.mkv clip2.mkv -o /output/dir/
```

The script will:

- Validate that all files have compatible streams (same codec, resolution, fps, audio format). If not, it exits with a clear error before touching FFmpeg.
- Compute the total duration of all inputs.
- Create a temporary concat list for FFmpeg.
- Write the result as `joined_<timestamp>.<ext>` next to the first input file, or in the path specified with `-o`.

All concatenation is done with **stream copy** (no re‑encoding).

#### 🎬 Fade in/out (`fade-video`)

Apply both fade‑in and fade‑out of the same duration:

```bash
fade-video -i input_ffv1.mkv --fade 2.5
```

Separate fade‑in and fade‑out, custom fps and output path:

```bash
fade-video -i input_ffv1.mkv --fade-in 1.5 --fade-out 3 --fps 30 -o output_fade.mkv
```

The output is encoded as FFV1 (lossless), with `pcm_s16le` audio. Frame rate defaults to 60 fps and can be changed with `--fps`.

> The input must be a FFV1 `.mkv` file. Run `convert-to-ffv1` first if starting from a raw `.mp4`.

#### 🔊 Extract audio (`extract-audio`)

```bash
extract-audio input.mp4
extract-audio input.mp4 -o /output/dir/
```

This extracts the audio track, re‑encodes it to **PCM 16-bit** (`pcm_s16le`), and saves it as `input.wav`. The input must have an audio stream.

#### 🎞️ Convert to FFV1 (`convert-to-ffv1`)

```bash
convert-to-ffv1 input.mp4
convert-to-ffv1 input.mp4 --fps 30 -o /output/dir/
```

This creates `input_ffv1.mkv` using:

- FFV1 for video (lossless)
- `pcm_s16le` for audio
- 60 fps output by default (override with `--fps`)

Useful as an intermediate master before applying effects like `fade-video` or `apply-vhs-effect`.

#### 📺 Prepare for YouTube (`prepare-youtube`)

```bash
prepare-youtube master_ffv1.mkv
prepare-youtube master_ffv1.mkv -o /output/dir/
```

The input must be a FFV1 `.mkv` file. This produces `master_youtube.mov`:

- Upscaled (if needed) to 4K (2160p) height, preserving aspect ratio.
- Encoded as ProRes 422 HQ (`prores_ks`, profile 3).
- 10‑bit 4:2:2 (`yuv422p10le`) video.
- Uncompressed 16‑bit PCM audio.

Uploading this file to YouTube usually results in better quality after YouTube’s recompression.

---

### 🐍 Running directly from the source tree (without installation)

From the project root (where `pyvideokit/` lives), you can also run the tools as Python modules:

```bash
python3 -m pyvideokit.apply_vhs_effect /path/to/video.mp4
python3 -m pyvideokit.trim_video -i /path/to/video.mp4 --start 5 --end 10
python3 -m pyvideokit.concat_videos clip1.mp4 clip2.mp4
python3 -m pyvideokit.fade_video -i input.mp4 --fade 2
python3 -m pyvideokit.extract_audio input.mp4
python3 -m pyvideokit.convert_to_ffv1 input.mp4
python3 -m pyvideokit.prepare_youtube input.mp4
```

This is the recommended way if you just cloned the repo and don’t want to install anything globally.

---

## 📜 Script Descriptions

| Script | Description |
|--------|-------------|
| `apply_vhs_effect.py` | 📼 Applies a VHS visual style (color bleeding, noise, jitter) **and** VHS‑like audio (brown noise, low‑pass filter) to a video. |
| `trim_video.py` | ✂️ Trims a video file. Supports both pure CLI (`--start/--end`) and an interactive mode using `rofi` (`--interactive`). |
| `concat_videos.py` | 🔗 Concatenates (joins) multiple video files into a single file using FFmpeg’s concat demuxer (no re‑encoding). |
| `fade_video.py` | 🎬 Applies fade-in and fade-out effects to both video and audio tracks, encoding to FFV1 @ 60 fps. |
| `extract_audio.py` | 🔊 Extracts the audio track from a video file and saves it as a separate `.wav` file (stream copy). |
| `convert_to_ffv1.py` | 🎞️ Converts a video to the FFV1 lossless codec, useful for intermediate editing. |
| `prepare_youtube.py` | 📺 Encodes a video with settings optimized for YouTube upload (ProRes 422 HQ, 4K upscaling). |

---

## ⚙️ Common Options & Tips

- **Timestamps**: For tools that accept time values, you can usually use formats like `SS`, `MM:SS`, or `HH:MM:SS(.sss)`.
- **Drag & Drop**: When prompted for a file path in the terminal, you can often drag the file from your file manager into the terminal window.
- **Notifications**: If `dunstify` is available, long‑running FFmpeg jobs will show progress notifications on your desktop. Errors are also shown as notifications.
- **Output path (`-o`)**: All tools accept `-o <file>` or `-o <directory>` to control where the output is written.
- **Typical workflow**: `convert-to-ffv1` → `apply-vhs-effect` / `fade-video` → `prepare-youtube`. Tools that re-encode (fade, prepare-youtube) require a FFV1 `.mkv` as input.

---

## ⚖️ License

This project is licensed under the GPLv3 License – see the [LICENSE](LICENSE) file for details.
