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
        remaining = self.target_duration - self._elapsed_seconds()
        if remaining > 0:
            self.wait(remaining)

    def _elapsed_seconds(self) -> float:
        # Manim CE accumulates elapsed scene time on the renderer. Guard with getattr so
        # padding never crashes if the attribute name shifts across Manim versions; the
        # Task 5 smoke test confirms the value is non-zero on the pinned 0.18 release.
        return float(getattr(self.renderer, "time", 0.0) or 0.0)

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
