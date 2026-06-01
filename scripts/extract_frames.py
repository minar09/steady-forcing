"""
extract_frames.py — Extract high-resolution frames from a video at specified timestamps.

Usage examples:
  # Explicit timestamps
  python extract_frames.py --video river.mp4 --times 0 15 30 45 60

  # Auto-evenly-spaced (e.g. 5 snapshots across the full duration)
  python extract_frames.py --video river.mp4 --count 5

  # Interval-based (every N seconds)
  python extract_frames.py --video river.mp4 --interval 15

  # Batch: all .mp4 files in a folder
  python extract_frames.py --folder ./generated_videos --interval 15

  # Override output directory
  python extract_frames.py --video river.mp4 --times 0 30 60 --output_dir ./snapshots

  python extract_frames.py --video river.mp4 --times 0 20 40 59 --output_dir ./snapshots

"""

import argparse
import os
import sys
from pathlib import Path

try:
    import cv2
except ImportError:
    sys.exit("opencv-python is required:  pip install opencv-python")

from PIL import Image   # only for optional upscaling — soft dependency
import numpy as np


# ─────────────────────────────────────────────────────────────
# Core extraction
# ─────────────────────────────────────────────────────────────

def get_video_info(cap: cv2.VideoCapture) -> tuple[float, float, int, int]:
    """Return (fps, duration_seconds, width, height)."""
    fps      = cap.get(cv2.CAP_PROP_FPS)
    n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    w        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h        = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = n_frames / fps if fps > 0 else 0.0
    return fps, duration, w, h


def resolve_timestamps(
    times:    list[float] | None,
    count:    int | None,
    interval: float | None,
    duration: float,
) -> list[float]:
    """Turn user arguments into a sorted list of timestamps (seconds)."""
    if times is not None:
        ts = sorted(set(times))
    elif interval is not None:
        ts = []
        t = 0.0
        while t <= duration + 1e-6:
            ts.append(round(t, 3))
            t += interval
    elif count is not None and count > 0:
        if count == 1:
            ts = [0.0]
        else:
            ts = [round(duration * i / (count - 1), 3) for i in range(count)]
    else:
        # Default: 0 %, 25 %, 50 %, 75 %, 100 %
        ts = [round(duration * p, 3) for p in [0.0, 0.25, 0.5, 0.75, 1.0]]

    # Clamp to [0, duration]
    ts = [max(0.0, min(t, duration)) for t in ts]
    return ts


def extract_frame(cap: cv2.VideoCapture, timestamp: float) -> np.ndarray | None:
    """Seek to timestamp (seconds) and return the frame as an RGB numpy array."""
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
    ret, frame = cap.read()
    if not ret:
        return None
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def save_frame(
    frame:      np.ndarray,
    output_dir: Path,
    stem:       str,
    timestamp:  float,
    fmt:        str = "png",
    upscale:    float = 1.0,
) -> Path:
    """Save a frame to disk, optionally upscaling it."""
    if upscale != 1.0:
        try:
            img = Image.fromarray(frame)
            new_w = int(img.width * upscale)
            new_h = int(img.height * upscale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            frame = np.array(img)
        except ImportError:
            print("  [warn] Pillow not installed — skipping upscale")

    # Use concise integer-second filenames (e.g., 0.png, 20.png)
    seconds_int = int(round(timestamp))
    outpath = output_dir / f"{seconds_int}.{fmt}"

    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if fmt.lower() in ("jpg", "jpeg"):
        cv2.imwrite(str(outpath), frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 97])
    else:
        cv2.imwrite(str(outpath), frame_bgr)      # PNG — lossless

    return outpath


# ─────────────────────────────────────────────────────────────
# Per-video driver
# ─────────────────────────────────────────────────────────────

def process_video(
    video_path: Path,
    times:      list[float] | None,
    count:      int | None,
    interval:   float | None,
    output_dir: Path | None,
    fmt:        str,
    upscale:    float,
) -> None:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[error] Cannot open: {video_path}")
        return

    fps, duration, w, h = get_video_info(cap)
    print(f"\n── {video_path.name}")
    print(f"   Resolution : {w}×{h}  |  FPS : {fps:.3f}  |  Duration : {duration:.3f}s")

    timestamps = resolve_timestamps(times, count, interval, duration)
    print(f"   Timestamps : {timestamps}")

    out_dir = output_dir or (video_path.parent / f"{video_path.stem}_frames")
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = video_path.stem
    saved = []

    for ts in timestamps:
        frame = extract_frame(cap, ts)
        if frame is None:
            print(f"   [warn] Could not read frame at t={ts:.3f}s — skipping")
            continue
        path = save_frame(frame, out_dir, stem, ts, fmt=fmt, upscale=upscale)
        saved.append(path)
        print(f"   ✓  t={ts:>8.3f}s  →  {path.name}")

    cap.release()
    print(f"   Saved {len(saved)} frames to: {out_dir}")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract high-resolution frames from a video at specified timestamps.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--video",  type=Path, help="Path to a single video file.")
    src.add_argument("--folder", type=Path, help="Process all .mp4 files in this folder.")

    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--times",    type=float, nargs="+",
        metavar="T",  help="Explicit timestamps in seconds (e.g. 0 15 30 45 60).",
    )
    mode.add_argument(
        "--count",    type=int,
        metavar="N",  help="Number of evenly-spaced frames to extract.",
    )
    mode.add_argument(
        "--interval", type=float,
        metavar="S",  help="Extract a frame every S seconds.",
    )

    p.add_argument("--output_dir", type=Path, default=None,
                   help="Output directory (default: <video_stem>_frames/ next to the video).")
    p.add_argument("--format",     choices=["png", "jpg"], default="png",
                   help="Output image format (default: png — lossless).")
    p.add_argument("--upscale",    type=float, default=1.0,
                   help="Upscale factor, e.g. 2.0 doubles resolution (requires Pillow).")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    videos: list[Path] = []
    if args.video:
        if not args.video.exists():
            sys.exit(f"[error] File not found: {args.video}")
        videos = [args.video]
    else:
        if not args.folder.is_dir():
            sys.exit(f"[error] Not a directory: {args.folder}")
        videos = sorted(args.folder.glob("*.mp4"))
        if not videos:
            sys.exit(f"[error] No .mp4 files found in: {args.folder}")
        print(f"Found {len(videos)} video(s) in {args.folder}")

    for vp in videos:
        process_video(
            video_path = vp,
            times      = args.times,
            count      = args.count,
            interval   = args.interval,
            output_dir = args.output_dir,
            fmt        = args.format,
            upscale    = args.upscale,
        )

    print("\nDone.")


if __name__ == "__main__":
    main()