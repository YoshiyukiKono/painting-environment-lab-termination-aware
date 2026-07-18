from __future__ import annotations

from .config import ExperimentConfig
from .greedy import GreedyResult, paint_greedily
from .reporting import write_outputs
from .targets import make_target


def run_experiment(config: ExperimentConfig) -> GreedyResult:
    target = make_target(config.target, config.width, config.height, config.seed)
    result = paint_greedily(target, config)
    write_outputs(target, result, config)
    return result
