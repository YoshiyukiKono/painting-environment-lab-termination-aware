from pathlib import Path

import numpy as np

from painting_env_lab.config import ExperimentConfig
from painting_env_lab.greedy import StopReason, paint_greedily


def test_flat_white_target_stops_without_accepted_actions() -> None:
    target = np.ones((8, 8, 3), dtype=np.float32)
    config = ExperimentConfig(
        width=8,
        height=8,
        max_steps=50,
        candidates_per_search=8,
        patience=3,
        epsilon=0.0,
        min_radius=1.0,
        max_radius=3.0,
        output_dir=Path("unused"),
    )
    result = paint_greedily(target, config)
    assert result.stop_reason == StopReason.NO_IMPROVEMENT
    assert len(result.records) == 0
    assert result.attempted_searches == 3


def test_max_steps_remains_safety_limit() -> None:
    target = np.zeros((12, 12, 3), dtype=np.float32)
    config = ExperimentConfig(
        width=12,
        height=12,
        seed=1,
        max_steps=1,
        candidates_per_search=16,
        patience=3,
        epsilon=0.0,
        min_radius=1.0,
        max_radius=4.0,
        output_dir=Path("unused"),
    )
    result = paint_greedily(target, config)
    assert result.stop_reason == StopReason.MAX_STEPS
    assert len(result.records) == 1
