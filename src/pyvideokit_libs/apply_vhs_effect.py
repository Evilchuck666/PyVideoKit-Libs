#!/usr/bin/env python3

import math
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from . import ffmpeg_utils as utils


SAMPLE_RATE   = 48000
BIT_DEPTH     = 32
CHANNELS      = 2
LOW_PASS_FREQ = 4000
IN_VOL        = 1.0
OUT_VOL       = 0.077
DB_VOLUME     = math.pow(10, -22.75 / 20.0)

V_CODEC        = "ffv1"
A_CODEC        = "pcm_s16le"
PIX_FMT        = "yuv420p"
VID_COLORSPACE = "bt709"


def build_vhs_filter(width: int, height: int) -> str:
    """Build a resolution-independent VHS filtergraph preserving the original aspect ratio."""
    chroma_w  = width // 2
    chroma_h  = height // 2
    luma_sq   = max(2, round(width * 0.4) // 2 * 2)
    chroma_sq = max(2, round(chroma_w * 0.125) // 2 * 2)
    return (
        f"format=yuv420p, split=3 [a][b][c]; "
        f"[a] extractplanes=y [y]; "
        f"[b] extractplanes=u [u]; "
        f"[c] extractplanes=v [v]; "
        f"[y] scale={luma_sq}:{height}, scale={width}:{height} [luma_scaled]; "
        f"[u] scale={chroma_sq}:{chroma_h}, scale={chroma_w}:{chroma_h} [u_scaled]; "
        f"[v] scale={chroma_sq}:{chroma_h}, scale={chroma_w}:{chroma_h} [v_scaled]; "
        f"[luma_scaled][u_scaled][v_scaled] mergeplanes=0x001020:yuv420p [merged]; "
        f"[merged] eq=saturation=0.75, noise=alls=5:allf=t, "
        f"geq='lum(X+5.5*(random(floor(Y/96))-0.5),Y)':cb='cb(X,Y)':cr='cr(X,Y)' [outv]"
    )


@dataclass
class TempFiles:
    vhs:    Path
    wav:    Path
    wav_fx: Path
    noise:  Path
    mix:    Path

    @classmethod
    def from_dir(cls, d: Path) -> "TempFiles":
        def mktmp(suffix: str) -> Path:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=d) as f:
                return Path(f.name)
        return cls(
            vhs=mktmp(".mkv"),
            wav=mktmp(".wav"),
            wav_fx=mktmp(".wav"),
            noise=mktmp(".wav"),
            mix=mktmp(".wav"),
        )

    def cleanup(self) -> None:
        for f in (self.noise, self.mix, self.vhs, self.wav_fx, self.wav):
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass


def _step_0_vhs_fx(
    input_path: Path,
    tmp: TempFiles,
    props: dict,
    on_progress: Callable[[float], None] | None = None,
) -> None:
    vhs_filter = build_vhs_filter(props["width"], props["height"])
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(input_path),
        "-filter_complex", vhs_filter,
        "-c:v", V_CODEC, "-pix_fmt", PIX_FMT,
        "-colorspace", VID_COLORSPACE,
        "-color_primaries", VID_COLORSPACE,
        "-color_trc", VID_COLORSPACE,
        "-map", "[outv]", str(tmp.vhs),
        "-map", "a", "-c:a", A_CODEC, str(tmp.wav),
    ]
    utils.run_ffmpeg_with_progress(cmd, duration=props.get("duration", 0.0), on_progress=on_progress)


def _step_1_audio_fx(tmp: TempFiles, duration: float) -> None:
    utils.run_command([
        "sox", "-n",
        "-r", str(SAMPLE_RATE), "-b", str(BIT_DEPTH),
        "-e", "floating-point", "-c", str(CHANNELS),
        str(tmp.noise), "synth", str(duration), "brownnoise", "vol", f"{DB_VOLUME}",
    ])
    utils.run_command([
        "sox", "-m",
        "-v", f"{IN_VOL}", str(tmp.wav),
        "-v", f"{OUT_VOL}", str(tmp.noise),
        str(tmp.mix),
    ])
    utils.run_command([
        "sox", str(tmp.mix), str(tmp.wav_fx), "lowpass", str(LOW_PASS_FREQ),
    ])


def _step_2_map_inputs(input_path: Path, tmp: TempFiles, duration: float, output: str | None = None) -> Path:
    base_name = input_path.stem
    for ch in ':*?"<>|':
        base_name = base_name.replace(ch, "-")
    default_path = tmp.vhs.parent / f"{base_name}.mkv"
    final_path = utils.resolve_output_path(default_path, output)
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(tmp.vhs),
        "-i", str(tmp.wav_fx),
        "-map", "0:v", "-map", "1:a",
        "-c", "copy",
        str(final_path),
    ]
    utils.run_ffmpeg_with_progress(cmd, duration=duration)
    return final_path


def apply_vhs_effect(
    input_path: Path,
    output: str | None = None,
    on_progress: Callable[[float], None] | None = None,
) -> Path:
    utils.require_audio_stream(input_path)
    props = utils.probe_stream_props(input_path)
    tmp = TempFiles.from_dir(input_path.parent)
    try:
        _step_0_vhs_fx(input_path, tmp, props, on_progress)
        _step_1_audio_fx(tmp, props.get("duration", 0.0))
        return _step_2_map_inputs(input_path, tmp, props.get("duration", 0.0), output)
    finally:
        tmp.cleanup()
