"""5-second visual smoke test: one glowing terracotta dot eases across a
cream field, leaving a trail. If this looks good, the pipeline is right.

Run: python -m src.smoke
"""
from __future__ import annotations

import os
import math

import imageio.v2 as imageio
import numpy as np

from . import palette
from .easing import ease_in_out_cubic, ease_in_out_sine, lerp
from .render import Renderer, RenderConfig, font_serif, font


OUT_PATH = "output/smoke.mp4"
SECONDS = 5
FPS = 30


def main():
    os.makedirs("output", exist_ok=True)
    cfg = RenderConfig(width=1280, height=720, fps=FPS,
                       trail_decay=0.94, bloom_sigma=12.0, bloom_strength=0.6)
    r = Renderer(cfg)

    title_font = font_serif(46)
    label_font = font(18)

    frames = []
    total = SECONDS * FPS

    for i in range(total):
        t = i / max(total - 1, 1)
        r.begin_frame()

        # title (faded in/out)
        title_alpha = int(255 * (1 - abs(2 * t - 1) ** 2))
        r.text(r.surface, "Intentional Rescue", (cfg.width // 2, 110),
               title_font, color=palette.INK, alpha=title_alpha, anchor="center")
        r.text(r.surface, "RENDER PIPELINE — SMOKE TEST",
               (cfg.width // 2, 160),
               label_font, color=palette.DIM_INK, alpha=title_alpha,
               anchor="center")

        # eased horizontal sweep
        x = lerp(180, cfg.width - 180, ease_in_out_cubic(t))
        y = cfg.height // 2 + 80 + math.sin(t * math.tau) * 22

        # stamp a soft mark into the trail layer each frame
        def stamp(layer, x=x, y=y):
            r.soft_halo(layer, (x, y), 10, palette.HERO, alpha=60, layers=5)
            r.aacircle(layer, (x, y), 6, palette.HERO, alpha=120)
        r.stamp_trail(stamp)

        # current agent
        r.soft_halo(r.surface, (x, y), 18, palette.HERO, alpha=60, layers=6)
        r.aacircle(r.surface, (x, y), 14, palette.HERO)

        frame = r.composite_frame()
        frames.append(frame)

    print(f"[smoke] writing {len(frames)} frames -> {OUT_PATH}")
    imageio.mimsave(OUT_PATH, frames, fps=FPS, codec="libx264",
                    quality=8, macro_block_size=1)
    print("[smoke] done.")


if __name__ == "__main__":
    main()
