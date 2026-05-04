#!/usr/bin/env python3

from collections.abc import Callable
from pathlib import Path
from . import ffmpeg_utils as utils


def extract_audio(
    input_path: Path,
    output: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    duration = utils.probe_duration(input_path)
    output_path = utils.resolve_output_path(
        utils.make_output_path(input_path, ext=".wav"), output
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(input_path),
        "-vn",
        "-c:a", "pcm_s16le",
        str(output_path),
    ]
    utils.run_ffmpeg_with_progress(cmd, duration=duration, on_progress=on_progress)
    return output_path
