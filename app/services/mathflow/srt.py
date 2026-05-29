from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SubtitleCue:
    index: int
    start: float  # seconds
    end: float    # seconds
    text: str


def format_timestamp(seconds: float) -> str:
    """Format seconds as an SRT timestamp: HH:MM:SS,mmm."""
    if seconds < 0:
        seconds = 0
    total_ms = int(round(seconds * 1000))
    hours, total_ms = divmod(total_ms, 3_600_000)
    minutes, total_ms = divmod(total_ms, 60_000)
    secs, millis = divmod(total_ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_cues(segments: List[Tuple[str, float]]) -> List[SubtitleCue]:
    """Turn (text, duration) segments into cumulative-timeline SRT cues."""
    cues: List[SubtitleCue] = []
    t = 0.0
    for i, (text, duration) in enumerate(segments, start=1):
        cues.append(SubtitleCue(index=i, start=t, end=t + duration, text=text.strip()))
        t += duration
    return cues


def write_srt(cues: List[SubtitleCue], out_path: str) -> str:
    lines: List[str] = []
    for cue in cues:
        lines.append(str(cue.index))
        lines.append(f"{format_timestamp(cue.start)} --> {format_timestamp(cue.end)}")
        lines.append(cue.text)
        lines.append("")
    with open(out_path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))
    return out_path
