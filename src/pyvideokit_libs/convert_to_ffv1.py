#!/usr/bin/env python3

from collections.abc import Callable
from pathlib import Path
from . import ffmpeg_utils as utils


def convert_to_ffv1(
    input_path: Path,
    fps: int | None = None,
    output: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    duration = utils.probe_duration(input_path)
    output_path = utils.resolve_output_path(
        utils.make_output_path(input_path, suffix="_ffv1", ext=".mkv"), output
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(input_path),
        "-map", "0",
        "-c:v", "ffv1",
    ]
    if fps is not None:
        cmd += ["-r", str(fps)]
    cmd += [
        "-c:a", "pcm_s16le",
        str(output_path),
    ]
    utils.run_ffmpeg_with_progress(cmd, duration=duration, on_progress=on_progress)
    return output_path
