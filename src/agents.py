"""Hero and Friend: small autonomous-looking robots.

Drawn as soft warm discs with a slow breath (radius pulse). The Hero also
carries a BDI snapshot — what it currently believes, desires, and plans —
which is rendered separately by the chyron, not by the agent itself.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from . import palette
from .easing import lerp


@dataclass
class Agent:
    name: str
    pos: tuple[float, float]
    color: tuple[int, int, int]
    radius: float = 16.0
    breath_speed: float = 0.55       # breaths per second
    breath_amp: float = 1.6
    glow_alpha: int = 70
    dim: float = 0.0                 # 0 = bright, 1 = nearly off (for Friend in Beat 2)
    phase: float = 0.0               # animation phase offset

    def breath_radius(self, t: float) -> float:
        return self.radius + math.sin((t + self.phase) * self.breath_speed * math.tau) * self.breath_amp

    def draw(self, renderer, t: float):
        r = self.breath_radius(t)
        dim_mix = self.dim
        # mix colour toward a desaturated warm-grey when dimmed
        DULL = (170, 158, 138)
        c = (
            int(lerp(self.color[0], DULL[0], dim_mix)),
            int(lerp(self.color[1], DULL[1], dim_mix)),
            int(lerp(self.color[2], DULL[2], dim_mix)),
        )
        glow_alpha = int(self.glow_alpha * (1 - 0.75 * dim_mix))
        renderer.soft_halo(renderer.surface, self.pos, r * 1.4, c,
                           alpha=glow_alpha, layers=6)
        renderer.aacircle(renderer.surface, self.pos, r, c)


def lerp_pos(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def chain(points: Sequence[tuple[float, float]], t: float) -> tuple[float, float]:
    """Walk a piecewise-linear chain at parameter t in [0, 1]."""
    if t <= 0:
        return points[0]
    if t >= 1:
        return points[-1]
    n_seg = len(points) - 1
    raw = t * n_seg
    i = int(raw)
    f = raw - i
    return lerp_pos(points[i], points[i + 1], f)


def chain_length(points: Sequence[tuple[float, float]]) -> float:
    s = 0.0
    for a, b in zip(points, points[1:]):
        s += math.hypot(b[0] - a[0], b[1] - a[1])
    return s


def chain_at_length(points: Sequence[tuple[float, float]], d: float) -> tuple[float, float]:
    """Walk a piecewise-linear chain at arc length d (0..total)."""
    if d <= 0:
        return points[0]
    remaining = d
    for a, b in zip(points, points[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if remaining <= seg:
            f = remaining / max(seg, 1e-9)
            return lerp_pos(a, b, f)
        remaining -= seg
    return points[-1]
