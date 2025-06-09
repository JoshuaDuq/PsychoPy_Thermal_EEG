# main_experiment.py

import os
import numpy as np
import pandas as pd
from psychopy import core, visual, event, gui, data, logging
from psychopy.hardware import keyboard

# --- Import Modularized Code ---
# It's assumed that config.py, hardware_setup.py, triggering.py,
# experiment_logic.py, and data_management.py are in the same directory.
import config
import hardware_setup as hw
import triggering
import experiment_logic as logic
import data_management as dm

# =================================================================
# 1. SETUP & INITIALIZATION
# =================================================================

# --- Get Experiment Info from User ---
exp_info = {
    'participant': 'test01',
    'date': data.getDateStr(),
    'com_thermode': 'COM4',
    'com_trigger': 'COM5',
    'eeg_ip': '192.168.1.2',
    'eeg_workspace': 'C:/BVA/workspaces/default.rwksp' # IMPORTANT: Change this path
}
dlg = gui.DlgFromDict(dictionary=exp_info, title='Thermal Pain Experiment')
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
    workspace_path=exp_info['eeg_workspace'],
    participant=f"{exp_info['participant']}_{exp_info['date']}",
    exp_name=exp_name
)

# Graceful exit if critical hardware fails
if thermode is None or trigger_port is None:
    print("Critical hardware failed to initialize. Exiting.")
    core.quit()

# --- Prepare Experiment Sequences & Values ---
temp_order = logic.generate_temperature_order(config.POSSIBLE_THERMODE_TEMPS, config.NUM_REPEATS_PER_TEMP)
surface_order = logic.generate_surface_order(temp_order, config.AVAILABLE_SURFACES, config.MAX_TEMP_VALUE)
ramp_rates = logic.precalculate_ramp_rates(
    config.POSSIBLE_THERMODE_TEMPS, config.BASELINE_TEMP,
    config.RAMP_UP_SECS_CONST, config.RAMP_DOWN_SECS_CONST, config.MIN_RATE_CONST
)
num_trials = len(temp_order)

# --- Setup PsychoPy Window & Keyboard ---
win = visual.Window(size=(1920, 1080), fullscr=True, screen=0, winType='pyglet',
                    allowGUI=False, color='black', units='height')
win.mouseVisible = False
kb = keyboard.Keyboard()
event.clearEvents()

# --- Prepare Data Collection ---
exp_data_collector = dm.create_data_collector()
thisExp = data.ExperimentHandler(name=exp_name, version='',
                                extraInfo=exp_info, runtimeInfo=None,
                                originPath='main_experiment.py',
                                savePickle=True, saveWideText=True,
                                dataFileName=os.path.join(_thisDir, 'data', exp_info['participant'], f"{exp_info['participant']}_{exp_name}_{exp_info['date']}"))


# =================================================================
# 2. START EXPERIMENT
# =================================================================

# --- Start EEG Recording ---
if rcs:
    try:
        print("Commanding EEG to start recording...")
        rcs.startRecording()
        thisExp.addData('eeg_rec_command_sent_time', core.monotonicClock.getTime())
        triggering.send_event_pulse(trigger_port, config.TRIG_EEG_REC_START, config.TRIG_RESET)
        print(f"Sent {config.TRIG_EEG_REC_START.hex()} pulse for EEG Start.")
    except Exception as e:
        print(f"EEG start recording error: {e}")
        thisExp.addData('eeg_recording_status', f'failed_rcs_error: {e}')
else:
    thisExp.addData('eeg_recording_status', 'skipped_rcs_not_available')
    
# --- Main Experiment Loop ---
main_loop = data.TrialHandler(
    nReps=1,
    method='sequential',
    originPath=-1,
    trialList=[{'idx': i} for i in range(num_trials)],
    name='trials_loop'
)
thisExp.addLoop(main_loop)

for this_trial in main_loop:
    current_loop_index = this_trial['idx']
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # ITI Routine
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    iti_duration = np.random.uniform(*config.ITI_DURATION_RANGE)
    thisExp.addData('iti_intended_duration', round(iti_duration, 2))
    
    win.callOnFlip(triggering.send_state_change, trigger_port, config.TRIG_ITI_START)
    print(f"ITI routine started. TRIG_ITI_START ({config.TRIG_ITI_START.hex()}) SET ON (queued).")

    fixation_cross = visual.TextStim(win, text='+', height=0.1, color='white')
    iti_timer = core.CountdownTimer(iti_duration)
    while iti_timer.getTime() > 0:
        fixation_cross.draw()
        win.flip()
        if event.getKeys(keyList=['escape']): core.quit()
        
    triggering.send_state_change(trigger_port, config.TRIG_RESET)
    print(f"ITI ended. Sent TRIG_RESET for {config.TRIG_ITI_START.hex()}.")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Stimulus Routine
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    current_temp = temp_order[current_loop_index]
    current_surface = surface_order[current_loop_index]
    current_rates = ramp_rates[current_temp]
    
    dur_ms = int((config.RAMP_UP_SECS_CONST + config.STIM_HOLD_DURATION_SECS) * 1000)
    
    thermode.set_stim(
        target=current_temp,
        rise_rate=current_rates['rise'],
        return_rate=current_rates['return'],
        dur_ms=dur_ms,
        surfaces=[current_surface]
    )
    thermode.trigger()
    print(f"Trial {current_loop_index+1}: Temp={current_temp}°C, Surface={current_surface}. Thermode triggered.")

    win.callOnFlip(triggering.send_state_change, trigger_port, config.TRIG_STIM_ON)
    stim_onset_trigger_time = win.getFutureFlipTime(clock='ptb')
    thisExp.addData('stim_onset_trigger_time_actual', stim_onset_trigger_time)
    print(f"TRIG_STIM_ON ({config.TRIG_STIM_ON.hex()}) SET ON (queued).")

    stim_duration = config.RAMP_UP_SECS_CONST + config.STIM_HOLD_DURATION_SECS + config.RAMP_DOWN_SECS_CONST
    stim_timer = core.CountdownTimer(stim_duration)
    while stim_timer.getTime() > 0:
        fixation_cross.draw()
        win.flip()
        if event.getKeys(keyList=['escape']): core.quit()

    triggering.send_event_pulse(trigger_port, config.TRIG_STIM_OFF, config.TRIG_RESET)
    stim_offset_trigger_time = core.getTime()
    thisExp.addData('stim_offset_trigger_time', stim_offset_trigger_time)
    print(f"TRIG_STIM_OFF ({config.TRIG_STIM_OFF.hex()}) pulsed and all lines reset.")
    thisExp.addData('stim_actual_duration_from_triggers', round(stim_offset_trigger_time - stim_onset_trigger_time, 4))
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Pain Question Routine
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    win.callOnFlip(triggering.send_state_change, trigger_port, config.TRIG_PAIN_Q_ON)
    print(f"TRIG_PAIN_Q_ON ({config.TRIG_PAIN_Q_ON.hex()}) SET ON (queued).")

    pain_question_stim = visual.TextStim(win, text="Était-ce douloureux? (o/n)", height=0.07, color='white')
    painKey = keyboard.Keyboard()
    painKey.clearEvents()
    
    continue_routine = True
    while continue_routine:
        pain_question_stim.draw()
        win.flip()
        keys = painKey.getKeys(keyList=['o', 'n', 'escape'], waitRelease=False)
        if keys:
            if 'escape' in [k.name for k in keys]: core.quit()
            painKey.keys = keys[-1].name
            continue_routine = False
            
    pain_response = -1
    if painKey.keys == 'o': pain_response = 1
    elif painKey.keys == 'n': pain_response = 0
    thisExp.addData('pain_question_response_coded', pain_response)
    
    triggering.send_state_change(trigger_port, config.TRIG_RESET)
    print(f"Pain question ended. Sent TRIG_RESET for {config.TRIG_PAIN_Q_ON.hex()}.")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # VAS Routine
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Begin Routine
    win.callOnFlip(triggering.send_state_change, trigger_port, config.TRIG_VAS_ON)
    print(f"TRIG_VAS_ON ({config.TRIG_VAS_ON.hex()}) SET ON (queued).")
    
    vas_rating_trace, vas_time_trace = [], []
    current_pos = round(np.random.uniform(0, 100), 1)
    initial_pos = current_pos
    interaction_occurred = False
    vas_timer = core.Clock()
    last_sample_time = 0.0

    context_is_painful = True if pain_response == 1 else False
    if context_is_painful:
        instr_txt, left_txt, right_txt = "Évaluez l'intensité de la DOULEUR :", "aucune douleur", "pire douleur\nimaginable"
    else:
        instr_txt, left_txt, right_txt = "Évaluez l'intensité de la CHALEUR :", "aucune sensation", "chaleur très intense\nmais non douloureuse"
    thisExp.addData('vas_context_presented', 'painful' if context_is_painful else 'nonpainful')
    
    # Create visual elements
    scale = visual.Line(win, start=(-0.5, 0), end=(0.5, 0), lineColor='white', lineWidth=3)
    marker = visual.Rect(win, width=0.01, height=0.08, fillColor='red', lineColor='red')
    instr = visual.TextStim(win, text=instr_txt, pos=(0, 0.2), height=0.05)
    anchor_L = visual.TextStim(win, text=left_txt, pos=(-0.5, -0.06), height=0.035, anchorHoriz='center')
    anchor_R = visual.TextStim(win, text=right_txt, pos=(0.5, -0.06), height=0.035, anchorHoriz='center')
    
    kb.clearEvents()
    event.clearEvents(eventType='keyboard')
    
    # Each Frame Loop
    continue_routine = True
    while continue_routine:
        frame_dur = win.monitorFramePeriod if hasattr(win, 'monitorFramePeriod') and win.monitorFramePeriod else 1/60.0
        increment = config.VAS_SPEED_UNITS_PER_SEC * frame_dur
        
        # Handle movement keys
        keys = kb.getKeys(['m', 'n'], waitRelease=False)
        if keys:
            interaction_occurred = True
            for key in keys:
                if key.name == 'm': current_pos = min(100.0, current_pos + increment)
                if key.name == 'n': current_pos = max(0.0, current_pos - increment)
        
        # Update marker position
        marker_x = -0.5 + (current_pos / 100.0)
        marker.setPos((marker_x, 0))
        
        # Draw all components
        scale.draw(); marker.draw(); instr.draw(); anchor_L.draw(); anchor_R.draw()
        win.flip()
        
        # Sample data
        elapsed_time = vas_timer.getTime()
        if elapsed_time - last_sample_time >= config.VAS_SAMPLING_INTERVAL_SECS:
            vas_rating_trace.append(current_pos)
            vas_time_trace.append(elapsed_time)
            last_sample_time = elapsed_time

        # Check for confirmation or timeout
        action_keys = event.getKeys(keyList=['space', 's', 'escape'])
        if action_keys:
            if 'escape' in action_keys: core.quit()
            if 's' in action_keys:
                main_loop.finished = True # End trials loop
                continue_routine = False
            if 'space' in action_keys:
                continue_routine = False
        
        if elapsed_time >= config.VAS_MAX_DURATION_SECS:
            continue_routine = False

    # End Routine
    final_rating_raw = current_pos
    vas_rating_trace.append(final_rating_raw) # ensure last position is recorded
    vas_time_trace.append(vas_timer.getTime())

    final_rating_coded = final_rating_raw
    vas_trace_coded = list(vas_rating_trace)
    if context_is_painful:
        final_rating_coded += 100.0
        vas_trace_coded = [r + 100.0 for r in vas_trace_coded]
    else:
        final_rating_coded = min(final_rating_raw, 99.0)
        vas_trace_coded = [min(r, 99.0) for r in vas_trace_coded]

    thisExp.addData('vas_final_coded_rating', round(final_rating_coded, 2))
    thisExp.addData('vas_interaction_occurred', int(interaction_occurred))
    thisExp.addData('vas_initial_position', round(initial_pos, 2))

    triggering.send_state_change(trigger_port, config.TRIG_RESET)
    print(f"VAS ended. Sent TRIG_RESET for {config.TRIG_VAS_ON.hex()}.")

    # --- Append data to collector for final saving ---
    exp_data_collector['trial_number'].append(current_loop_index + 1)
    exp_data_collector['stimulus_temp'].append(current_temp)
    exp_data_collector['selected_surface'].append(current_surface)
    exp_data_collector['pain_binary_coded'].append(pain_response)
    exp_data_collector['vas_final_coded_rating'].append(round(final_rating_coded, 2))
    exp_data_collector['vas_traces'].append(vas_trace_coded)
    exp_data_collector['vas_times'].append(vas_time_trace)
    
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

# --- Save All Collected Data from our custom collector ---
dm.save_all_data(exp_info, exp_name, exp_data_collector, _thisDir)

# --- Clean Up PsychoPy ---
win.close()
core.quit()
