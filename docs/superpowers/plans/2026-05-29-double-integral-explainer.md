# Double-Integral Math-Explainer Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a hardcoded `math_explainer` flow to MoneyPrinterTurbo that renders a ~100s, 9:16 (720×1280) Vietnamese-narrated 3D explainer video about double integrals, reusing MPT's TTS, subtitle-burning, BGM, mux, task, API, and WebUI plumbing.

**Architecture:** A new `flow_type` field on `VideoParams` selects the flow. `task.start()` branches to a new `app/services/mathflow/` package. The flow generates per-beat Vietnamese TTS, renders one Manim scene per beat padded to the narration length, concatenates beat videos + audio, builds an SRT, and hands everything to the existing `video.generate_video()` for subtitle burning, BGM, and final mux.

**Tech Stack:** Python 3.11+, Manim Community (new dep), edge-tts (existing `voice.py`), moviepy/ffmpeg (existing), Streamlit (WebUI), `unittest`.

**Spec:** `docs/superpowers/specs/2026-05-29-double-integral-explainer-design.md`

---

## File Structure

**Create:**
- `app/services/mathflow/__init__.py` — package marker.
- `app/services/mathflow/srt.py` — pure SRT cue builder + timestamp formatter.
- `app/services/mathflow/timing.py` — pure per-beat duration / silence-padding math.
- `app/services/mathflow/audioutil.py` — ffmpeg helpers: pad audio to length, concat audio.
- `app/services/mathflow/scenes/__init__.py` — package marker.
- `app/services/mathflow/scenes/double_integral.py` — Manim scene base + 7 beat scenes + `formula()`.
- `app/services/mathflow/render.py` — `render_beat()` drives Manim programmatically.
- `app/services/mathflow/beats.py` — `Beat` dataclass + hardcoded `BEATS` list.
- `app/services/mathflow/pipeline.py` — `start()` orchestrator.
- `resource/fonts/DejaVuSans.ttf` — Vietnamese-capable subtitle font (bundled).
- `test/services/test_mathflow.py` — unit tests (srt, timing, beats registry, pipeline wiring).

**Modify:**
- `app/models/schema.py` — add `flow_type` to `VideoParams`.
- `app/services/task.py` — branch on `flow_type` at top of `start()`.
- `webui/Main.py` — flow selector, disabled controls, validation bypass, routing.
- `pyproject.toml` and `requirements.txt` — add `manim`.

**Conventions (match existing tests):** every test file starts with:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```
Run tests with `python -m unittest test.services.test_mathflow -v`.

---

## Task 1: Add `flow_type` to VideoParams

**Files:**
- Modify: `app/models/schema.py:73-108` (inside `class VideoParams`)
- Test: `test/services/test_mathflow.py`

- [ ] **Step 1: Write the failing test**

Create `test/services/test_mathflow.py`:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.schema import VideoParams


class TestFlowType(unittest.TestCase):
    def test_flow_type_defaults_to_standard(self):
        params = VideoParams(video_subject="x")
        self.assertEqual(params.flow_type, "standard")

    def test_flow_type_accepts_math_explainer(self):
        params = VideoParams(video_subject="x", flow_type="math_explainer")
        self.assertEqual(params.flow_type, "math_explainer")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestFlowType -v`
Expected: FAIL — `AttributeError: 'VideoParams' object has no attribute 'flow_type'`

- [ ] **Step 3: Add the field**

In `app/models/schema.py`, inside `class VideoParams`, immediately after the line `video_subject: str` (line 73), add:
```python
    flow_type: Optional[str] = "standard"  # "standard" | "math_explainer"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestFlowType -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/models/schema.py test/services/test_mathflow.py
git commit -m "feat: add flow_type to VideoParams"
```

---

## Task 2: SRT cue builder (`srt.py`)

**Files:**
- Create: `app/services/mathflow/__init__.py`
- Create: `app/services/mathflow/srt.py`
- Test: `test/services/test_mathflow.py`

- [ ] **Step 1: Create the package marker**

Create `app/services/mathflow/__init__.py` with a single line:
```python
"""Math-explainer video flow (hardcoded double-integral MVP)."""
```

- [ ] **Step 2: Write the failing test**

Append to `test/services/test_mathflow.py` (before the `if __name__` block):
```python
from app.services.mathflow import srt


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
            content = open(out, encoding="utf-8").read()
        self.assertIn("1\n00:00:00,000 --> 00:00:01,000\nhello", content)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestSrt -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.mathflow.srt'`

- [ ] **Step 4: Implement `srt.py`**

Create `app/services/mathflow/srt.py`:
```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestSrt -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add app/services/mathflow/__init__.py app/services/mathflow/srt.py test/services/test_mathflow.py
git commit -m "feat: add SRT cue builder for mathflow"
```

---

## Task 3: Per-beat timing math (`timing.py`)

**Files:**
- Create: `app/services/mathflow/timing.py`
- Test: `test/services/test_mathflow.py`

- [ ] **Step 1: Write the failing test**

Append to `test/services/test_mathflow.py`:
```python
from app.services.mathflow import timing


class TestTiming(unittest.TestCase):
    def test_beat_duration_takes_the_longer(self):
        self.assertEqual(timing.beat_duration(audio_dur=4.0, anim_min=10.0), 10.0)
        self.assertEqual(timing.beat_duration(audio_dur=12.0, anim_min=10.0), 12.0)

    def test_silence_padding_is_nonnegative(self):
        self.assertEqual(timing.silence_padding(audio_dur=4.0, target=10.0), 6.0)
        self.assertEqual(timing.silence_padding(audio_dur=12.0, target=10.0), 0.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestTiming -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.mathflow.timing'`

- [ ] **Step 3: Implement `timing.py`**

Create `app/services/mathflow/timing.py`:
```python
def beat_duration(audio_dur: float, anim_min: float) -> float:
    """A beat lasts as long as the longer of its narration or its animation."""
    return max(float(audio_dur), float(anim_min))


def silence_padding(audio_dur: float, target: float) -> float:
    """Seconds of trailing silence needed to stretch narration to the beat length."""
    return max(0.0, float(target) - float(audio_dur))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestTiming -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/mathflow/timing.py test/services/test_mathflow.py
git commit -m "feat: add per-beat timing math for mathflow"
```

---

## Task 4: Add Manim dependency + bundle Vietnamese font

**Files:**
- Modify: `pyproject.toml:15-34`
- Modify: `requirements.txt`
- Create: `resource/fonts/DejaVuSans.ttf`

- [ ] **Step 1: Add `manim` to `pyproject.toml`**

In `app/.../pyproject.toml`, inside the `dependencies = [ ... ]` list (lines 15-34), add this line after `"litellm==1.60.0",`:
```python
    "manim==0.18.1",
```

- [ ] **Step 2: Add `manim` to `requirements.txt`**

Append to `requirements.txt`:
```
manim==0.18.1
```

- [ ] **Step 3: Install Manim and verify import**

Run: `python -m pip install "manim==0.18.1"`
Then: `python -c "import manim; print(manim.__version__)"`
Expected: prints `0.18.1` (or the resolved patch). If install fails for missing system libs, install `libcairo2-dev libpango1.0-dev pkg-config` (Debian/Ubuntu) and retry. Document any extra step in the commit message.

- [ ] **Step 4: Bundle a Vietnamese-capable font**

Run:
```bash
cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf resource/fonts/DejaVuSans.ttf
```
If that file is absent, download it:
```bash
curl -L -o resource/fonts/DejaVuSans.ttf \
  https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf
```
Verify it loads and covers Vietnamese diacritics:
```bash
python -c "from PIL import ImageFont; f=ImageFont.truetype('resource/fonts/DejaVuSans.ttf', 40); print('ok', f.getname())"
```
Expected: prints `ok ('DejaVu Sans', 'Book')`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt resource/fonts/DejaVuSans.ttf
git commit -m "build: add manim dependency and bundle Vietnamese font"
```

---

## Task 5: Manim scenes (`scenes/double_integral.py`)

**Files:**
- Create: `app/services/mathflow/scenes/__init__.py`
- Create: `app/services/mathflow/scenes/double_integral.py`

This task defines the visual content. There is no fast unit test (rendering is slow); correctness is checked by the manual render smoke test in Step 4 and tuned in Task 12. The scenes use only stable Manim CE API.

- [ ] **Step 1: Create the package marker**

Create `app/services/mathflow/scenes/__init__.py`:
```python
"""Manim scenes for the double-integral explainer."""
```

- [ ] **Step 2: Implement the scene base + `formula()` + 7 beat scenes**

Create `app/services/mathflow/scenes/double_integral.py`:
```python
"""Manim scenes for the double-integral explainer (Vietnamese, 9:16).

Each beat scene subclasses TimedThreeDScene and implements animate_body().
The base pads with self.wait() so the scene lasts exactly target_duration.
Formulas use unicode Text via formula() — the single LaTeX-upgrade seam.
"""
import numpy as np
from manim import (
    ThreeDScene, ThreeDAxes, Surface, Text, Prism, Rectangle, VGroup,
    Create, FadeIn, FadeOut, Write, BLACK, WHITE, YELLOW, PINK, TEAL,
    DEGREES, UP, RIGHT, ORIGIN,
)

VI_FONT = "DejaVu Sans"
SURFACE_COLOR = TEAL
HIGHLIGHT = YELLOW
COLUMN_COLOR = PINK


def f(x, y):
    """The explainer surface z = e^{-(x^2 + y^2)}."""
    return np.exp(-(x ** 2 + y ** 2))


def formula(text: str, size: int = 40, color=WHITE) -> Text:
    """Render a formula/label as unicode Text (LaTeX-upgrade seam)."""
    return Text(text, font=VI_FONT, font_size=size, color=color)


class TimedThreeDScene(ThreeDScene):
    """Base class: subclasses implement animate_body(); base pads to target_duration."""

    def __init__(self, target_duration: float = 10.0, **kwargs):
        self.target_duration = float(target_duration)
        super().__init__(**kwargs)

    def construct(self):
        self.camera.background_color = BLACK
        self.animate_body()
        remaining = self.target_duration - self.renderer.time
        if remaining > 0:
            self.wait(remaining)

    def animate_body(self):  # overridden by each beat
        raise NotImplementedError

    def make_axes(self) -> ThreeDAxes:
        axes = ThreeDAxes(
            x_range=[-2, 2, 1], y_range=[-2, 2, 1], z_range=[0, 1.2, 0.5],
            x_length=6, y_length=6, z_length=3,
        )
        return axes

    def make_surface(self, axes: ThreeDAxes) -> Surface:
        return Surface(
            lambda u, v: axes.c2p(u, v, f(u, v)),
            u_range=[-2, 2], v_range=[-2, 2],
            resolution=(24, 24), fill_opacity=0.6, checkerboard_colors=[SURFACE_COLOR],
            stroke_color=SURFACE_COLOR, stroke_width=0.5,
        )


class Intro1DScene(TimedThreeDScene):
    """Beat 1: the single (1D) integral as area under a curve."""

    def animate_body(self):
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        axes = self.make_axes()
        self.play(Create(axes), run_time=2)
        label = formula("∫ f(x) dx  —  diện tích dưới đường cong", size=34)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(UP)
        self.play(Write(label), run_time=2)
        self.wait(1)


class Surface3DScene(TimedThreeDScene):
    """Beat 2: introduce the 3D surface z = f(x, y)."""

    def animate_body(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        axes = self.make_axes()
        surface = self.make_surface(axes)
        self.play(Create(axes), run_time=2)
        self.play(Create(surface), run_time=3)
        label = formula("z = f(x, y) = e^(−(x² + y²))", size=34)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(UP)
        self.play(Write(label), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(2)


class CellDAScene(TimedThreeDScene):
    """Beat 3: highlight a small area cell dA = dx·dy on the xy-plane."""

    def animate_body(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        axes = self.make_axes()
        surface = self.make_surface(axes)
        self.add(axes, surface)
        cell = Rectangle(width=0.6, height=0.6, fill_color=HIGHLIGHT,
                         fill_opacity=0.8, stroke_color=HIGHLIGHT)
        cell.move_to(axes.c2p(0.3, 0.3, 0))
        self.play(FadeIn(cell), run_time=2)
        label = formula("dA = dx · dy", size=36, color=HIGHLIGHT)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(UP)
        self.play(Write(label), run_time=2)
        self.wait(1)


class VolumeColumnScene(TimedThreeDScene):
    """Beat 4: build one small volume column f(x,y)·dA up to the surface."""

    def animate_body(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        axes = self.make_axes()
        surface = self.make_surface(axes)
        self.add(axes, surface)
        height = f(0.3, 0.3)
        column = Prism(dimensions=[0.6, 0.6, max(height, 0.05)],
                       fill_color=COLUMN_COLOR, fill_opacity=0.7)
        column.move_to(axes.c2p(0.3, 0.3, height / 2))
        self.play(FadeIn(column), run_time=3)
        label = formula("Thể tích cột nhỏ = f(x, y) · dA", size=34, color=COLUMN_COLOR)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(UP)
        self.play(Write(label), run_time=2)
        self.wait(1)


class RiemannSumScene(TimedThreeDScene):
    """Beat 5: many columns — V ≈ ΣΣ f(x,y)ΔA."""

    def animate_body(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        axes = self.make_axes()
        self.add(axes)
        columns = VGroup()
        step = 0.5
        xs = np.arange(-1.5, 1.5, step)
        ys = np.arange(-1.5, 1.5, step)
        for x in xs:
            for y in ys:
                h = f(x + step / 2, y + step / 2)
                col = Prism(dimensions=[step * 0.9, step * 0.9, max(h, 0.03)],
                            fill_color=COLUMN_COLOR, fill_opacity=0.6)
                col.move_to(axes.c2p(x + step / 2, y + step / 2, h / 2))
                columns.add(col)
        self.play(FadeIn(columns), run_time=4)
        label = formula("V ≈ ΣΣ f(x, y) ΔA", size=38, color=COLUMN_COLOR)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(UP)
        self.play(Write(label), run_time=2)
        self.wait(1)


class SliceScene(TimedThreeDScene):
    """Beat 6: a slice plane swept across x — the iterated integral."""

    def animate_body(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-50 * DEGREES)
        axes = self.make_axes()
        surface = self.make_surface(axes)
        self.add(axes, surface)
        plane = Rectangle(width=4, height=3, fill_color=HIGHLIGHT,
                          fill_opacity=0.4, stroke_color=HIGHLIGHT)
        plane.rotate(90 * DEGREES, axis=RIGHT)
        plane.move_to(axes.c2p(-1.5, 0, 0.6))
        self.play(FadeIn(plane), run_time=1)
        self.play(plane.animate.move_to(axes.c2p(1.5, 0, 0.6)), run_time=4)
        label = formula("∫ [ ∫ f(x, y) dy ] dx", size=36, color=HIGHLIGHT)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(UP)
        self.play(Write(label), run_time=2)
        self.wait(1)


class ConclusionScene(TimedThreeDScene):
    """Beat 7: V = ∬_D f(x,y) dA."""

    def animate_body(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        axes = self.make_axes()
        surface = self.make_surface(axes)
        self.play(Create(surface), run_time=2)
        self.add(axes)
        big = formula("V = ∬_D f(x, y) dA", size=48, color=SURFACE_COLOR)
        self.add_fixed_in_frame_mobjects(big)
        big.move_to(ORIGIN)
        self.play(Write(big), run_time=3)
        self.wait(2)
```

- [ ] **Step 3: Smoke-check that the module imports**

Run: `python -c "from app.services.mathflow.scenes import double_integral as d; print([c.__name__ for c in (d.Intro1DScene, d.ConclusionScene)])"`
Expected: prints `['Intro1DScene', 'ConclusionScene']` with no error.

- [ ] **Step 4: Manual render smoke test (one short scene)**

Run:
```bash
python - <<'PY'
from manim import tempconfig
from app.services.mathflow.scenes.double_integral import Surface3DScene
with tempconfig({"pixel_width": 720, "pixel_height": 1280, "frame_rate": 15,
                 "media_dir": "/tmp/mathflow_smoke", "disable_caching": True,
                 "verbosity": "ERROR"}):
    Surface3DScene(target_duration=6.0).render()
print("rendered")
PY
```
Expected: prints `rendered` and an mp4 appears under `/tmp/mathflow_smoke/videos/...`. If a Manim API call errors, fix the offending call (stay on documented CE 0.18 API) before continuing.

- [ ] **Step 5: Commit**

```bash
git add app/services/mathflow/scenes/
git commit -m "feat: add double-integral Manim scenes"
```

---

## Task 6: Beat render driver (`render.py`)

**Files:**
- Create: `app/services/mathflow/render.py`
- Test: `test/services/test_mathflow.py`

- [ ] **Step 1: Write the failing test (Manim mocked — no real render)**

Append to `test/services/test_mathflow.py`:
```python
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
                open(path, "wb").write(b"x")

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestRender -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.mathflow.render'`

- [ ] **Step 3: Implement `render.py`**

Create `app/services/mathflow/render.py`:
```python
import os
import shutil
import contextlib

from loguru import logger


def _import_manim_tempconfig():
    try:
        from manim import tempconfig
        return tempconfig
    except ImportError as exc:  # pragma: no cover - exercised only without manim
        raise RuntimeError(
            "manim is not installed. Install it with: pip install manim==0.18.1"
        ) from exc


def _tempconfig_for(out_dir: str, index: int):
    """Return a Manim tempconfig context manager for a 9:16 720x1280 render."""
    tempconfig = _import_manim_tempconfig()
    settings = {
        "pixel_width": 720,
        "pixel_height": 1280,
        "frame_rate": 30,
        "background_color": "#000000",
        "media_dir": os.path.join(out_dir, "manim_media"),
        "output_file": f"beat-{index}",
        "disable_caching": True,
        "verbosity": "ERROR",
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestRender -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/mathflow/render.py test/services/test_mathflow.py
git commit -m "feat: add Manim beat render driver"
```

---

## Task 7: Beat registry (`beats.py`)

**Files:**
- Create: `app/services/mathflow/beats.py`
- Test: `test/services/test_mathflow.py`

- [ ] **Step 1: Write the failing test**

Append to `test/services/test_mathflow.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestBeats -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.mathflow.beats'`

- [ ] **Step 3: Implement `beats.py`**

Create `app/services/mathflow/beats.py`:
```python
from dataclasses import dataclass
from typing import List, Type

from app.services.mathflow.scenes import double_integral as di


@dataclass(frozen=True)
class Beat:
    key: str
    narration_vi: str
    scene_cls: Type
    anim_min_secs: float


BEATS: List[Beat] = [
    Beat(
        key="intro_1d",
        narration_vi=(
            "Hãy bắt đầu từ tích phân một lớp. "
            "Nó cho ta diện tích nằm dưới một đường cong."
        ),
        scene_cls=di.Intro1DScene,
        anim_min_secs=11.0,
    ),
    Beat(
        key="surface_3d",
        narration_vi=(
            "Bây giờ ta nâng lên không gian ba chiều, "
            "với một mặt cong z bằng f của x và y."
        ),
        scene_cls=di.Surface3DScene,
        anim_min_secs=14.0,
    ),
    Beat(
        key="cell_dA",
        narration_vi=(
            "Trên mặt phẳng xy, ta lấy một ô diện tích rất nhỏ, "
            "ký hiệu dA bằng dx nhân dy."
        ),
        scene_cls=di.CellDAScene,
        anim_min_secs=12.0,
    ),
    Beat(
        key="volume_column",
        narration_vi=(
            "Dựng một cột thẳng đứng từ ô nhỏ đó lên tới mặt cong. "
            "Thể tích của cột bằng f của x, y nhân với dA."
        ),
        scene_cls=di.VolumeColumnScene,
        anim_min_secs=14.0,
    ),
    Beat(
        key="riemann_sum",
        narration_vi=(
            "Cộng rất nhiều cột nhỏ như vậy lại, "
            "ta xấp xỉ được thể tích: tổng kép của f nhân delta A."
        ),
        scene_cls=di.RiemannSumScene,
        anim_min_secs=14.0,
    ),
    Beat(
        key="slice",
        narration_vi=(
            "Ta cũng có thể cắt mặt cong bằng các lát phẳng. "
            "Cộng diện tích các lát chính là tích phân lặp."
        ),
        scene_cls=di.SliceScene,
        anim_min_secs=13.0,
    ),
    Beat(
        key="conclusion",
        narration_vi=(
            "Khi các ô nhỏ vô hạn, tổng trở thành tích phân hai lớp: "
            "thể tích bằng tích phân kép của f trên miền D."
        ),
        scene_cls=di.ConclusionScene,
        anim_min_secs=12.0,
    ),
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestBeats -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/mathflow/beats.py test/services/test_mathflow.py
git commit -m "feat: add hardcoded double-integral beat registry"
```

---

## Task 8: Audio helpers (`audioutil.py`)

**Files:**
- Create: `app/services/mathflow/audioutil.py`
- Test: `test/services/test_mathflow.py`

These wrap ffmpeg (reusing `video.get_ffmpeg_binary()`). The test verifies command construction with `subprocess.run` mocked (no real ffmpeg).

- [ ] **Step 1: Write the failing test**

Append to `test/services/test_mathflow.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestAudioUtil -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.mathflow.audioutil'`

- [ ] **Step 3: Implement `audioutil.py`**

Create `app/services/mathflow/audioutil.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestAudioUtil -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/mathflow/audioutil.py test/services/test_mathflow.py
git commit -m "feat: add ffmpeg audio pad/concat helpers for mathflow"
```

---

## Task 9: Pipeline orchestrator (`pipeline.py`)

**Files:**
- Create: `app/services/mathflow/pipeline.py`
- Test: `test/services/test_mathflow.py`

- [ ] **Step 1: Write the failing test (all heavy calls mocked)**

Append to `test/services/test_mathflow.py`:
```python
from app.models.schema import VideoParams
from app.services.mathflow import pipeline as pipeline_mod


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
                    open(p, "wb").write(b"x")
                    return p
                render_mock.render_beat.side_effect = fake_render

                def fake_pad(in_path, target_secs, out_path):
                    open(out_path, "wb").write(b"a")
                    return out_path
                audio_mock.pad_audio_to.side_effect = fake_pad
                audio_mock.concat_audio.side_effect = lambda files, out, output_dir: out

                # voice.tts writes the audio file the pipeline checks for
                def write_audio(text, voice_name, voice_rate, voice_file, voice_volume):
                    open(voice_file, "wb").write(b"a")
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestPipeline -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.mathflow.pipeline'`

- [ ] **Step 3: Implement `pipeline.py`**

Create `app/services/mathflow/pipeline.py`:
```python
import os

from loguru import logger

from app.models import const
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


def start(task_id, params, stop_at: str = "video"):
    logger.info(f"start math_explainer task: {task_id}")
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

        try:
            beat_video = render.render_beat(beat, target_duration=target,
                                            out_dir=task_path, index=index)
        except Exception as exc:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED)
            logger.error(f"math beat '{beat.key}' render failed: {exc}")
            return

        padded_audio = os.path.join(task_path, f"beat-{index}.mp3")
        audioutil.pad_audio_to(raw_audio, target_secs=target, out_path=padded_audio)

        beat_videos.append(beat_video)
        beat_audios.append(padded_audio)
        segments.append((beat.narration_vi, target))

        sm.state.update_task(task_id, progress=5 + int(70 * index / len(BEATS)))

    scenes_video = os.path.join(task_path, "scenes.mp4")
    video.concat_video_clips_with_ffmpeg(
        beat_videos, scenes_video, threads=params.n_threads, output_dir=task_path)

    full_audio = os.path.join(task_path, "audio.mp3")
    audioutil.concat_audio(beat_audios, full_audio, output_dir=task_path)

    subtitle_path = os.path.join(task_path, "subtitle.srt")
    srt_mod.write_srt(srt_mod.build_cues(segments), subtitle_path)

    sm.state.update_task(task_id, state=const.TASK_STATE_PROCESSING, progress=85)

    final_video = os.path.join(task_path, "final-1.mp4")
    video.generate_video(
        video_path=scenes_video,
        audio_path=full_audio,
        subtitle_path=subtitle_path,
        output_file=final_video,
        params=params,
    )

    kwargs = {
        "videos": [final_video],
        "combined_videos": [scenes_video],
        "audio_file": full_audio,
        "subtitle_path": subtitle_path,
    }
    sm.state.update_task(task_id, state=const.TASK_STATE_COMPLETE, progress=100, **kwargs)
    logger.success(f"math_explainer task {task_id} finished")
    return kwargs
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestPipeline -v`
Expected: PASS

- [ ] **Step 5: Run the whole mathflow suite**

Run: `python -m unittest test.services.test_mathflow -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/services/mathflow/pipeline.py test/services/test_mathflow.py
git commit -m "feat: add math_explainer pipeline orchestrator"
```

---

## Task 10: Branch `task.start()` on flow_type

**Files:**
- Modify: `app/services/task.py:248-250`
- Test: `test/services/test_mathflow.py`

- [ ] **Step 1: Write the failing test**

Append to `test/services/test_mathflow.py`:
```python
from app.services import task as task_mod


class TestTaskBranch(unittest.TestCase):
    def test_start_delegates_to_mathflow_when_flow_type_math(self):
        params = VideoParams(video_subject="x", flow_type="math_explainer")
        with mock.patch("app.services.mathflow.pipeline.start") as math_start:
            math_start.return_value = {"videos": ["final-1.mp4"]}
            result = task_mod.start("task-9", params)
        math_start.assert_called_once()
        self.assertEqual(result, {"videos": ["final-1.mp4"]})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test.services.test_mathflow.TestTaskBranch -v`
Expected: FAIL — the standard flow runs instead (it will try to generate a script / hit the network or return None), so `math_start` is not called.

- [ ] **Step 3: Add the branch**

In `app/services/task.py`, at the very start of `def start(...)` (immediately after line 249 `logger.info(f"start task: {task_id}, stop_at: {stop_at}")`), insert:
```python
    if getattr(params, "flow_type", "standard") == "math_explainer":
        from app.services.mathflow import pipeline as mathflow_pipeline
        return mathflow_pipeline.start(task_id, params, stop_at=stop_at)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test.services.test_mathflow.TestTaskBranch -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/task.py test/services/test_mathflow.py
git commit -m "feat: route math_explainer flow in task.start"
```

---

## Task 11: WebUI flow selector + routing

**Files:**
- Modify: `webui/Main.py` (selector near line 525; disabled controls at the subject/source widgets; validation bypass at lines 1063-1081)

No unit test (Streamlit UI); verified manually in Task 12.

- [ ] **Step 1: Add the flow selector above the settings panel**

In `webui/Main.py`, immediately after line 527 (`uploaded_audio_file = None`) and before the `with left_panel:` block at line 529, add this module-level selector (it renders above the three-column panel):
```python
flow_label_map = {
    "standard": tr("Standard short video"),
    "math_explainer": tr("Math Explainer: Double Integral"),
}
flow_keys = list(flow_label_map.keys())
selected_flow = st.selectbox(
    tr("Flow"),
    options=range(len(flow_keys)),
    format_func=lambda i: flow_label_map[flow_keys[i]],
    index=0,
)
params.flow_type = flow_keys[selected_flow]
is_math_flow = params.flow_type == "math_explainer"
if is_math_flow:
    st.info(tr("Math Explainer flow: subject, script, keywords and video source are fixed and ignored."))
```
(Do not set `params.video_subject` here — the subject widget at line 532 runs afterward and would overwrite it, and the math pipeline ignores `video_subject` anyway. The empty-subject validation is bypassed in Step 3.)

- [ ] **Step 2: Disable the now-irrelevant inputs**

In `webui/Main.py`, add `disabled=is_math_flow,` to these existing widgets, leaving every other argument unchanged:
- The subject `st.text_input(...)` at line 532 (key `video_subject_input`).
- The script `st.text_area(...)` at line 571.
- The keywords `st.text_area(...)` at line 586.
- The video-source `st.selectbox(...)` near line 611.

Example for the subject input (line 532) — note the existing key is `video_subject_input`:
```python
        params.video_subject = st.text_input(
            tr("Video Subject"),
            value=st.session_state["video_subject"],
            key="video_subject_input",
            disabled=is_math_flow,
        ).strip()
```
(Apply the same `disabled=is_math_flow,` argument to the other three widgets, keeping their existing arguments exactly as they are.)

- [ ] **Step 3: Bypass subject/source validation for the math flow**

In `webui/Main.py`, replace the validation block at lines 1063-1081 (the four `if`/`st.error`/`st.stop()` checks for empty subject and video source) so they are skipped for the math flow. Wrap them:
```python
    if not is_math_flow:
        if not params.video_subject and not params.video_script:
            st.error(tr("Video Script and Subject Cannot Both Be Empty"))
            scroll_to_bottom()
            st.stop()

        if params.video_source not in ["pexels", "pixabay", "local"]:
            st.error(tr("Please Select a Valid Video Source"))
            scroll_to_bottom()
            st.stop()

        if params.video_source == "pexels" and not config.app.get("pexels_api_keys", ""):
            st.error(tr("Please Enter the Pexels API Key"))
            scroll_to_bottom()
            st.stop()

        if params.video_source == "pixabay" and not config.app.get("pixabay_api_keys", ""):
            st.error(tr("Please Enter the Pixabay API Key"))
            scroll_to_bottom()
            st.stop()
```
(The downstream `result = tm.start(task_id=task_id, params=params)` call at line 1144 already routes correctly via Task 10 — no change needed there.)

- [ ] **Step 4: Verify the WebUI imports and starts**

Run: `python -c "import ast; ast.parse(open('webui/Main.py').read()); print('syntax ok')"`
Expected: prints `syntax ok`.
Then launch and eyeball the selector:
Run: `streamlit run webui/Main.py` (or `sh webui.sh`), open the URL, confirm the **Flow** selector appears, selecting **Math Explainer** disables subject/source inputs and shows the info banner.

- [ ] **Step 5: Commit**

```bash
git add webui/Main.py
git commit -m "feat: add math-explainer flow selector to WebUI"
```

---

## Task 12: End-to-end render + duration tuning

**Files:**
- Possibly tune: `app/services/mathflow/beats.py` (`anim_min_secs`), `app/services/mathflow/scenes/double_integral.py` (animation run_times)

- [ ] **Step 1: Run the full flow headless**

```bash
python - <<'PY'
from app.models.schema import VideoParams
from app.services.mathflow import pipeline
params = VideoParams(video_subject="x", flow_type="math_explainer")
result = pipeline.start("e2e-doubleintegral", params)
print(result)
PY
```
Expected: completes without error and prints a dict containing `videos: ['.../final-1.mp4']`. This is slow (Manim renders 7 scenes).

- [ ] **Step 2: Inspect the output video**

Verify the final video exists, is 720×1280, ~90–110s, has Vietnamese audio, and shows correctly-rendered Vietnamese subtitles (no tofu boxes):
```bash
python -c "from moviepy import VideoFileClip; import glob; \
p=glob.glob('storage/tasks/e2e-doubleintegral/final-1.mp4')[0]; \
c=VideoFileClip(p); print(p, c.size, round(c.duration,1))"
```
Expected: prints the path, `[720, 1280]`, and a duration near 100s.

- [ ] **Step 3: Tune if needed**

If total duration is far from ~100s, or a scene's animation overruns/feels rushed, adjust `anim_min_secs` in `beats.py` and/or `run_time` values in `double_integral.py`. Re-run Step 1. Confirm subtitles stay aligned to narration (one cue per beat).

- [ ] **Step 4: Run the full unit suite one more time**

Run: `python -m unittest test.services.test_mathflow -v`
Expected: all PASS.

- [ ] **Step 5: Commit any tuning**

```bash
git add app/services/mathflow/beats.py app/services/mathflow/scenes/double_integral.py
git commit -m "chore: tune double-integral beat durations"
```

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** flow_type (T1, T10), Manim engine + no LaTeX (T4, T5 `formula()`), per-beat audio-first sync + padding (T3, T8, T9), assembly + reuse of `generate_video` (T9), SRT one-cue-per-beat (T2, T9), WebUI selector + reuse of voice/subtitle/BGM (T11), Vietnamese font + voice defaults (T4 bundle, T9 `_apply_defaults`), error handling per beat (T9), tests (T2/T3/T6/T7/T8/T9/T10). All spec sections map to a task.
- **Manim API risk:** `Prism`, `Surface`, `add_fixed_in_frame_mobjects`, `begin_ambient_camera_rotation`, `self.renderer.time`, and `tempconfig` are all stable Manim CE 0.18 API. The Task 5 Step 4 smoke test catches any drift before the full pipeline runs.
- **Type consistency:** `Beat(key, narration_vi, scene_cls, anim_min_secs)` is used identically in T7 and T9; `render_beat(beat, target_duration, out_dir, index)` signature matches between T6 and T9; `build_cues`/`write_srt`/`SubtitleCue` match between T2 and T9.
