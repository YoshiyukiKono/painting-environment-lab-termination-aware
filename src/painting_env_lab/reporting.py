from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .config import ExperimentConfig
from .greedy import GreedyResult


def _save_image(array: np.ndarray, path: Path) -> None:
    image = Image.fromarray(np.clip(array * 255.0, 0, 255).astype(np.uint8), mode="RGB")
    image.save(path)


def write_outputs(
    target: np.ndarray,
    result: GreedyResult,
    config: ExperimentConfig,
) -> None:
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    _save_image(target, output_dir / "target.png")
    _save_image(result.canvas, output_dir / "final_canvas.png")

    with (output_dir / "steps.csv").open("w", newline="", encoding="utf-8") as handle:
        if result.records:
            writer = csv.DictWriter(handle, fieldnames=list(asdict(result.records[0]).keys()))
            writer.writeheader()
            writer.writerows(asdict(record) for record in result.records)
        else:
            handle.write("step,error_before,error_after,best_improvement\n")

    summary = {
        "config": config.as_json_dict(),
        "result": {
            "stop_reason": result.stop_reason.value,
            "accepted_steps": len(result.records),
            "attempted_searches": result.attempted_searches,
            "candidate_evaluations": result.candidate_evaluations,
            "final_error": result.final_error,
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if result.records:
        steps = [record.step for record in result.records]
        errors = [record.error_after for record in result.records]
        improvements = [record.best_improvement for record in result.records]
        radii = [record.radius for record in result.records]

        plt.figure(figsize=(8, 4.5))
        plt.plot(steps, errors)
        plt.xlabel("Accepted step")
        plt.ylabel("Mean squared error")
        plt.title(f"Error curve — {config.target}")
        plt.tight_layout()
        plt.savefig(output_dir / "error_curve.png", dpi=150)
        plt.close()

        plt.figure(figsize=(8, 4.5))
        plt.plot(steps, improvements)
        plt.xlabel("Accepted step")
        plt.ylabel("Best improvement")
        plt.yscale("log")
        plt.title(f"Improvement curve — {config.target}")
        plt.tight_layout()
        plt.savefig(output_dir / "improvement_curve.png", dpi=150)
        plt.close()

        plt.figure(figsize=(8, 4.5))
        plt.plot(steps, radii)
        plt.xlabel("Accepted step")
        plt.ylabel("Brush radius")
        plt.title(f"Brush radius — {config.target}")
        plt.tight_layout()
        plt.savefig(output_dir / "radius_curve.png", dpi=150)
        plt.close()
