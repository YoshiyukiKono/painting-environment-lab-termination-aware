import numpy as np
import pytest

from painting_env_lab.targets import TARGET_NAMES, make_target


@pytest.mark.parametrize("name", TARGET_NAMES)
def test_target_shape_and_range(name: str) -> None:
    target = make_target(name, width=20, height=12, seed=3)
    assert target.shape == (12, 20, 3)
    assert target.dtype == np.float32
    assert np.all(target >= 0.0)
    assert np.all(target <= 1.0)
