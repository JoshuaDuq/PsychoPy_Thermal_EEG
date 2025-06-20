import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pytest
from experiment_logic import (
    generate_temperature_order,
    precalculate_ramp_rates,
    generate_surface_order,
    generate_run_trial_lists,
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
    assert order[0] == max(temps)


def test_precalculate_ramp_rates_keys():
    temps = [40, 50]
    rates = precalculate_ramp_rates(
        temps, baseline=35, ramp_up_secs=3, ramp_down_secs=2, min_rate=0.1
    )
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


def test_generate_surface_order_balanced_distribution():
    np.random.seed(2)
    temp_order = [40] * 4 + [45] * 4
    surfaces = [1, 2]
    order = generate_surface_order(temp_order, surfaces, max_temp=45)

    counts = {(t, s): 0 for t in set(temp_order) for s in surfaces}
    for t, s in zip(temp_order, order):
        counts[(t, s)] += 1

    for t in set(temp_order):
        assert counts[(t, 1)] == counts[(t, 2)]


def test_generate_run_trial_lists_properties():
    np.random.seed(3)
    temps = [44.3, 45.3, 46.3, 47.3, 48.3, 49.3]
    surfaces = [1, 2, 3, 4, 5]
    runs = generate_run_trial_lists(temps, surfaces)

    assert len(runs) == 5
    for run in runs:
        assert len(run) == 12
        # ensure no immediate repeat of surfaces
        assert all(run[i][1] != run[i - 1][1] for i in range(1, len(run)))

    # each pair occurs exactly twice overall
    counts = {}
    for run in runs:
        for pair in run:
            counts[pair] = counts.get(pair, 0) + 1
    assert all(count == 2 for count in counts.values())

    # run 1 first pair fixed
    assert runs[0][0] == (max(temps), surfaces[0])
