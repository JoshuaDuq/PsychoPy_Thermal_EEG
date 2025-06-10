# experiment_logic.py

import numpy as np
import logging

logger = logging.getLogger(__name__)

def generate_temperature_order(temps, repeats):
    """Creates and shuffles the temperature order for all trials."""
    order = np.tile(temps, repeats)
    np.random.shuffle(order)
    logger.debug("Randomized temperature order generated: %s", order)
    return order.tolist()

def precalculate_ramp_rates(temps, baseline, ramp_up_secs, ramp_down_secs, min_rate):
    """Precalculate rise and return rates for each possible temperature."""
    temps_arr = np.asarray(temps, dtype=float)
    diff = np.abs(temps_arr - baseline)

    rise = np.where(ramp_up_secs > 0, diff / ramp_up_secs, 99.0)
    ret = np.where(ramp_down_secs > 0, diff / ramp_down_secs, 99.0)

    rise = np.where(diff > 0, np.maximum(rise, min_rate), 10.0)
    ret = np.where(diff > 0, np.maximum(ret, min_rate), 10.0)

    rates = {
        float(t): {'rise': float(r), 'return': float(d)}
        for t, r, d in zip(temps_arr, rise, ret)
    }
    logger.debug("Pre-calculated ramp rates: %s", rates)
    return rates

def generate_surface_order(temp_order, available_surfaces, max_temp):
    """Pre-generate a surface order balancing temperatures across surfaces."""
    num_trials = len(temp_order)
    surface_order = [0] * num_trials
    available_surfaces = list(available_surfaces)

    # Determine how many times each temperature should appear on each surface
    temp_counts = {t: temp_order.count(t) for t in set(temp_order)}
    remaining = {}
    n_surfaces = len(available_surfaces)
    for t, count in temp_counts.items():
        base = count // n_surfaces
        extra = count % n_surfaces
        counts = {s: base for s in available_surfaces}
        if extra:
            extras = np.random.choice(available_surfaces, size=extra, replace=False)
            for s in extras:
                counts[s] += 1
        remaining[t] = counts

    last_surface_overall = None
    last_surface_max_temp = None

    for i, current_temp in enumerate(temp_order):
        candidate_surfaces = [s for s in available_surfaces if remaining[current_temp][s] > 0]

        # Avoid repeating the last used surface if possible
        if last_surface_overall is not None and len(candidate_surfaces) > 1:
            choices = [s for s in candidate_surfaces if s != last_surface_overall]
            if choices:
                candidate_surfaces = choices

        # For max temp, avoid repeating the last max_temp surface
        if current_temp == max_temp and last_surface_max_temp is not None and len(candidate_surfaces) > 1:
            choices = [s for s in candidate_surfaces if s != last_surface_max_temp]
            if choices:
                candidate_surfaces = choices

        chosen_surface = int(np.random.choice(candidate_surfaces))
        surface_order[i] = chosen_surface
        remaining[current_temp][chosen_surface] -= 1
        last_surface_overall = chosen_surface
        if current_temp == max_temp:
            last_surface_max_temp = chosen_surface

    logger.debug("Pre-generated surface order: %s", surface_order)
    return surface_order