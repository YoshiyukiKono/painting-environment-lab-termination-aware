from __future__ import annotations

import argparse
from pathlib import Path

from .config import ExperimentConfig
from .experiment import run_experiment
from .targets import TARGET_NAMES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a termination-aware greedy painting experiment.")
    parser.add_argument("--target", choices=TARGET_NAMES, default="gradient")
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-steps", type=int, default=2_000)
    parser.add_argument("--candidates", type=int, default=96)
    parser.add_argument("--epsilon", type=float, default=1e-5)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--min-radius", type=float, default=1.5)
    parser.add_argument("--max-radius", type=float, default=24.0)
    parser.add_argument("--output", type=Path, default=Path("outputs/latest"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = ExperimentConfig(
        target=args.target,
        width=args.width,
        height=args.height,
        seed=args.seed,
        max_steps=args.max_steps,
        candidates_per_search=args.candidates,
        epsilon=args.epsilon,
        patience=args.patience,
        min_radius=args.min_radius,
        max_radius=args.max_radius,
        output_dir=args.output,
    )
    result = run_experiment(config)
    print(f"target={config.target}")
    print(f"stop_reason={result.stop_reason.value}")
    print(f"accepted_steps={len(result.records)}")
    print(f"attempted_searches={result.attempted_searches}")
    print(f"candidate_evaluations={result.candidate_evaluations}")
    print(f"final_error={result.final_error:.8f}")
    print(f"output={config.output_dir}")


if __name__ == "__main__":
    main()
