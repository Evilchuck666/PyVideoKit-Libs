from .ffmpeg_utils import (
    FFmpegError,
    validate_input_file,
    require_tools,
    require_video_codec,
    require_audio_stream,
    probe_duration,
    probe_stream_props,
    probe_video_codec,
    probe_has_audio,
    parse_time_to_seconds,
    seconds_to_hms,
    make_output_path,
    resolve_output_path,
    which,
    run_command,
    run_ffmpeg_with_progress,
)
from .apply_vhs_effect import apply_vhs_effect, build_vhs_filter
from .concat_videos import join_videos, check_stream_compatibility
from .convert_to_ffv1 import convert_to_ffv1
from .extract_audio import extract_audio
from .fade_video import fade_video
from .prepare_youtube import prepare_youtube
from .trim_video import trim_video

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("PyVideoKit-Libs")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "FFmpegError",
    "validate_input_file",
    "require_tools",
    "require_video_codec",
    "require_audio_stream",
    "probe_duration",
    "probe_stream_props",
    "probe_video_codec",
    "probe_has_audio",
    "parse_time_to_seconds",
    "seconds_to_hms",
    "make_output_path",
    "resolve_output_path",
    "which",
    "run_command",
    "run_ffmpeg_with_progress",
    "apply_vhs_effect",
    "build_vhs_filter",
    "join_videos",
    "check_stream_compatibility",
    "convert_to_ffv1",
    "extract_audio",
    "fade_video",
    "prepare_youtube",
    "trim_video",
]
