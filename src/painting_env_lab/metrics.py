from __future__ import annotations

import numpy as np


def mean_squared_error(canvas: np.ndarray, target: np.ndarray) -> float:
    if canvas.shape != target.shape:
        raise ValueError("canvas and target must have the same shape")
    return float(np.mean((canvas - target) ** 2))
