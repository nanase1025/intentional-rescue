"""Render the full film to output/intentional_rescue.mp4.

Run from the project root:

    python -m src.main
"""
from __future__ import annotations

import argparse
import os
import time

from .scene import render_film


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="output/intentional_rescue.mp4")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    args = ap.parse_args()

    os.makedirs("output", exist_ok=True)
    t0 = time.time()
    render_film(args.out, fps=args.fps, width=args.width, height=args.height)
    dt = time.time() - t0
    print(f"[main] total render time: {dt:.1f}s")


if __name__ == "__main__":
    main()
