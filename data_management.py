# data_management.py

import os
import pandas as pd
import numpy as np

def create_data_collector():
    """Initializes a dictionary to hold all trial data."""
    return {
        'trial_number': [], 'stimulus_temp': [], 'selected_surface': [],
        'pain_binary_coded': [], 'vas_final_coded_rating': [],
        'vas_traces': [], 'vas_times': []
    }

def save_all_data(exp_info, exp_name, data, this_dir):
    """Saves trial summary, VAS traces, and a raw backup."""
    participant_id = str(exp_info.get('participant', 'UNKNOWN'))
    date_str = str(exp_info.get('date', 'NODATE'))
    
    # Create output directory
    participant_dir = os.path.join(this_dir, 'data', participant_id)
    os.makedirs(participant_dir, exist_ok=True)
    
    base_filename = f"{participant_id}_{exp_name}_{date_str}"

    # --- Save Trial Summary CSV ---
    try:
        summary_df = pd.DataFrame({
            'trial_number': data['trial_number'],
            'stimulus_temp': data['stimulus_temp'],
            'selected_surface': data['selected_surface'],
            'pain_binary_coded': data['pain_binary_coded'],
            'vas_final_coded_rating': data['vas_final_coded_rating']
        })
        summary_filename = os.path.join(participant_dir, f"{base_filename}_TrialSummary.csv")
        summary_df.to_csv(summary_filename, index=False, float_format='%.2f', na_rep='NA')
        print(f"Trial summary saved to {summary_filename}")
    except Exception as e:
        print(f"ERROR saving summary CSV: {e}")

    # --- Save VAS Traces Long Format CSV ---
    try:
        vas_long_list = []
        for i in range(len(data['trial_number'])):
            for sample_idx, (rating, time) in enumerate(zip(data['vas_traces'][i], data['vas_times'][i])):
                vas_long_list.append({
                    'participant_id': participant_id,
                    'trial_number': data['trial_number'][i],
                    'stimulus_temp': data['stimulus_temp'][i],
                    'pain_context_0no_1yes': data['pain_binary_coded'][i],
                    'sample_in_trace': sample_idx + 1,
                    'vas_time_in_trial_secs': time,
                    'vas_coded_rating': rating
                })
        if vas_long_list:
            vas_df = pd.DataFrame(vas_long_list)
            vas_filename = os.path.join(participant_dir, f"{base_filename}_VASTraces_Long.csv")
            vas_df.to_csv(vas_filename, index=False, float_format='%.4f', na_rep='NA')
            print(f"VAS traces saved to {vas_filename}")
    except Exception as e:
        print(f"ERROR saving VAS traces CSV: {e}")

    # --- Save Raw Lists Backup ---
    try:
        backup_filename = os.path.join(participant_dir, f"{base_filename}_BACKUP.npz")
        # Use dtype=object for lists of lists/uneven arrays
        np.savez_compressed(backup_filename, **{k: np.array(v, dtype=object) for k, v in data.items()})
        print(f"Raw data backup saved to {backup_filename}")
    except Exception as e:
        print(f"ERROR saving raw backup: {e}")