# Double-Integral Math-Explainer Flow (MVP)

**Date:** 2026-05-29
**Status:** Approved design, ready for implementation plan
**Scope:** A hardcoded MVP that generates one specific video — a Vietnamese-narrated 3D
"math explainer" about double integrals, in the visual spirit of 3Blue1Brown / GlassBox
(black background, teal 3D surface, slow camera, formulas revealed incrementally).

## 1. Goal & Non-Goals

### Goal
Add a second video-generation flow to MoneyPrinterTurbo that renders a ~100s, 9:16
(1080×1920) math-explainer video for the topic **double integrals**, with Vietnamese
narration and burned Vietnamese subtitles, reusing as much of the existing MPT pipeline
(TTS, subtitle burning, BGM, muxing, task/state/API/WebUI plumbing) as possible.

The video reproduces this 7-beat narrative arc from the reference:
1. Start from the single (1D) integral.
2. Introduce the 3D surface `z = f(x, y)` (use `z = e^(−(x²+y²))`).
3. Highlight a small area cell `dA = dx · dy` on the xy-plane.
4. Build one small volume column `f(x,y)·dA` from the cell up to the surface.
5. Riemann sum: many columns, `V ≈ ΣΣ f(x,y)ΔA`.
6. Slice plane sweeping the surface (iterated integral `∫[∫ f dy]dx`).
7. Conclusion: `V = ∬_D f(x,y) dA` — summing infinitely many tiny volume columns.

### Non-Goals (MVP)
- No LLM-generated animation code, no scene templating engine, no topic generality.
  The topic, script, and scenes are **hardcoded** for double integrals only.
- No LaTeX/`MathTex` dependency. Formulas use Manim `Text`/unicode behind a `formula()`
  seam so a LaTeX upgrade is a one-spot change later.
- No Blender / Three.js / Remotion. Engine is **Manim** (Python, drops into this codebase).

## 2. Engine & Dependency Decisions

- **Engine: Manim Community.** Reasons: Python (no Node/Blender pipeline), purpose-built
  for this 3D math-animation style, programmatically renderable from the task worker.
- **New dependency:** `manim` added to `pyproject.toml` and `requirements.txt`. No texlive.
- **ffmpeg:** already provided via `moviepy` / `imageio-ffmpeg` (no system ffmpeg required).
- **Vietnamese font:** the current `resource/fonts/` holds Chinese `.ttc` fonts that lack
  Vietnamese diacritics (would render tofu when subtitles are burned). Bundle a
  Vietnamese-capable TTF (DejaVuSans or Noto Sans) into `resource/fonts/` and default the
  math flow's `font_name` to it. Manim in-scene labels use `font="DejaVu Sans"`.
- **Default narration voice:** `vi-VN-HoaiMyNeural-Female` (edge-tts), overridable in WebUI.

## 3. Architecture & Integration

A new field on `VideoParams`:

```python
flow_type: Optional[str] = "standard"   # "standard" | "math_explainer"
```

`app/services/task.py::start()` branches at the very top:

```python
def start(task_id, params, stop_at="video"):
    if getattr(params, "flow_type", "standard") == "math_explainer":
        from app.services.mathflow import pipeline as mathflow
        return mathflow.start(task_id, params, stop_at=stop_at)
    # ... existing standard flow unchanged ...
```

This keeps the API (`POST /videos` → `task_manager.add_task(tm.start, …)`), task manager,
and state/progress reporting identical. The standard flow is untouched.

### New module layout: `app/services/mathflow/`
- `__init__.py`
- `beats.py` — the hardcoded script (the 7 beats).
- `scenes/__init__.py`
- `scenes/double_integral.py` — Manim `ThreeDScene` subclasses, one per beat.
- `render.py` — drives Manim programmatically, outputs one silent mp4 per beat.
- `pipeline.py` — orchestrator (`start(task_id, params, stop_at)`).

## 4. Components

### 4.1 `beats.py`
```python
@dataclass
class Beat:
    key: str                 # e.g. "intro_1d", "surface_3d", ...
    narration_vi: str        # hardcoded Vietnamese narration for this beat
    scene_cls: type          # Manim scene class for this beat
    anim_min_secs: float     # minimum seconds the animation needs regardless of narration

BEATS: list[Beat] = [ ... 7 entries ... ]
```
Beat registry integrity is unit-tested (non-empty narration, scene_cls is a Manim Scene
subclass, anim_min_secs > 0, unique keys).

### 4.2 `scenes/double_integral.py`
- One `ThreeDScene` subclass per beat. Each accepts a `target_duration: float` and is
  responsible for finishing in exactly that wall-clock time: play its animations, then
  `self.wait(remaining)` to fill. `anim_min_secs` is the time the scene's animations take
  before any padding; because `target_duration = max(audio_dur, anim_min_secs)` (see 5.2),
  the animations always fit and the scene only ever waits to fill, never overruns.
- Shared visual config module-level constants: black background, teal surface color, pink/
  yellow highlight colors, axis styling, slow camera moves (`move_camera`, `begin_ambient_camera_rotation`).
- Surface: `z = e^(−(x²+y²))` via `Surface`. Volume columns via `Prism`/`Cube`. Riemann
  sum via a grid of thin prisms. Slice via a translucent plane swept across x.
- `formula(s: str) -> Mobject` helper renders formula strings as Manim `Text` with unicode
  glyphs (`∬ ∫ Σ dA ² ≈`). In a `ThreeDScene`, formulas/labels are added with
  `add_fixed_in_frame_mobjects` so they stay 2D/billboarded. This helper is the single
  LaTeX-upgrade seam.

### 4.3 `render.py`
- `render_beat(beat, target_duration, out_dir, index) -> str` configures Manim
  (`pixel_width=1080, pixel_height=1920, frame_rate=30`, black background, output to
  `out_dir`) and renders `beat.scene_cls` to a silent mp4. Returns the mp4 path.
- Raises a clear error with an install hint if `manim` import fails.
- **Resolution must equal `VideoAspect.portrait.to_resolution()` (1080×1920).**
  `video.generate_video()` does not resize the input video; it only uses that resolution
  to wrap (`width*0.9`) and position (`height*0.95`) subtitles. Rendering at any other
  size would push the burned Vietnamese subtitles off-screen. `frame_rate=30` matches the
  module-level `fps=30` in `video.py`.

### 4.4 `pipeline.py::start(task_id, params, stop_at)`
Mirrors the standard flow's state/progress contract.

## 5. Data Flow

### 5.1 Per-beat generation
For each `beat` in `BEATS` (progress updated incrementally):
1. `voice.tts(text=beat.narration_vi, voice_name=params.voice_name, voice_rate=params.voice_rate, voice_file=beat_i.mp3, voice_volume=params.voice_volume)`.
2. `audio_dur = voice.get_audio_duration(beat_i.mp3)`.
3. `dur_i = max(audio_dur, beat.anim_min_secs)`.
4. `render.render_beat(beat, target_duration=dur_i, out_dir=task_dir, index=i+1) -> beat_i.mp4`.

### 5.2 Padding rule (keep A/V aligned per beat)
Each beat occupies exactly `dur_i` on the final timeline:
- If `audio_dur < dur_i` (animation is the longer one): pad `beat_i.mp3` with trailing
  silence to `dur_i`.
- The scene is always rendered to `dur_i` (it waits to fill), so video already equals `dur_i`.

### 5.3 Assembly
5. Concatenate `beat_*.mp4` → `scenes.mp4` (reuse `video.concat_video_clips_with_ffmpeg`).
6. Concatenate the (padded) `beat_*.mp3` → `audio.mp3`.
7. Build `subtitle.srt` from cumulative beat start/end times + `narration_vi`
   (one cue per beat for the MVP).
8. `video.generate_video(video_path=scenes.mp4, audio_path=audio.mp3, subtitle_path=subtitle.srt, output_file=final-1.mp4, params=params)` — reuses MPT's subtitle burning, font/color/aspect handling, BGM, and final mux.
9. Cross-posting (`upload_post`) is **deferred for the MVP** — the math pipeline does not
   call it (the standard flow keeps it). Can be added later by mirroring the standard flow's
   step 7 with a fixed Vietnamese title.

### 5.4 State & stop_at
- Report `TASK_STATE_PROCESSING` with incremental `progress` across beats, then assembly.
- On success: `TASK_STATE_COMPLETE`, `progress=100`, return `{"videos": [final-1.mp4], ...}`
  matching the standard flow's result shape so the WebUI/API render it identically.
- `stop_at`: for the MVP only `"video"` is meaningfully supported; other values fall through
  to producing the full video (documented; no separate audio/subtitle-only endpoints needed).

## 6. WebUI Changes (`webui/Main.py`)

- Add a flow selector near the top of the settings panel:
  **"Standard short video"** / **"Math Explainer: Double Integral"**.
- When **Math Explainer** is selected:
  - Hide subject / keywords / video-source controls; show a caption that the topic is fixed.
  - Keep **voice**, **subtitle styling**, and **BGM** controls active — they are reused.
  - Default `font_name` to the bundled Vietnamese font; default voice to `vi-VN-HoaiMyNeural-Female`.
- The existing Generate button sets `params.flow_type = "math_explainer"` and submits the
  same task; everything downstream (task manager, progress, result display) is unchanged.

## 7. Error Handling

- `manim` import failure → fail the task with `TASK_STATE_FAILED` and a log line including
  the install command.
- Per-beat TTS failure → `TASK_STATE_FAILED`, logging which beat key failed (reuse the
  standard flow's failure pattern).
- Per-beat render failure → `TASK_STATE_FAILED`, logging which beat key failed.
- Concatenation / final mux failure → `TASK_STATE_FAILED`.

## 8. Testing

`test/services/test_mathflow.py`, matching the existing stubbed/offline test style:
- **SRT builder:** given a list of `(text, duration)`, produces correct cumulative
  `HH:MM:SS,mmm` start/end timestamps and sequential indices.
- **Duration/padding math:** `dur_i = max(audio_dur, anim_min)` and the silence-padding
  decision are correct for both branches.
- **Beat registry integrity:** `BEATS` non-empty, unique keys, non-empty narration, each
  `scene_cls` is a Manim `Scene` subclass, `anim_min_secs > 0`.
- **Pipeline wiring:** `voice.tts` and `render.render_beat` mocked (no real edge-tts / Manim
  render); assert the orchestration calls assembly with the expected file lists and that
  state transitions/progress are emitted.
- Real Manim rendering is a **slow manual integration check**, not part of the unit suite.

## 9. Dependencies Summary

- Add `manim` to `pyproject.toml` and `requirements.txt`.
- Add a Vietnamese-capable TTF to `resource/fonts/`.
- No LaTeX. ffmpeg via existing `imageio-ffmpeg`.

## 10. Open Risks

- Manim `ThreeDScene` + fixed-in-frame unicode formulas need care so glyphs (`∬`, `²`) render
  with the chosen font; mitigated by the `formula()` helper and font selection.
- Hitting a clean ~100s total depends on tuning each beat's `anim_min_secs` against the
  narration length; tunable because everything is hardcoded.
- First Manim render in a fresh/Docker environment may need cairo/pango system libs;
  document in install notes.
- Two distinct font paths: moviepy subtitle burning takes a TTF **file path**
  (`resource/fonts/DejaVuSans.ttf`, bundled here), but Manim `Text(font="DejaVu Sans")`
  resolves the font by **name via Pango/OS font cache**. The dev machine has DejaVu Sans
  installed; in a container without it, register the bundled TTF (e.g.
  `manimpango.register_font("resource/fonts/DejaVuSans.ttf")`) or install the OS package.
