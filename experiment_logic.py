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
    """Pre-generates the thermode surface order to avoid repetition."""
    num_trials = len(temp_order)
    surface_order = [0] * num_trials
    last_surface_overall = None
    last_surface_max_temp = None

    for i in range(num_trials):
        current_temp = temp_order[i]
        possible_surfaces = list(available_surfaces)

        # Avoid repeating the last used surface if possible
        if last_surface_overall is not None and len(possible_surfaces) > 1:
            choices = [s for s in possible_surfaces if s != last_surface_overall]
            if choices: possible_surfaces = choices

        # For max temp, avoid repeating the last max_temp surface
        if current_temp == max_temp:
            if last_surface_max_temp is not None and len(possible_surfaces) > 1:
                choices = [s for s in possible_surfaces if s != last_surface_max_temp]
                if choices: possible_surfaces = choices
        
        chosen_surface = int(np.random.choice(possible_surfaces))
        surface_order[i] = chosen_surface
        last_surface_overall = chosen_surface
        if current_temp == max_temp:
            last_surface_max_temp = chosen_surface
            
    logger.debug("Pre-generated surface order: %s", surface_order)
    return surface_order