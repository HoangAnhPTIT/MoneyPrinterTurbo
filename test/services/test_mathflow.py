import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.schema import VideoParams
from app.services.mathflow import srt, timing


class TestFlowType(unittest.TestCase):
    def test_flow_type_defaults_to_standard(self):
        params = VideoParams(video_subject="x")
        self.assertEqual(params.flow_type, "standard")

    def test_flow_type_accepts_math_explainer(self):
        params = VideoParams(video_subject="x", flow_type="math_explainer")
        self.assertEqual(params.flow_type, "math_explainer")


class TestSrt(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(srt.format_timestamp(0), "00:00:00,000")
        self.assertEqual(srt.format_timestamp(3.5), "00:00:03,500")
        self.assertEqual(srt.format_timestamp(61.25), "00:01:01,250")
        self.assertEqual(srt.format_timestamp(-1), "00:00:00,000")

    def test_build_cues_cumulative_timeline(self):
        cues = srt.build_cues([("a", 2.0), ("b", 3.0)])
        self.assertEqual(len(cues), 2)
        self.assertEqual((cues[0].index, cues[0].start, cues[0].end, cues[0].text),
                         (1, 0.0, 2.0, "a"))
        self.assertEqual((cues[1].index, cues[1].start, cues[1].end, cues[1].text),
                         (2, 2.0, 5.0, "b"))

    def test_write_srt(self):
        import tempfile, os
        cues = srt.build_cues([("hello", 1.0)])
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "x.srt")
            srt.write_srt(cues, out)
            with open(out, encoding="utf-8") as fh:
                content = fh.read()
        self.assertIn("1\n00:00:00,000 --> 00:00:01,000\nhello", content)


class TestTiming(unittest.TestCase):
    def test_beat_duration_takes_the_longer(self):
        self.assertEqual(timing.beat_duration(audio_dur=4.0, anim_min=10.0), 10.0)
        self.assertEqual(timing.beat_duration(audio_dur=12.0, anim_min=10.0), 12.0)

    def test_silence_padding_is_nonnegative(self):
        self.assertEqual(timing.silence_padding(audio_dur=4.0, target=10.0), 6.0)
        self.assertEqual(timing.silence_padding(audio_dur=12.0, target=10.0), 0.0)


import os
import tempfile
from unittest import mock
from app.services.mathflow import render as render_mod


class TestRender(unittest.TestCase):
    def test_render_beat_invokes_scene_with_target_duration(self):
        captured = {}

        class FakeScene:
            def __init__(self, target_duration):
                captured["target_duration"] = target_duration

            def render(self):
                # emulate manim writing a file under media dir
                path = captured["expected_src"]
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(b"x")

            @property
            def renderer(self):
                m = mock.Mock()
                m.file_writer.movie_file_path = captured["expected_src"]
                return m

        class FakeBeat:
            scene_cls = FakeScene
            key = "demo"

        with tempfile.TemporaryDirectory() as d:
            captured["expected_src"] = os.path.join(d, "media", "demo.mp4")
            with mock.patch.object(render_mod, "_tempconfig_for", return_value=_nullctx()):
                out = render_mod.render_beat(FakeBeat(), target_duration=7.5,
                                             out_dir=d, index=2)
            self.assertEqual(captured["target_duration"], 7.5)
            self.assertTrue(out.endswith("beat-2.mp4"))
            self.assertTrue(os.path.exists(out))


import contextlib
@contextlib.contextmanager
def _nullctx():
    yield


from app.services.mathflow import beats as beats_mod


class TestBeats(unittest.TestCase):
    def test_registry_has_seven_unique_well_formed_beats(self):
        beats = beats_mod.BEATS
        self.assertEqual(len(beats), 7)
        keys = [b.key for b in beats]
        self.assertEqual(len(keys), len(set(keys)), "beat keys must be unique")
        for b in beats:
            self.assertTrue(b.narration_vi.strip(), f"{b.key} has empty narration")
            self.assertGreater(b.anim_min_secs, 0, f"{b.key} anim_min must be > 0")
            self.assertTrue(callable(b.scene_cls), f"{b.key} scene_cls not callable")


from app.services.mathflow import audioutil


class TestAudioUtil(unittest.TestCase):
    def test_pad_audio_to_builds_apad_command(self):
        with mock.patch("app.services.mathflow.audioutil.subprocess.run") as run, \
             mock.patch("app.services.mathflow.audioutil.video.get_ffmpeg_binary",
                        return_value="ffmpeg"):
            run.return_value = mock.Mock(returncode=0, stderr="", stdout="")
            out = audioutil.pad_audio_to("in.mp3", target_secs=9.0, out_path="out.mp3")
        self.assertEqual(out, "out.mp3")
        cmd = run.call_args[0][0]
        self.assertIn("apad", " ".join(cmd))
        self.assertIn("9.0", " ".join(cmd))

    def test_concat_audio_writes_list_and_runs_ffmpeg(self):
        with tempfile.TemporaryDirectory() as d, \
             mock.patch("app.services.mathflow.audioutil.subprocess.run") as run, \
             mock.patch("app.services.mathflow.audioutil.video.get_ffmpeg_binary",
                        return_value="ffmpeg"):
            run.return_value = mock.Mock(returncode=0, stderr="", stdout="")
            out = audioutil.concat_audio(["a.mp3", "b.mp3"],
                                         os.path.join(d, "all.mp3"), output_dir=d)
        self.assertTrue(out.endswith("all.mp3"))
        self.assertTrue(run.called)


from app.models.schema import VideoParams
from app.services.mathflow import pipeline as pipeline_mod
from app.services import task as task_mod


class TestPipeline(unittest.TestCase):
    def test_start_orchestrates_beats_and_returns_video(self):
        params = VideoParams(video_subject="x", flow_type="math_explainer")

        with mock.patch.object(pipeline_mod, "utils") as utils_mock, \
             mock.patch.object(pipeline_mod, "voice") as voice_mock, \
             mock.patch.object(pipeline_mod, "render") as render_mock, \
             mock.patch.object(pipeline_mod, "audioutil") as audio_mock, \
             mock.patch.object(pipeline_mod, "video") as video_mock, \
             mock.patch.object(pipeline_mod, "sm") as sm_mock:
            with tempfile.TemporaryDirectory() as d:
                utils_mock.task_dir.return_value = d
                voice_mock.tts.return_value = object()  # non-None sub_maker
                voice_mock.get_audio_duration.return_value = 8.0

                def fake_render(beat, target_duration, out_dir, index):
                    p = os.path.join(out_dir, f"beat-{index}.mp4")
                    with open(p, "wb") as fh:
                        fh.write(b"x")
                    return p
                render_mock.render_beat.side_effect = fake_render

                def fake_pad(in_path, target_secs, out_path):
                    with open(out_path, "wb") as fh:
                        fh.write(b"a")
                    return out_path
                audio_mock.pad_audio_to.side_effect = fake_pad
                audio_mock.concat_audio.side_effect = lambda files, out, output_dir: out

                # voice.tts writes the audio file the pipeline checks for
                def write_audio(text, voice_name, voice_rate, voice_file, voice_volume):
                    with open(voice_file, "wb") as fh:
                        fh.write(b"a")
                    return object()
                voice_mock.tts.side_effect = write_audio

                result = pipeline_mod.start("task-1", params)

        self.assertIn("videos", result)
        self.assertEqual(len(result["videos"]), 1)
        self.assertEqual(render_mock.render_beat.call_count, 7)
        video_mock.generate_video.assert_called_once()
        # narration defaulted to a Vietnamese voice
        self.assertTrue(params.voice_name.startswith("vi-VN"))
        # font forced to the bundled Vietnamese font
        self.assertEqual(params.font_name, "DejaVuSans.ttf")
        # math flow forces portrait aspect so burned subtitles stay on-screen
        self.assertEqual(params.video_aspect, "9:16")


    def test_assembly_failure_marks_task_failed(self):
        from app.models import const as const_mod
        params = VideoParams(video_subject="x", flow_type="math_explainer")
        with mock.patch.object(pipeline_mod, "utils") as utils_mock, \
             mock.patch.object(pipeline_mod, "voice") as voice_mock, \
             mock.patch.object(pipeline_mod, "render") as render_mock, \
             mock.patch.object(pipeline_mod, "audioutil") as audio_mock, \
             mock.patch.object(pipeline_mod, "video") as video_mock, \
             mock.patch.object(pipeline_mod, "sm") as sm_mock:
            with tempfile.TemporaryDirectory() as d:
                utils_mock.task_dir.return_value = d
                voice_mock.get_audio_duration.return_value = 8.0

                def write_audio(text, voice_name, voice_rate, voice_file, voice_volume):
                    with open(voice_file, "wb") as fh:
                        fh.write(b"a")
                    return object()
                voice_mock.tts.side_effect = write_audio

                def fake_render(beat, target_duration, out_dir, index):
                    p = os.path.join(out_dir, f"beat-{index}.mp4")
                    with open(p, "wb") as fh:
                        fh.write(b"x")
                    return p
                render_mock.render_beat.side_effect = fake_render

                def fake_pad(in_path, target_secs, out_path):
                    with open(out_path, "wb") as fh:
                        fh.write(b"a")
                    return out_path
                audio_mock.pad_audio_to.side_effect = fake_pad
                audio_mock.concat_audio.side_effect = lambda files, out, output_dir: out
                video_mock.generate_video.side_effect = RuntimeError("mux boom")

                result = pipeline_mod.start("task-fail", params)

        self.assertIsNone(result)
        states = [c.kwargs.get("state")
                  for c in sm_mock.state.update_task.call_args_list
                  if "state" in c.kwargs]
        self.assertIn(const_mod.TASK_STATE_FAILED, states)


class TestTaskBranch(unittest.TestCase):
    def test_start_delegates_to_mathflow_when_flow_type_math(self):
        params = VideoParams(video_subject="x", flow_type="math_explainer")
        with mock.patch("app.services.mathflow.pipeline.start") as math_start:
            math_start.return_value = {"videos": ["final-1.mp4"]}
            result = task_mod.start("task-9", params)
        math_start.assert_called_once()
        self.assertEqual(result, {"videos": ["final-1.mp4"]})


if __name__ == "__main__":
    unittest.main()
