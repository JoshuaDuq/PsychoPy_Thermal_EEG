# config.py

import numpy as np

# --- Hexadecimal Trigger Definitions (Aligned with BrainVision Bit Mapping) ---
TRIG_RESET = b'\x00'         # ALL BITS LOW
TRIG_EEG_REC_START = b'\x01' # Bit 0 HIGH (EEG Rec Start event)
TRIG_ITI_START = b'\x02'     # Bit 1 HIGH (ITI phase active)
TRIG_STIM_ON = b'\x04'       # Bit 2 HIGH (Stimulus phase active)
TRIG_STIM_OFF = b'\x08'      # Bit 3 HIGH (Stimulus Offset event)
TRIG_PAIN_Q_ON = b'\x10'     # Bit 4 HIGH (Pain Question phase active)
TRIG_VAS_ON = b'\x20'        # Bit 5 HIGH (VAS phase active)

# --- Experiment Specific Variables & Temperature Generation ---
POSSIBLE_THERMODE_TEMPS = [44.3, 45.3, 46.3, 47.3, 48.3, 49.3]
NUM_REPEATS_PER_TEMP = 10
MAX_TEMP_VALUE = max(POSSIBLE_THERMODE_TEMPS) if POSSIBLE_THERMODE_TEMPS else 0
AVAILABLE_SURFACES = [1, 2, 3, 4, 5]

# --- Timing and Ramp Constants ---
BASELINE_TEMP = 35.0
RAMP_UP_SECS_CONST = 3.0
RAMP_DOWN_SECS_CONST = 2.0
STIM_HOLD_DURATION_SECS = 7.5
MIN_RATE_CONST = 0.1
ITI_DURATION_RANGE = (15, 20) # Min and Max ITI in seconds

# --- VAS Routine Constants ---
VAS_SPEED_UNITS_PER_SEC = 22.0
VAS_MAX_DURATION_SECS = 30.0
VAS_SAMPLING_INTERVAL_SECS = 0.02