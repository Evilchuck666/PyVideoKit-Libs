#!/usr/bin/env python3

from collections.abc import Callable
from pathlib import Path
from . import ffmpeg_utils as utils


def prepare_youtube(
    input_path: Path,
    output: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    utils.require_video_codec(
        input_path, "ffv1",
        hint="Run convert_to_ffv1() on the source file first.",
    )
    duration = utils.probe_duration(input_path)
    output_path = utils.resolve_output_path(
        utils.make_output_path(input_path, suffix="_youtube", ext=".mov"), output
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(input_path),
        "-map", "0",
        "-vf", "scale=-1:2160",     # YouTube gives better bitrate to 4K uploads
        "-c:v", "prores_ks",
        "-profile:v", "3",          # ProRes 422 HQ
        "-pix_fmt", "yuv422p10le",
        "-c:a", "pcm_s16le",
        str(output_path),
    ]
    utils.run_ffmpeg_with_progress(cmd, duration=duration, on_progress=on_progress)
    return output_path
