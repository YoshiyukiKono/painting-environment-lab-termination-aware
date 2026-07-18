from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BrushAction:
    x: float
    y: float
    radius: float
    color: tuple[float, float, float]


def apply_circle_stamp(canvas: np.ndarray, action: BrushAction) -> np.ndarray:
    """Return a new canvas with one opaque circular stamp applied."""
    height, width, _ = canvas.shape
    yy, xx = np.mgrid[0:height, 0:width]
    mask = (xx - action.x) ** 2 + (yy - action.y) ** 2 <= action.radius ** 2
    result = canvas.copy()
    result[mask] = np.asarray(action.color, dtype=np.float32)
    return result
