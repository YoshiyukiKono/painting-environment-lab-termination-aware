from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    target: str = "gradient"
    width: int = 64
    height: int = 64
    seed: int = 7
    max_steps: int = 2_000
    candidates_per_search: int = 96
    epsilon: float = 1e-5
    patience: int = 12
    min_radius: float = 1.5
    max_radius: float = 24.0
    output_dir: Path = Path("outputs/latest")

    def validate(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if self.candidates_per_search <= 0:
            raise ValueError("candidates_per_search must be positive")
        if self.epsilon < 0:
            raise ValueError("epsilon must be non-negative")
        if self.patience <= 0:
            raise ValueError("patience must be positive")
        if not 0 < self.min_radius <= self.max_radius:
            raise ValueError("radii must satisfy 0 < min_radius <= max_radius")

    def as_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["output_dir"] = str(self.output_dir)
        return data
