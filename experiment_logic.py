# experiment_logic.py

import numpy as np

def generate_temperature_order(temps, repeats):
    """Creates and shuffles the temperature order for all trials."""
    order = []
    for temp in temps:
        order.extend([temp] * repeats)
    np.random.shuffle(order)
    print(f"Randomized temperature order generated: {order}")
    return order

def precalculate_ramp_rates(temps, baseline, ramp_up_secs, ramp_down_secs, min_rate):
    """Precalculates rise and return rates for each possible temperature."""
    rates = {}
    for temp_val in temps:
        temp_diff = abs(temp_val - baseline)
        rise = (temp_diff / ramp_up_secs) if ramp_up_secs > 0 else 99.0
        ret = (temp_diff / ramp_down_secs) if ramp_down_secs > 0 else 99.0
        
        if temp_diff > 0:
            rise = max(rise, min_rate)
            ret = max(ret, min_rate)
        elif temp_diff == 0:
            rise, ret = 10.0, 10.0
            
        rates[temp_val] = {'rise': rise, 'return': ret}
    print(f"Pre-calculated ramp rates: {rates}")
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
            
    print(f"Pre-generated surface order: {surface_order}")
    return surface_order