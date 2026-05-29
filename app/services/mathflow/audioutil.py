import os
import subprocess
from typing import List

from loguru import logger

from app.services import video


def pad_audio_to(in_path: str, target_secs: float, out_path: str) -> str:
    """Pad an audio file with trailing silence and trim to exactly target_secs."""
    command = [
        video.get_ffmpeg_binary(), "-y",
        "-i", in_path,
        "-af", "apad",
        "-t", str(float(target_secs)),
        "-c:a", "libmp3lame",
        out_path,
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "").strip()
                           or "ffmpeg pad failed")
    return out_path


def concat_audio(clip_files: List[str], output_file: str, output_dir: str) -> str:
    """Concatenate mp3 clips into one file (re-encoded for safe joining)."""
    concat_list_file = os.path.join(output_dir, "ffmpeg-audio-concat-list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as fp:
        for clip in clip_files:
            absolute = os.path.abspath(clip).replace("'", "'\\''")
            fp.write(f"file '{absolute}'\n")
    command = [
        video.get_ffmpeg_binary(), "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-c:a", "libmp3lame",
        output_file,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "").strip()
                               or "ffmpeg audio concat failed")
    finally:
        if os.path.exists(concat_list_file):
            os.remove(concat_list_file)
    return output_file
