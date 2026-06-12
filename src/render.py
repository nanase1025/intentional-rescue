"""Headless render pipeline: pygame draws frames, numpy/scipy post-process,
imageio writes mp4. No window, no screen recording.

Visual recipe:
- cream paper background with a faint warm grain
- agents drawn with anti-aliased filled circles (gfxdraw) plus a soft halo
- trails accumulated on a persistent alpha-blended layer
- final pass: gentle bloom (gaussian highlight) added back to compositor

The compositor stays in float32 [0..1] until the final encode so bloom
addition does not clip ugly.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pygame
import pygame.gfxdraw
from scipy.ndimage import gaussian_filter

from . import palette

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


@dataclass
class RenderConfig:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    trail_decay: float = 0.92          # 1.0 = trails never fade, 0 = no trails
    bloom_sigma: float = 14.0          # radius of glow
    bloom_strength: float = 0.55       # how much bloom is added back
    grain_strength: float = 0.012      # tiny paper noise


@dataclass
class Renderer:
    config: RenderConfig = field(default_factory=RenderConfig)

    def __post_init__(self):
        pygame.init()
        self.surface = pygame.Surface(
            (self.config.width, self.config.height), pygame.SRCALPHA
        )
        self.trail = pygame.Surface(
            (self.config.width, self.config.height), pygame.SRCALPHA
        )
        self.trail.fill((0, 0, 0, 0))
        self._grain = self._make_grain()

    # ---- public API ----------------------------------------------------

    def begin_frame(self):
        """Paint background + decayed trail."""
        self.surface.fill(palette.CREAM)
        self._fade_trail()
        self.surface.blit(self.trail, (0, 0))

    def stamp_trail(self, draw_fn):
        """draw_fn(surface) renders something onto the persistent trail layer."""
        draw_fn(self.trail)

    def composite_frame(self) -> np.ndarray:
        """Return final uint8 RGB array with bloom + grain applied."""
        arr = pygame.surfarray.array3d(self.surface).astype(np.float32) / 255.0
        # surfarray is (W, H, 3); transpose to (H, W, 3) for natural orientation
        arr = arr.transpose(1, 0, 2)

        if self.config.bloom_strength > 0:
            arr = self._apply_bloom(arr)

        if self.config.grain_strength > 0:
            arr = arr + self._grain * self.config.grain_strength
            arr = np.clip(arr, 0, 1)

        return (arr * 255).astype(np.uint8)

    # ---- drawing helpers ----------------------------------------------

    def aacircle(self, surface, center, radius, color, alpha=255):
        x, y = int(center[0]), int(center[1])
        r = max(1, int(radius))
        c = (color[0], color[1], color[2], alpha)
        pygame.gfxdraw.filled_circle(surface, x, y, r, c)
        pygame.gfxdraw.aacircle(surface, x, y, r, c)

    def soft_halo(self, surface, center, radius, color, alpha=70, layers=5):
        """Concentric translucent rings to fake a soft glow on the SDL layer.
        The real bloom happens in post; this is for the on-screen feel."""
        x, y = int(center[0]), int(center[1])
        for i in range(layers, 0, -1):
            r = int(radius * (1 + 0.5 * i / layers))
            a = int(alpha * (1 - i / (layers + 1)))
            c = (color[0], color[1], color[2], a)
            pygame.gfxdraw.filled_circle(surface, x, y, r, c)

    def aaline(self, surface, p1, p2, color, alpha=255, width=2):
        c = (color[0], color[1], color[2], alpha)
        if width <= 1:
            pygame.gfxdraw.line(surface, int(p1[0]), int(p1[1]),
                                int(p2[0]), int(p2[1]), c)
        else:
            pygame.draw.aaline(surface, c, p1, p2)
            pygame.draw.line(surface, c, p1, p2, width)

    def filled_rounded_rect(self, surface, rect, color, radius=12, alpha=255):
        pygame.draw.rect(
            surface,
            (color[0], color[1], color[2], alpha),
            rect,
            border_radius=radius,
        )

    def text(self, surface, txt, pos, font, color=palette.INK, alpha=255,
             anchor="topleft"):
        s = font.render(txt, True, color)
        if alpha < 255:
            s.set_alpha(alpha)
        rect = s.get_rect()
        setattr(rect, anchor, pos)
        surface.blit(s, rect)

    # ---- internals ----------------------------------------------------

    def _fade_trail(self):
        """Scale the trail's alpha channel down so old marks fade out cleanly
        without bleaching toward cream (which would lose contrast)."""
        mult = max(0, min(255, int(255 * self.config.trail_decay)))
        fader = pygame.Surface(
            (self.config.width, self.config.height), pygame.SRCALPHA
        )
        fader.fill((255, 255, 255, mult))
        self.trail.blit(fader, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def _make_grain(self) -> np.ndarray:
        rng = np.random.default_rng(7)
        g = rng.standard_normal((self.config.height, self.config.width, 1))
        g = g.astype(np.float32)
        return np.repeat(g, 3, axis=2)

    def _apply_bloom(self, arr: np.ndarray) -> np.ndarray:
        # extract highlights (above mid-grey) and blur them
        luma = arr.mean(axis=2, keepdims=True)
        highlight = np.maximum(arr - 0.55, 0)
        highlight = highlight * np.clip((luma - 0.45) * 2.5, 0, 1)
        blurred = np.empty_like(highlight)
        for c in range(3):
            blurred[..., c] = gaussian_filter(
                highlight[..., c], sigma=self.config.bloom_sigma
            )
        return np.clip(arr + blurred * self.config.bloom_strength, 0, 1)


def font(size: int, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """Pick the best available system font for our editorial look."""
    candidates_sans = ["Inter", "Helvetica Neue", "Helvetica", "Arial"]
    candidates_serif = ["Source Serif Pro", "Source Serif 4", "IBM Plex Serif",
                        "Charter", "Georgia", "Times New Roman"]
    # default to sans; serif requested via load_serif
    return _load(candidates_sans, size, bold, italic)


def font_serif(size: int, bold: bool = False, italic: bool = False):
    candidates = ["Source Serif Pro", "Source Serif 4", "IBM Plex Serif",
                  "Charter", "Georgia", "Times New Roman"]
    return _load(candidates, size, bold, italic)


def _load(names, size, bold, italic):
    pygame.font.init()
    for n in names:
        path = pygame.font.match_font(n, bold=bold, italic=italic)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size, bold=bold, italic=italic)
