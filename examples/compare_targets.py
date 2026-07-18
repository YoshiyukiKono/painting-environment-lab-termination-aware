from __future__ import annotations

import json
from pathlib import Path

from painting_env_lab import ExperimentConfig, run_experiment
from painting_env_lab.targets import TARGET_NAMES


def main() -> None:
    root = Path("outputs/comparison")
    rows: list[dict[str, object]] = []

    for target in TARGET_NAMES:
        config = ExperimentConfig(
            target=target,
            width=64,
            height=64,
            seed=7,
            max_steps=2_000,
            candidates_per_search=96,
            epsilon=1e-5,
            patience=12,
            output_dir=root / target,
        )
        result = run_experiment(config)
        rows.append(
            {
                "target": target,
                "stop_reason": result.stop_reason.value,
                "accepted_steps": len(result.records),
                "attempted_searches": result.attempted_searches,
                "candidate_evaluations": result.candidate_evaluations,
                "final_error": result.final_error,
            }
        )

    (root / "comparison.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
