import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pytest
from experiment_logic import (
    generate_temperature_order,
    precalculate_ramp_rates,
    generate_surface_order,
)


def test_generate_temperature_order_length_and_shuffle():
    np.random.seed(0)
    temps = [1, 2, 3]
    repeats = 2
    order = generate_temperature_order(temps, repeats)
    assert len(order) == len(temps) * repeats
    assert sorted(order) == sorted(temps * repeats)
    # With the seed above the order should be shuffled
    assert order != temps * repeats


def test_precalculate_ramp_rates_keys():
    temps = [40, 50]
    rates = precalculate_ramp_rates(temps, baseline=35, ramp_up_secs=3, ramp_down_secs=2, min_rate=0.1)
    for t in temps:
        assert t in rates
        assert set(rates[t].keys()) == {"rise", "return"}


def test_generate_surface_order_no_consecutive_repeat():
    np.random.seed(1)
    temp_order = [50, 45, 50, 45, 50]
    surfaces = [1, 2, 3]
    order = generate_surface_order(temp_order, surfaces, max_temp=50)
    assert len(order) == len(temp_order)
    assert all(order[i] != order[i - 1] for i in range(1, len(order)))

