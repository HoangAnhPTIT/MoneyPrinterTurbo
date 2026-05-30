import os
import shutil

from loguru import logger


def _import_manim_tempconfig():
    try:
        from manim import tempconfig
        return tempconfig
    except ImportError as exc:  # pragma: no cover - exercised only without manim
        raise RuntimeError(
            "manim is not installed. Install it with: pip install 'manim>=0.18.1,<0.19'"
        ) from exc


def _resolve_ffmpeg() -> str:
    """Resolve an ffmpeg binary for Manim, mirroring video.get_ffmpeg_binary().

    Manim shells out to `config.ffmpeg_executable` (default "ffmpeg" on PATH). This repo
    does not require a system ffmpeg — moviepy ships one via imageio-ffmpeg — so point
    Manim at the same binary instead of depending on PATH.
    """
    exe = os.environ.get("IMAGEIO_FFMPEG_EXE") or shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # pragma: no cover - last-resort fallback
        return "ffmpeg"


def _tempconfig_for(out_dir: str, index: int):
    """Return a Manim tempconfig context manager for a 9:16 1080x1920 render.

    Must match VideoAspect.portrait.to_resolution() (1080x1920) — video.generate_video
    positions burned subtitles relative to that resolution and does not resize the input.
    """
    tempconfig = _import_manim_tempconfig()
    settings = {
        "pixel_width": 1080,
        "pixel_height": 1920,
        "frame_rate": 30,
        "background_color": "#000000",
        "media_dir": os.path.join(out_dir, "manim_media"),
        "output_file": f"beat-{index}",
        "disable_caching": True,
        "verbosity": "ERROR",
        "ffmpeg_executable": _resolve_ffmpeg(),
    }
    return tempconfig(settings)


def render_beat(beat, target_duration: float, out_dir: str, index: int) -> str:
    """Render one beat's scene to a silent mp4 in out_dir; return its path."""
    logger.info(f"rendering math beat #{index} ({getattr(beat, 'key', '?')}), "
                f"target_duration={target_duration:.2f}s")
    dest = os.path.join(out_dir, f"beat-{index}.mp4")
    with _tempconfig_for(out_dir, index):
        scene = beat.scene_cls(target_duration=target_duration)
        scene.render()
        src = scene.renderer.file_writer.movie_file_path
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy(src, dest)
    return dest
