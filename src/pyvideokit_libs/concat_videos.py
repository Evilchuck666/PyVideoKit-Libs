#!/usr/bin/env python3

import tempfile
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from . import ffmpeg_utils as utils


def _build_concat_file(video_paths: list[Path]) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    with tmp as f:
        for p in video_paths:
            # Escape single quotes for ffmpeg concat file format
            path_str = str(p.resolve()).replace("'", r"'\''")
            f.write(f"file '{path_str}'\n")
    return Path(tmp.name)


def _build_output_path(first_video: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ext = first_video.suffix or ".mkv"
    return first_video.with_name(f"joined_{timestamp}{ext}")


def check_stream_compatibility(video_paths: list[Path], all_props: list[dict]) -> None:
    """Raise ValueError if files have incompatible streams for stream-copy concat."""
    ref = all_props[0]
    if not ref:
        return
    keys = ("vcodec", "width", "height", "fps", "acodec", "sample_rate", "channels")
    for path, props in zip(video_paths[1:], all_props[1:]):
        mismatches = [
            f"  {k}: {video_paths[0].name}={ref[k]!r} vs {path.name}={props.get(k)!r}"
            for k in keys
            if k in ref and props.get(k) != ref[k]
        ]
        if mismatches:
            raise ValueError(
                "Incompatible streams for lossless concat:\n" + "\n".join(mismatches)
            )


def join_videos(
    video_paths: list[Path],
    output: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    if len(video_paths) < 2:
        raise ValueError("Need at least two input videos.")
    all_props = [utils.probe_stream_props(p) for p in video_paths]
    check_stream_compatibility(video_paths, all_props)
    total = sum(p.get("duration", 0.0) for p in all_props)
    concat_file = _build_concat_file(video_paths)
    output_path = utils.resolve_output_path(_build_output_path(video_paths[0]), output)
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy", str(output_path),
    ]
    try:
        utils.run_ffmpeg_with_progress(cmd, duration=total, on_progress=on_progress)
    finally:
        concat_file.unlink(missing_ok=True)
    return output_path
