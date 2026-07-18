from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from .brush import BrushAction, apply_circle_stamp
from .config import ExperimentConfig
from .metrics import mean_squared_error


class StopReason(StrEnum):
    NO_IMPROVEMENT = "no_improvement"
    MAX_STEPS = "max_steps"


@dataclass(frozen=True)
class StepRecord:
    step: int
    error_before: float
    error_after: float
    best_improvement: float
    x: float
    y: float
    radius: float
    color_r: float
    color_g: float
    color_b: float
    failed_searches: int
    candidate_evaluations: int


@dataclass(frozen=True)
class GreedyResult:
    canvas: np.ndarray
    records: list[StepRecord]
    stop_reason: StopReason
    final_error: float
    attempted_searches: int
    candidate_evaluations: int


def _sample_action(
    rng: np.random.Generator,
    target: np.ndarray,
    config: ExperimentConfig,
) -> BrushAction:
    height, width, _ = target.shape
    x = float(rng.uniform(0, width - 1))
    y = float(rng.uniform(0, height - 1))
    # Log-uniform radii give small and large brushes meaningful representation.
    radius = float(np.exp(rng.uniform(np.log(config.min_radius), np.log(config.max_radius))))
    tx = int(np.clip(round(x), 0, width - 1))
    ty = int(np.clip(round(y), 0, height - 1))
    color = tuple(float(v) for v in target[ty, tx])
    return BrushAction(x=x, y=y, radius=radius, color=color)


def paint_greedily(target: np.ndarray, config: ExperimentConfig) -> GreedyResult:
    config.validate()
    rng = np.random.default_rng(config.seed)
    canvas = np.ones_like(target, dtype=np.float32)
    records: list[StepRecord] = []
    failed_searches = 0
    attempted_searches = 0
    candidate_evaluations = 0

    while len(records) < config.max_steps:
        attempted_searches += 1
        current_error = mean_squared_error(canvas, target)
        best_action: BrushAction | None = None
        best_canvas: np.ndarray | None = None
        best_error = current_error

        for _ in range(config.candidates_per_search):
            action = _sample_action(rng, target, config)
            candidate = apply_circle_stamp(canvas, action)
            candidate_error = mean_squared_error(candidate, target)
            candidate_evaluations += 1
            if candidate_error < best_error:
                best_error = candidate_error
                best_action = action
                best_canvas = candidate

        improvement = current_error - best_error
        if best_action is None or best_canvas is None or improvement <= config.epsilon:
            failed_searches += 1
            if failed_searches >= config.patience:
                return GreedyResult(
                    canvas=canvas,
                    records=records,
                    stop_reason=StopReason.NO_IMPROVEMENT,
                    final_error=current_error,
                    attempted_searches=attempted_searches,
                    candidate_evaluations=candidate_evaluations,
                )
            continue

        canvas = best_canvas
        failed_searches = 0
        records.append(
            StepRecord(
                step=len(records) + 1,
                error_before=current_error,
                error_after=best_error,
                best_improvement=improvement,
                x=best_action.x,
                y=best_action.y,
                radius=best_action.radius,
                color_r=best_action.color[0],
                color_g=best_action.color[1],
                color_b=best_action.color[2],
                failed_searches=failed_searches,
                candidate_evaluations=candidate_evaluations,
            )
        )

    final_error = mean_squared_error(canvas, target)
    return GreedyResult(
        canvas=canvas,
        records=records,
        stop_reason=StopReason.MAX_STEPS,
        final_error=final_error,
        attempted_searches=attempted_searches,
        candidate_evaluations=candidate_evaluations,
    )
