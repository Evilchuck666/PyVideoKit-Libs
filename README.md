# 🎥 PyVideoKit-Libs

![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)

Python library for FFmpeg-based video and audio processing. Provides the core functions behind [PyVideoKit-CLI](../PyVideoKit-CLI), and can be used directly in your own Python projects.

---

## ✨ Features

- 📼 **VHS effect** — retro visual noise, color bleed, and audio degradation
- ✂️ **Trim** — cut a segment by start/end time with stream copy (no re-encoding)
- 🔗 **Concatenate** — join multiple videos with stream compatibility validation
- 🎬 **Fade** — fade-in and/or fade-out on an FFV1 master
- 🔊 **Extract audio** — dump the audio track to uncompressed WAV (PCM 16-bit)
- 🎞️ **Convert to FFV1** — create a lossless MKV master for editing
- 📺 **Prepare for YouTube** — encode to ProRes 422 HQ MOV, upscaled to 4K

---

## 📦 Requirements

- **Python** ≥ 3.10
- **FFmpeg** and **FFprobe** available in `PATH`
- **SoX** available in `PATH` (required by `apply_vhs_effect`)

No Python package dependencies — the library delegates all heavy lifting to external tools via subprocess.

---

## 🔧 Installation

### 🏗️ Arch Linux (AUR)

```bash
yay -S python-pyvideokit-libs
```

FFmpeg, FFprobe, and SoX are installed automatically as pacman dependencies.

### 🐍 Other systems (pip)

```bash
pip install PyVideoKit-Libs
```

Make sure **FFmpeg**, **FFprobe**, and **SoX** are available in your `PATH`.

---

## 🚀 Quick Start

```python
from pathlib import Path
from pyvideokit_libs import convert_to_ffv1, fade_video, prepare_youtube

# 1. Create a lossless master
master = convert_to_ffv1(Path("recording.mp4"))

# 2. Add a 1-second fade in and out
faded = fade_video(master, fade_in=1.0, fade_out=1.0)

# 3. Export for YouTube
result = prepare_youtube(faded)
print(result)
```

All functions accept an optional `on_progress` callback `(pct: float) -> None` for tracking progress.

---

## 📖 API Reference

### 🎞️ Video processing functions

#### `apply_vhs_effect(input_path, output=None, on_progress=None) -> Path`

Apply a retro VHS visual and audio effect. The input must have an audio stream. Produces a `.mkv` file.

```python
out = apply_vhs_effect(Path("video.mp4"))
```

---

#### `trim_video(input_path, start, end, output=None, on_progress=None) -> Path`

Cut a segment from a video using stream copy (no re-encoding). `start` and `end` are in seconds.

```python
out = trim_video(Path("video.mkv"), start=10.0, end=90.5)
```

Use `parse_time_to_seconds("00:01:30")` to convert a timestamp string to seconds.

---

#### `join_videos(video_paths, output=None, on_progress=None) -> Path`

Concatenate two or more videos using stream copy. Validates stream compatibility (codec, resolution, fps, audio format) before proceeding.

```python
out = join_videos([Path("clip1.mkv"), Path("clip2.mkv"), Path("clip3.mkv")])
```

---

#### `fade_video(input_path, fade_in=None, fade_out=None, fps=60, output=None, on_progress=None) -> Path`

Add fade-in and/or fade-out to an FFV1 video. Output is re-encoded as FFV1 with PCM audio.

```python
out = fade_video(Path("master.mkv"), fade_in=1.5, fade_out=2.0)
```

---

#### `extract_audio(input_path, output=None, on_progress=None) -> Path`

Extract the audio track to an uncompressed WAV file (PCM 16-bit, `pcm_s16le`).

```python
out = extract_audio(Path("video.mkv"))
```

---

#### `convert_to_ffv1(input_path, fps=60, output=None, on_progress=None) -> Path`

Convert any video to a lossless FFV1/MKV master. Use this as the first step before applying effects.

```python
master = convert_to_ffv1(Path("recording.mp4"), fps=60)
```

---

#### `prepare_youtube(input_path, output=None, on_progress=None) -> Path`

Encode an FFV1 master to ProRes 422 HQ MOV for YouTube upload:

- Upscaled to 4K (2160p height), aspect ratio preserved
- ProRes 422 HQ (`prores_ks`, profile 3), 10-bit 4:2:2 (`yuv422p10le`)
- Uncompressed 16-bit PCM audio

```python
out = prepare_youtube(Path("master_ffv1.mkv"))
```

---

### ⚙️ Utility functions

| Function | Description |
|---|---|
| `parse_time_to_seconds(ts)` | Parse `SS`, `MM:SS`, or `HH:MM:SS` to a float |
| `seconds_to_hms(seconds)` | Convert seconds to `HH:MM:SS.mmm` string |
| `probe_duration(path)` | Get media duration in seconds via FFprobe |
| `probe_stream_props(path)` | Get codec, dimensions, fps, sample rate, channels |
| `probe_video_codec(path)` | Get the video codec name |
| `probe_has_audio(path)` | Check whether an audio stream is present |
| `make_output_path(input_path, suffix, ext)` | Generate an output filename next to the input |
| `resolve_output_path(default, output)` | Resolve a file or directory output argument |
| `require_tools(*names)` | Raise if any external tool is not in `PATH` |
| `require_video_codec(path, codec, hint)` | Raise if the video codec does not match |
| `require_audio_stream(path)` | Raise if no audio stream is present |
| `run_ffmpeg_with_progress(cmd, duration, on_progress)` | Run an FFmpeg command with progress tracking |

---

### 🛡️ Error handling

All functions raise `FFmpegError` when an FFmpeg subprocess exits with a non-zero code.

```python
from pyvideokit_libs import FFmpegError, convert_to_ffv1

try:
    out = convert_to_ffv1(Path("bad_file.mp4"))
except FFmpegError as e:
    print(f"FFmpeg failed (exit {e.returncode}):")
    for line in e.error_lines:
        print(line)
```

---

## 🔄 Typical Workflow

```
convert_to_ffv1  →  trim_video / fade_video / apply_vhs_effect  →  prepare_youtube
```

> Functions that re-encode (`fade_video`, `apply_vhs_effect`, `prepare_youtube`) expect an FFV1 `.mkv` as input.

---

## ⚖️ License

This project is licensed under the GPLv3 License — see the [LICENSE](LICENSE) file for details.
