# main_experiment.py

import os
import numpy as np
from psychopy import core, visual, event, gui, data
from psychopy.hardware import keyboard

# --- Import Modularized Code ---
import config
import hardware_setup as hw
import triggering
import experiment_logic as logic
import data_management as dm

# =================================================================
# 1. SETUP & INITIALIZATION
# =================================================================

# --- Get Experiment Info ---
exp_info = {'participant': 'test01', 'date': data.getDateStr(), 'com_thermode': 'COM4', 'com_trigger': 'COM5', 'eeg_ip': '192.168.1.2'}
dlg = gui.DlgFromDict(dictionary=exp_info, title='Experiment Setup')
if not dlg.OK:
    core.quit()

exp_name = "ThermalPainEEG"
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# --- Initialize Hardware ---
thermode = hw.initialize_thermode(exp_info['com_thermode'], config.BASELINE_TEMP)
trigger_port = hw.initialize_trigger_port(exp_info['com_trigger'])
rcs = hw.initialize_eeg_rcs(
    host_ip=exp_info['eeg_ip'],
    workspace_path='C:/YOUR_EEG_WORKSPACE.rwksp', # <-- IMPORTANT: Set your actual workspace path here
    participant=f"{exp_info['participant']}_{exp_info['date']}",
    exp_name=exp_name
)

# Graceful exit if critical hardware fails
if thermode is None or trigger_port is None:
    print("Critical hardware failed to initialize. Exiting.")
    core.quit()

# --- Prepare Experiment Logic ---
temp_order = logic.generate_temperature_order(config.POSSIBLE_THERMODE_TEMPS, config.NUM_REPEATS_PER_TEMP)
surface_order = logic.generate_surface_order(temp_order, config.AVAILABLE_SURFACES, config.MAX_TEMP_VALUE)
ramp_rates = logic.precalculate_ramp_rates(config.POSSIBLE_THERMODE_TEMPS, config.BASELINE_TEMP, config.RAMP_UP_SECS_CONST, config.RAMP_DOWN_SECS_CONST, config.MIN_RATE_CONST)
num_trials = len(temp_order)

# --- Setup PsychoPy Window & Keyboard ---
win = visual.Window(size=(1920, 1080), fullscr=True, screen=0, winType='pyglet', allowGUI=False, color='black', units='height')
win.mouseVisible = False
kb = keyboard.Keyboard()

# --- Prepare Data Collection ---
exp_data = dm.create_data_collector()
thisExp = data.ExperimentHandler(name=exp_name, version='',
                                extraInfo=exp_info, runtimeInfo=None,
                                originPath='main_experiment.py',
                                savePickle=True, saveWideText=True,
                                dataFileName=os.path.join(_thisDir, 'data', f"{exp_info['participant']}_{exp_name}_{exp_info['date']}"))

# =================================================================
# 2. START EXPERIMENT
# =================================================================

# --- Start EEG Recording ---
if rcs:
    try:
        print("Commanding EEG to start recording...")
        rcs.startRecording()
        triggering.send_event_pulse(trigger_port, config.TRIG_EEG_REC_START, config.TRIG_RESET)
        print(f"Sent TRIG_EEG_REC_START pulse.")
    except Exception as e:
        print(f"EEG start recording error: {e}")

# --- Main Experiment Loop ---
main_loop = data.TrialHandler(nReps=num_trials, method='sequential', 
                              originPath=-1, trialList=[None], name='trials_loop')
thisExp.addLoop(main_loop)

for this_trial in main_loop:
    current_loop_index = main_loop.thisN
    
    # --- ITI Routine ---
    iti_duration = np.random.uniform(*config.ITI_DURATION_RANGE)
    win.callOnFlip(triggering.send_state_change, trigger_port, config.TRIG_ITI_START)
    fixation_cross = visual.TextStim(win, text='+', height=0.1)
    for _ in range(int(iti_duration * 60)): # Approximation for frame-based timing
        fixation_cross.draw()
        win.flip()
    triggering.send_state_change(trigger_port, config.TRIG_RESET)

    # --- Stimulus Routine ---
    current_temp = temp_order[current_loop_index]
    current_surface = surface_order[current_loop_index]
    current_rates = ramp_rates[current_temp]
    
    # Setup and trigger thermode
    dur_ms = int((config.RAMP_UP_SECS_CONST + config.STIM_HOLD_DURATION_SECS) * 1000)
    thermode.set_stim(target=current_temp, rise_rate=current_rates['rise'], return_rate=current_rates['return'], dur_ms=dur_ms, surfaces=[current_surface])
    core.wait(0.05)
    thermode.trigger()
    
    # Send STIM_ON trigger and wait for stimulus duration
    win.callOnFlip(triggering.send_state_change, trigger_port, config.TRIG_STIM_ON)
    stim_duration = config.RAMP_UP_SECS_CONST + config.STIM_HOLD_DURATION_SECS + config.RAMP_DOWN_SECS_CONST
    for _ in range(int(stim_duration * 60)):
        fixation_cross.draw()
        win.flip()

    # Send STIM_OFF pulse (event marker + state reset)
    triggering.send_event_pulse(trigger_port, config.TRIG_STIM_OFF, config.TRIG_RESET)
    
    # --- Pain Question Routine ---
    # (Implementation would go here, returning 0 or 1. Simplified for brevity)
    pain_response = 1 # Placeholder

    # --- VAS Routine ---
    # (Full implementation would go here, returning final rating and traces. Simplified for brevity)
    final_vas_rating = 50.0 # Placeholder
    vas_trace_coded = [10, 20, 50] # Placeholder
    vas_time_trace = [0.5, 1.2, 2.5] # Placeholder
    
    # --- Collect Data for this Trial ---
    exp_data['trial_number'].append(current_loop_index + 1)
    exp_data['stimulus_temp'].append(current_temp)
    exp_data['selected_surface'].append(current_surface)
    exp_data['pain_binary_coded'].append(pain_response)
    exp_data['vas_final_coded_rating'].append(final_vas_rating)
    exp_data['vas_traces'].append(vas_trace_coded)
    exp_data['vas_times'].append(vas_time_trace)

    thisExp.nextEntry()

# =================================================================
# 3. END EXPERIMENT & SAVE DATA
# =================================================================

# --- Stop EEG & Close Hardware ---
if rcs:
    try:
        rcs.stopRecording()
        core.wait(1.0)
        rcs.close()
        print("EEG recording stopped and RCS connection closed.")
    except Exception as e:
        print(f"EEG stop/close error: {e}")

if trigger_port and trigger_port.is_open:
    triggering.send_state_change(trigger_port, config.TRIG_RESET)
    trigger_port.close()
    print("Trigger port closed.")

# --- Save All Collected Data ---
dm.save_all_data(exp_info, exp_name, exp_data, _thisDir)

# --- Clean Up ---
win.close()
core.quit()