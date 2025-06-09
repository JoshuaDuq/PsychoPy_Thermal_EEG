# PsychoPy EEG Modularized

This repository contains a modular PsychoPy experiment for delivering thermal
pain stimulation while recording EEG data. The code is organized so that
hardware setup, triggering, trial logic and data management live in separate
modules.

## Data output

All result files are written inside the `data/<participant_id>` directory when
the experiment finishes. The filenames include the participant identifier,
experiment name and date (e.g. `01_ThermalPainEEG_20240101_TrialSummary.csv`).

### TrialSummary.csv
Provides one row per trial with the following columns:
- `trial_number` &ndash; sequential index starting at 1
- `stimulus_temp` &ndash; stimulus temperature in °C
- `selected_surface` &ndash; thermode surface used
- `pain_binary_coded` &ndash; pain question response (1 for "yes" and 0 for
  "no")
- `vas_final_coded_rating` &ndash; final visual analogue scale (VAS) rating
  already coded for pain context

### VASTraces_Long.csv
Contains every sampled VAS rating for each trial in long format:
- `participant_id`
- `trial_number`
- `stimulus_temp`
- `pain_context_0no_1yes`
- `sample_in_trace` &ndash; sample index within the trial
- `vas_time_in_trial_secs` &ndash; timestamp of the sample (s)
- `vas_coded_rating` &ndash; coded rating value

### BACKUP.npz
A compressed NumPy archive storing the raw lists from the data collector. This
serves as a full backup should any custom analysis be required.

