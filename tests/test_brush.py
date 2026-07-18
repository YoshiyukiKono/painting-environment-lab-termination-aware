import numpy as np

from painting_env_lab.brush import BrushAction, apply_circle_stamp


def test_circle_stamp_changes_center_without_mutating_input() -> None:
    canvas = np.ones((9, 9, 3), dtype=np.float32)
    action = BrushAction(x=4, y=4, radius=2, color=(0.1, 0.2, 0.3))
    result = apply_circle_stamp(canvas, action)
    assert np.allclose(canvas, 1.0)
    assert np.allclose(result[4, 4], [0.1, 0.2, 0.3])
    assert np.allclose(result[0, 0], 1.0)
