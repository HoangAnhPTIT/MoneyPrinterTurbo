def beat_duration(audio_dur: float, anim_min: float) -> float:
    """A beat lasts as long as the longer of its narration or its animation."""
    return max(float(audio_dur), float(anim_min))


def silence_padding(audio_dur: float, target: float) -> float:
    """Seconds of trailing silence needed to stretch narration to the beat length."""
    return max(0.0, float(target) - float(audio_dur))
