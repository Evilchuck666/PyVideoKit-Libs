#!/usr/bin/env python3

from collections.abc import Callable
from pathlib import Path
from . import ffmpeg_utils as utils


def _build_fade_cmd(
    input_path: Path,
    fade_in: float | None,
    fade_out: float | None,
    total_duration: float,
    output_path: Path,
) -> list[str]:
    v_filters = []
    if fade_in is not None:
        v_filters.append(f"fade=t=in:st=0:d={fade_in:.3f}")
    if fade_out is not None:
        start_out = max(0.0, total_duration - fade_out)
        v_filters.append(f"fade=t=out:st={start_out:.3f}:d={fade_out:.3f}")
    v_filters.append("format=yuv420p")

    a_filters = []
    if fade_in is not None:
        a_filters.append(f"afade=t=in:st=0:d={fade_in:.3f}")
    if fade_out is not None:
        a_start_out = max(0.0, total_duration - fade_out)
        a_filters.append(f"afade=t=out:st={a_start_out:.3f}:d={fade_out:.3f}")
    af_chain = ",".join(a_filters) if a_filters else None

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(input_path),
        "-c:v", "ffv1",
        "-pix_fmt", "yuv420p",
        "-vf", ",".join(v_filters),
    ]
    if af_chain:
        cmd += ["-c:a", "pcm_s16le", "-af", af_chain]
    else:
        cmd += ["-c:a", "pcm_s16le"]
    cmd.append(str(output_path))
    return cmd


def fade_video(
    input_path: Path,
    fade_in: float | None = None,
    fade_out: float | None = None,
    output: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    utils.require_video_codec(
        input_path, "ffv1",
        hint="Run convert_to_ffv1() on the source file first.",
    )
    utils.require_audio_stream(input_path)
    if fade_in is None and fade_out is None:
        raise ValueError("Specify at least one of fade_in or fade_out.")
    total_duration = utils.probe_duration(input_path)
    if total_duration <= 0:
        raise ValueError("Could not determine video duration.")
    output_path = utils.resolve_output_path(
        utils.make_output_path(input_path, suffix="_fade"), output
    )
    cmd = _build_fade_cmd(input_path, fade_in, fade_out, total_duration, output_path)
    utils.run_ffmpeg_with_progress(cmd, duration=total_duration, on_progress=on_progress)
    return output_path
