from __future__ import annotations

import numpy as np

TARGET_NAMES = ("flat", "geometry", "gradient", "noise")


def make_target(name: str, width: int, height: int, seed: int = 0) -> np.ndarray:
    if name not in TARGET_NAMES:
        raise ValueError(f"unknown target {name!r}; choose from {TARGET_NAMES}")

    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:height, 0:width]

    if name == "flat":
        color = np.array([0.20, 0.58, 0.82], dtype=np.float32)
        return np.broadcast_to(color, (height, width, 3)).copy()

    if name == "geometry":
        image = np.full((height, width, 3), [0.94, 0.90, 0.78], dtype=np.float32)
        circle = (x - width * 0.32) ** 2 + (y - height * 0.42) ** 2 <= (min(width, height) * 0.22) ** 2
        image[circle] = [0.18, 0.32, 0.66]
        image[int(height * 0.58):int(height * 0.86), int(width * 0.48):int(width * 0.88)] = [0.83, 0.23, 0.18]
        return image

    if name == "gradient":
        nx = x.astype(np.float32) / max(width - 1, 1)
        ny = y.astype(np.float32) / max(height - 1, 1)
        red = 0.10 + 0.80 * nx
        green = 0.15 + 0.70 * ny
        blue = 0.85 - 0.55 * nx + 0.05 * np.sin(ny * np.pi)
        return np.clip(np.stack([red, green, blue], axis=-1), 0.0, 1.0).astype(np.float32)

    base = rng.random((height, width, 3), dtype=np.float32)
    # Mild spatial averaging retains high-frequency structure while avoiding pure white noise.
    padded = np.pad(base, ((1, 1), (1, 1), (0, 0)), mode="reflect")
    smoothed = sum(
        padded[dy:dy + height, dx:dx + width]
        for dy in range(3)
        for dx in range(3)
    ) / 9.0
    return smoothed.astype(np.float32)
