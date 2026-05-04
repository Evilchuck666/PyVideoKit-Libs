#!/usr/bin/env python3

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from . import ffmpeg_utils as utils


def _build_output_path(input_path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return input_path.with_name(f"{ts}{input_path.suffix}")


def trim_video(
    input_path: Path,
    start: float,
    end: float,
    output: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    if end <= start:
        raise ValueError("end time must be greater than start time.")
    file_dur = utils.probe_duration(input_path)
    if file_dur > 0 and start > file_dur:
        raise ValueError(f"start ({start:.3f}s) exceeds input duration ({file_dur:.3f}s).")
    duration = end - start
    output_path = utils.resolve_output_path(_build_output_path(input_path), output)
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-ss", utils.seconds_to_hms(start),
        "-i", str(input_path),
        "-t", utils.seconds_to_hms(duration),
        "-c", "copy",
        str(output_path),
    ]
    utils.run_ffmpeg_with_progress(cmd, duration=duration, on_progress=on_progress)
    return output_path
