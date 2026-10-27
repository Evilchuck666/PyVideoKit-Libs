#!/usr/bin/env python3
"""End-to-end smoke test: runs every public function on a short generated clip.

Needs FFmpeg, FFprobe and SoX in PATH. Run it against an installed package
(not the src tree) so it checks what actually ships in the wheel.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pyvideokit_libs as pvk


def make_clip(path: Path, seconds: int = 3) -> None:
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", f"testsrc2=size=320x240:rate=25:duration={seconds}",
         "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={seconds}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
         str(path)],
        check=True,
    )


def check(label: str, path: Path, codec: str | None = None) -> Path:
    if not path.is_file() or path.stat().st_size == 0:
        sys.exit(f"FAIL {label}: {path} is missing or empty")
    if codec and pvk.probe_video_codec(path) != codec:
        sys.exit(f"FAIL {label}: expected {codec}, got {pvk.probe_video_codec(path)!r}")
    print(f"ok   {label}: {path.name}")
    return path


def main() -> None:
    print(f"PyVideoKit-Libs {pvk.__version__}")
    pvk.require_tools("ffmpeg", "ffprobe", "sox")
    assert pvk.parse_time_to_seconds("01:02:03.5") == 3723.5
    assert pvk.seconds_to_hms(3723.5) == "01:02:03.500"

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "source.mp4"
        make_clip(src)

        master = check("convert_to_ffv1", pvk.convert_to_ffv1(src), "ffv1")
        check("trim_video", pvk.trim_video(master, 0.5, 2.0, output=str(Path(tmp) / "trim.mkv")))
        check("join_videos", pvk.join_videos([master, master]))
        check("fade_video", pvk.fade_video(master, fade_in=0.5, fade_out=0.5), "ffv1")
        check("extract_audio", pvk.extract_audio(master))
        # Explicit output: the default name equals an .mkv input and would overwrite it.
        check("apply_vhs_effect", pvk.apply_vhs_effect(master, output=str(Path(tmp) / "vhs.mkv")), "ffv1")
        check("prepare_youtube", pvk.prepare_youtube(master), "prores")

    print("All smoke tests passed.")


if __name__ == "__main__":
    main()
