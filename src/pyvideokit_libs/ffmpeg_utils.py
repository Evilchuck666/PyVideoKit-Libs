#!/usr/bin/env python3

import json
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path


class FFmpegError(Exception):
    def __init__(self, returncode: int, error_lines: list[str]) -> None:
        self.returncode = returncode
        self.error_lines = error_lines
        super().__init__(f"FFmpeg exited with code {returncode}")


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def has_ffprobe() -> bool:
    return which("ffprobe") is not None


def parse_time_to_seconds(ts: str) -> float | None:
    """Parse SS, MM:SS, or HH:MM:SS(.ms) into total seconds; returns None for empty input."""
    ts = (ts or "").strip()
    if ts == "":
        return None
    if ts.count(":") == 0:
        return float(ts)
    parts = [float(p) for p in ts.split(":")]
    if len(parts) == 2:
        mm, ss = parts
        return mm * 60 + ss
    if len(parts) == 3:
        hh, mm, ss = parts
        return hh * 3600 + mm * 60 + ss
    raise ValueError(f"Invalid time format: {ts}")


def seconds_to_hms(seconds: float) -> str:
    """Convert seconds to HH:MM:SS.mmm string."""
    seconds = max(0.0, float(seconds))
    hh = int(seconds // 3600)
    mm = int((seconds % 3600) // 60)
    ss = seconds - (hh * 3600 + mm * 60)
    return f"{hh:02d}:{mm:02d}:{ss:06.3f}"


def probe_video_codec(path: Path) -> str:
    """Return the codec name of the first video stream, or '' if none."""
    if not has_ffprobe():
        return ""
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=codec_name",
             "-of", "default=nk=1:nw=1", str(path)],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return out
    except Exception:
        return ""


def probe_has_audio(path: Path) -> bool:
    """Return True if the file has at least one audio stream."""
    if not has_ffprobe():
        return False
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=codec_name",
             "-of", "default=nk=1:nw=1", str(path)],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return bool(out)
    except Exception:
        return False


def probe_stream_props(path: Path) -> dict:
    """Return stream properties and duration in a single ffprobe call."""
    if not has_ffprobe():
        return {}
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error",
             "-show_entries",
             "format=duration:stream=codec_name,width,height,r_frame_rate,sample_rate,channels",
             "-of", "json", str(path)],
            stderr=subprocess.DEVNULL,
        ).decode()
        data = json.loads(out)
        props: dict = {}
        for stream in data.get("streams", []):
            if "width" in stream:
                props["vcodec"] = stream.get("codec_name", "")
                props["width"]  = stream.get("width")
                props["height"] = stream.get("height")
                props["fps"]    = stream.get("r_frame_rate", "")
            elif "sample_rate" in stream:
                props["acodec"]      = stream.get("codec_name", "")
                props["sample_rate"] = stream.get("sample_rate")
                props["channels"]    = stream.get("channels")
        duration_str = data.get("format", {}).get("duration")
        if duration_str:
            props["duration"] = float(duration_str)
        return props
    except Exception:
        return {}


def probe_duration(path: Path) -> float:
    """Return the duration of a media file in seconds, or 0.0 on failure."""
    if not has_ffprobe():
        return 0.0
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nk=1:nw=1", str(path)],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return float(out)
    except Exception:
        return 0.0


def validate_input_file(path: str | Path) -> Path:
    """Resolve and validate that an input file exists; raise FileNotFoundError if not."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    return p


def require_tools(*names: str) -> None:
    """Check that all required external tools are in PATH; raise RuntimeError if any are missing."""
    missing = [n for n in names if which(n) is None]
    if missing:
        raise RuntimeError(f"Required tools not found in PATH: {', '.join(missing)}")


def require_video_codec(path: Path, codec: str, hint: str = "") -> None:
    """Raise ValueError if the file's video codec doesn't match the expected one."""
    actual = probe_video_codec(path)
    if actual != codec:
        msg = f"'{path.name}' has codec '{actual or 'none'}', expected '{codec}'."
        if hint:
            msg += f" {hint}"
        raise ValueError(msg)


def require_audio_stream(path: Path) -> None:
    """Raise ValueError if the file has no audio stream."""
    if not probe_has_audio(path):
        raise ValueError(f"'{path.name}' has no audio stream.")


def resolve_output_path(default: Path, output: str | None) -> Path:
    """Return default if output is None, place inside dir if dir, else treat as explicit path."""
    if output is None:
        return default
    out = Path(output).expanduser()
    if out.is_dir():
        return out / default.name
    return out


def make_output_path(input_path: Path, suffix: str = "", ext: str | None = None) -> Path:
    """Build an output path in the same directory as input with optional suffix/extension."""
    name = input_path.stem + suffix
    extension = ext if ext is not None else input_path.suffix
    return input_path.with_name(name + extension)


def run_command(cmd: list[str]) -> None:
    """Run a subprocess command; raises CalledProcessError on failure."""
    subprocess.run(cmd, check=True)


def run_ffmpeg_with_progress(
    cmd: list[str],
    duration: float = 0.0,
    on_progress: Callable[[float], None] | None = None,
) -> None:
    """Run an FFmpeg command, calling on_progress(pct) as it encodes. Raises FFmpegError on failure."""
    if "-progress" not in cmd:
        full_cmd = cmd[:1] + ["-progress", "pipe:1", "-nostats", "-loglevel", "error"] + cmd[1:]
    else:
        full_cmd = cmd

    try:
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        )
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found in PATH")

    last_pct = -1.0
    error_lines: list[str] = []

    for line in proc.stdout or []:
        line = line.strip()
        if not line:
            continue
        if line.startswith("out_time_ms="):
            try:
                ms = int(line.split("=", 1)[1])
                out_time_sec = ms / 1_000_000.0
                if duration > 0:
                    pct = min(100.0, (out_time_sec / duration) * 100.0)
                else:
                    pct = min(100.0, (out_time_sec % 10) * 10.0)
                if on_progress and (pct - last_pct >= 1.0 or pct >= 100.0):
                    last_pct = pct
                    on_progress(pct)
            except ValueError:
                pass
        elif line.startswith("progress=end"):
            break
        elif " " in line or line.startswith("["):
            # FFmpeg error/warning messages contain spaces or start with [codec @ addr]
            error_lines.append(line)

    rc = proc.wait()
    if rc != 0:
        raise FFmpegError(rc, error_lines)
