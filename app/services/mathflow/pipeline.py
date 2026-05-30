import os

from loguru import logger

from app.models import const
from app.models.schema import VideoAspect
from app.services import video, voice
from app.services import state as sm
from app.services.mathflow import audioutil, render
from app.services.mathflow import srt as srt_mod
from app.services.mathflow import timing
from app.services.mathflow.beats import BEATS
from app.utils import utils

DEFAULT_VI_VOICE = "vi-VN-HoaiMyNeural-Female"
DEFAULT_VI_FONT = "DejaVuSans.ttf"


def _apply_defaults(params):
    if not params.voice_name:
        params.voice_name = DEFAULT_VI_VOICE
    # Vietnamese subtitles require a diacritics-capable font; force the bundled one.
    params.font_name = DEFAULT_VI_FONT
    # Manim always renders at 1080x1920; video.generate_video positions burned subtitles
    # using the aspect's resolution and does not resize, so force portrait to keep the
    # subtitles on-screen regardless of the WebUI ratio selector.
    params.video_aspect = VideoAspect.portrait.value


def start(task_id, params, stop_at: str = "video"):
    logger.info(f"start math_explainer task: {task_id}")
    if stop_at != "video":
        logger.warning(
            f"math_explainer: stop_at='{stop_at}' is not supported and will be ignored"
        )
    _apply_defaults(params)
    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=5)

    task_path = utils.task_dir(task_id)
    beat_videos = []
    beat_audios = []
    segments = []  # (text, duration)

    for i, beat in enumerate(BEATS):
        index = i + 1
        raw_audio = os.path.join(task_path, f"beat-{index}-raw.mp3")
        sub_maker = voice.tts(
            text=beat.narration_vi,
            voice_name=voice.parse_voice_name(params.voice_name),
            voice_rate=params.voice_rate,
            voice_file=raw_audio,
            voice_volume=params.voice_volume,
        )
        if sub_maker is None or not os.path.exists(raw_audio):
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error(f"math beat '{beat.key}' TTS failed")
            return

        audio_dur = voice.get_audio_duration(raw_audio)
        target = timing.beat_duration(audio_dur, beat.anim_min_secs)

        padded_audio = os.path.join(task_path, f"beat-{index}.mp3")
        try:
            beat_video = render.render_beat(beat, target_duration=target,
                                            out_dir=task_path, index=index)
            audioutil.pad_audio_to(raw_audio, target_secs=target, out_path=padded_audio)
        except Exception as exc:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error(f"math beat '{beat.key}' render/pad failed: {exc}")
            return

        beat_videos.append(beat_video)
        beat_audios.append(padded_audio)
        segments.append((beat.narration_vi, target))

        sm.state.update_task(task_id, progress=5 + int(70 * index / len(BEATS)))

    try:
        scenes_video = os.path.join(task_path, "scenes.mp4")
        video.concat_video_clips_with_ffmpeg(
            beat_videos, scenes_video, threads=params.n_threads, output_dir=task_path)

        full_audio = os.path.join(task_path, "audio.mp3")
        audioutil.concat_audio(beat_audios, full_audio, output_dir=task_path)

        subtitle_path = os.path.join(task_path, "subtitle.srt")
        srt_mod.write_srt(srt_mod.build_cues(segments), subtitle_path)

        sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=85)

        _encode_logged = {"pct": -10}

        def _encode_progress(pct):
            # The final encode is the longest silent step; map its 0-100 onto the
            # 85-99 band so the UI progress bar keeps moving instead of freezing at 85.
            sm.state.update_task(task_id, progress=85 + int(14 * pct / 100))
            # The WebUI advances its bar off log lines, and the encode emits none on its
            # own — so log a throttled line (~every 10%) to keep the bar moving here too.
            if pct >= _encode_logged["pct"] + 10 or pct >= 100:
                _encode_logged["pct"] = pct
                logger.info(f"encoding final video: {pct}%")

        final_video = os.path.join(task_path, "final-1.mp4")
        video.generate_video(
            video_path=scenes_video,
            audio_path=full_audio,
            subtitle_path=subtitle_path,
            output_file=final_video,
            params=params,
            progress_callback=_encode_progress,
        )
    except Exception as exc:
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
        logger.error(f"math_explainer assembly failed: {exc}")
        return

    kwargs = {
        "videos": [final_video],
        "combined_videos": [scenes_video],
        "audio_file": full_audio,
        "subtitle_path": subtitle_path,
    }
    sm.state.update_task(task_id, state=const.TASK_STATE_COMPLETE, progress=100, **kwargs)
    logger.success(f"math_explainer task {task_id} finished")
    return kwargs
