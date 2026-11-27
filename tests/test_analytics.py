import pytest

from ecopulse.analytics import calculate_average


def test_calculate_average():
    assert calculate_average([10.0, 20.0, 30.0]) == 20.0


def test_empty_values():
    with pytest.raises(ValueError):
        calculate_average([])
