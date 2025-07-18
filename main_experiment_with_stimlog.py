"""Main experiment variant that logs and plots thermode temperature traces."""

import os
import numpy as np
import logging
import matplotlib.pyplot as plt
from psychopy import core, visual, event, gui, data, logging as psy_logging
from psychopy.hardware import keyboard

import config
import hardware_setup as hw
import triggering
import experiment_logic as logic
import data_management as dm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RUN_LISTS_PATH = os.path.join(os.path.dirname(__file__), "trial_lists.json")


# =================================================================
# 1. SETUP & INITIALIZATION
# =================================================================

exp_info = {
    "participant": "sub0000",
    "date": data.getDateStr(),
    "com_thermode": "COM15",
    "com_trigger": "COM17",
    "eeg_ip": "192.168.1.2",
    "eeg_workspace": "C:\\Users\\labmp-eeg\\Desktop\\workspace\\workspace.rwksp",
    "run_number": "1",
}

dlg = gui.DlgFromDict(dictionary=exp_info, title="Thermal Pain Experiment")
if not dlg.OK:
    core.quit()

try:
    run_number = int(exp_info.get("run_number", 1))
except Exception:
    core.quit()
if run_number not in {1, 2, 3, 4, 5}:
    core.quit()
exp_info["run_number"] = str(run_number)

run_lists = logic.get_or_create_run_trial_lists(
    RUN_LISTS_PATH, config.POSSIBLE_THERMODE_TEMPS, config.AVAILABLE_SURFACES
)
run_pairs = run_lists[run_number - 1]
temp_order = [p[0] for p in run_pairs]
surface_order = [p[1] for p in run_pairs]

exp_name = f"ThermalPainEEGFMRI_run{run_number}"
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Directory for outputs
participant_dir = os.path.join(_thisDir, "data", exp_info["participant"])
os.makedirs(participant_dir, exist_ok=True)
base_filename = f"{exp_info['participant']}_{exp_name}_{exp_info['date']}"

# --- Initialize Hardware ---
thermode = hw.initialize_thermode(
    exp_info["com_thermode"], config.BASELINE_TEMP
)
trigger_port = hw.initialize_trigger_port(exp_info["com_trigger"])
rcs = hw.initialize_eeg_rcs(
    host_ip=exp_info["eeg_ip"],
    workspace_path=exp_info["eeg_workspace"],
    participant=f"{exp_info['participant']}_{exp_info['date']}",
    exp_name=exp_name,
)

if thermode is None or trigger_port is None:
    logger.error("Critical hardware failed to initialize. Exiting.")
    core.quit()

# --- Prepare Experiment Sequences & Values ---
ramp_rates = logic.precalculate_ramp_rates(
    config.POSSIBLE_THERMODE_TEMPS,
    config.BASELINE_TEMP,
    config.RAMP_UP_SECS_CONST,
    config.RAMP_DOWN_SECS_CONST,
    config.MIN_RATE_CONST,
)
num_trials = len(temp_order)

# --- Setup PsychoPy Window & Keyboard ---
win = visual.Window(
    size=(1920, 1080),
    fullscr=True,
    screen=0,
    winType="pyglet",
    allowGUI=False,
    color="black",
    units="height",
)
win.mouseVisible = False
kb = keyboard.Keyboard()
event.clearEvents()
fixation_cross = visual.TextStim(win, text="+", height=0.1, color="white")
pain_question_stim = visual.TextStim(
    win, text="Était-ce douloureux? (o/n)", height=0.07, color="white"
)

# --- Prepare Data Collection ---
exp_data_collector = dm.create_data_collector()
thisExp = data.ExperimentHandler(
    name=exp_name,
    version="",
    extraInfo=exp_info,
    runtimeInfo=None,
    originPath="main_experiment_with_stimlog.py",
    savePickle=True,
    saveWideText=True,
    dataFileName=os.path.join(
        _thisDir,
        "data",
        exp_info["participant"],
        f"{exp_info['participant']}_{exp_name}_{exp_info['date']}",
    ),
)


# =================================================================
# 2. START EXPERIMENT
# =================================================================

if rcs:
    try:
        logger.info("Commanding EEG to start recording...")
        rcs.startRecording()
        thisExp.addData("eeg_rec_command_sent_time", core.monotonicClock.getTime())
        triggering.send_event_pulse(
            trigger_port, config.TRIG_EEG_REC_START, config.TRIG_RESET
        )
        logger.debug("Sent %s pulse for EEG Start.", config.TRIG_EEG_REC_START.hex())
    except Exception as e:
        logger.error("EEG start recording error: %s", e)
        thisExp.addData("eeg_recording_status", f"failed_rcs_error: {e}")
else:
    thisExp.addData("eeg_recording_status", "skipped_rcs_not_available")


# --- Welcome Routine ---
welcome_text = (
    "Merci de participer \u00e0 cette \u00e9tude.\n\n"
    "Vous recevrez des stimulations thermiques (chaleur, parfois douloureuse) sur l\u2019avant-bras, r\u00e9parties sur plusieurs essais. Chaque essai commencera par une croix de fixation \u00e0 regarder. Ensuite, une chaleur sera appliqu\u00e9e. Apr\u00e8s chaque stimulation, vous devrez indiquer si vous avez ressenti de la douleur en appuyant sur O (Oui) ou N (Non). Ensuite, vous \u00e9valuerez l\u2019intensit\u00e9 de la chaleur (si vous n\u2019avez pas eu mal) ou de la douleur (si vous en avez eu), en d\u00e9pla\u00e7ant un curseur avec les touches 2 (gauche) et 3 (droite), puis en confirmant avec la touche 1.\n\n"
    "Veuillez rester immobile, vous concentrer sur vos sensations et r\u00e9pondre honn\u00eatement. L\u2019exp\u00e9rience peut \u00eatre arr\u00eat\u00e9e en tout temps, seulement si n\u00e9cessaire. Avez-vous des questions avant de commencer ?"
)

welcome_stim = visual.TextStim(
    win, text=welcome_text, font="Arial", height=0.04, wrapWidth=1.2, color="white"
)

continue_routine = True
while continue_routine:
    welcome_stim.draw()
    win.flip()
    keys = event.getKeys(keyList=["1", "escape"])
    if "escape" in keys:
        core.quit()
    if "1" in keys:
        continue_routine = False


# --- Main Experiment Loop ---
main_loop = data.TrialHandler(
    nReps=1,
    method="sequential",
    originPath=-1,
    trialList=[{"idx": i} for i in range(num_trials)],
    name="trials_loop",
)
thisExp.addLoop(main_loop)

for this_trial in main_loop:
    current_loop_index = this_trial["idx"]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # ITI Routine
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    iti_duration = np.random.uniform(*config.ITI_DURATION_RANGE)
    thisExp.addData("iti_intended_duration", round(iti_duration, 2))

    iti_start_time = core.monotonicClock.getTime()
    thisExp.addData("iti_start_time", iti_start_time)

    iti_timer = core.CountdownTimer(iti_duration)

    def trigger_iti_onset():
        if trigger_port and trigger_port.is_open:
            trigger_port.write(config.TRIG_ITI_START)

    win.callOnFlip(trigger_iti_onset)
    while iti_timer.getTime() > 0:
        fixation_cross.draw()
        win.flip()
        keys = event.getKeys(keyList=["1", "escape"])
        if "escape" in keys:
            core.quit()
        if "1" in keys:
            break

    iti_end_time = core.monotonicClock.getTime()
    thisExp.addData("iti_end_time", iti_end_time)
    thisExp.addData("iti_actual_duration", round(iti_end_time - iti_start_time, 4))
    if trigger_port and trigger_port.is_open:
        trigger_port.write(config.TRIG_RESET)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Stimulus Routine with temperature logging
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    current_temp = temp_order[current_loop_index]
    current_surface = surface_order[current_loop_index]
    current_rates = ramp_rates[current_temp]

    dur_ms = int((config.RAMP_UP_SECS_CONST + config.STIM_HOLD_DURATION_SECS) * 1000)

    thermode.set_stim(
        target=current_temp,
        rise_rate=current_rates["rise"],
        return_rate=current_rates["return"],
        dur_ms=dur_ms,
        surfaces=[current_surface],
    )

    stim_duration = (
        config.RAMP_UP_SECS_CONST
        + config.STIM_HOLD_DURATION_SECS
        + config.RAMP_DOWN_SECS_CONST
    )

    stim_timer = core.CountdownTimer(stim_duration)

    stim_onset_time = {"t": None}
    temp_samples = []
    temp_sample_times = []
    temp_clock = core.Clock()

    def trigger_and_log_stim_onset():
        thermode.trigger()
        stim_onset_time["t"] = core.monotonicClock.getTime()
        temp_clock.reset()
        if trigger_port and trigger_port.is_open:
            trigger_port.write(config.TRIG_STIM_ON)

    win.callOnFlip(trigger_and_log_stim_onset)
    while stim_timer.getTime() > 0:
        thermode.port.write(b"E")
        out = thermode.port.readline().decode().strip()
        if out:
            temp_samples.append(out)
            temp_sample_times.append(temp_clock.getTime())
        fixation_cross.draw()
        win.flip()
        if event.getKeys(keyList=["escape"]):
            core.quit()

    if trigger_port and trigger_port.is_open:
        trigger_port.write(config.TRIG_RESET)

    stim_reset_time = core.monotonicClock.getTime()
    thisExp.addData("stim_offset_trigger_time", stim_reset_time)
    thisExp.addData(
        "stim_actual_duration_from_triggers",
        round(stim_reset_time - stim_onset_time["t"], 4),
    )
    thisExp.addData("stim_onset_trigger_time", stim_onset_time["t"])

    stim_end_time = core.monotonicClock.getTime()
    stim_start_time = stim_onset_time["t"]
    thisExp.addData("stim_start_time", stim_start_time)
    thisExp.addData("stim_end_time", stim_end_time)
    thisExp.addData("stim_routine_actual_duration", round(stim_end_time - stim_start_time, 4))

    # Parse temperature samples and plot
    try:
        temp_array = (
            np.asarray([s.split("+") for s in temp_samples], dtype=float) / 10.0
            if temp_samples
            else np.empty((0, 6))
        )
    except Exception as e:
        logger.error("Temperature parsing error: %s", e)
        temp_array = np.empty((0, 6))

    if temp_array.size:
        fig = plt.figure()
        labels = ["Neutral", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5"]
        styles = ["--", "-.", ":", "-", "-", "-"]
        for idx in range(min(temp_array.shape[1], 6)):
            plt.plot(
                temp_sample_times[: len(temp_array)],
                temp_array[:, idx],
                label=labels[idx],
                linestyle=styles[idx],
            )
        plt.axhline(current_temp, label="target", linestyle="--", color="red")
        plt.axhline(
            config.BASELINE_TEMP, label="baseline", linestyle="--", color="green"
        )
        plt.xlabel("Time (s)")
        plt.ylabel("Temperature (°C)")
        plt.legend()
        plt.tight_layout()
        plot_path = os.path.join(
            participant_dir,
            f"{base_filename}_trial{current_loop_index + 1}_TempPlot.png",
        )
        plt.savefig(plot_path)
        plt.close(fig)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # Pain Question Routine
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    pain_q_start_time = core.monotonicClock.getTime()
    thisExp.addData("pain_q_start_time", pain_q_start_time)

    painKey = keyboard.Keyboard()
    painKey.clearEvents()

    def trigger_pain_q_onset():
        if trigger_port and trigger_port.is_open:
            trigger_port.write(config.TRIG_PAIN_Q_ON)

    win.callOnFlip(trigger_pain_q_onset)
    continue_routine = True
    while continue_routine:
        pain_question_stim.draw()
        win.flip()
        keys = painKey.getKeys(keyList=["o", "n", "escape"], waitRelease=False)
        if keys:
            if "escape" in [k.name for k in keys]:
                core.quit()
            painKey.keys = keys[-1].name
            continue_routine = False

    pain_response = -1
    if painKey.keys == "o":
        pain_response = 1
    elif painKey.keys == "n":
        pain_response = 0
    thisExp.addData("pain_question_response_coded", pain_response)

    pain_q_end_time = core.monotonicClock.getTime()
    thisExp.addData("pain_q_end_time", pain_q_end_time)
    thisExp.addData("pain_q_actual_duration", round(pain_q_end_time - pain_q_start_time, 4))
    if trigger_port and trigger_port.is_open:
        trigger_port.write(config.TRIG_RESET)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # VAS Routine
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    vas_rating_trace, vas_time_trace = [], []
    current_pos = round(np.random.uniform(0, 100), 1)
    initial_pos = current_pos
    interaction_occurred = False
    vas_timer = core.Clock()
    last_sample_time = 0.0

    context_is_painful = True if pain_response == 1 else False
    if context_is_painful:
        instr_txt, left_txt, right_txt = (
            "Évaluez l'intensité de la DOULEUR :",
            "aucune douleur",
            "pire douleur\nimaginable",
        )
    else:
        instr_txt, left_txt, right_txt = (
            "Évaluez l'intensité de la CHALEUR :",
            "aucune sensation",
            "chaleur très intense\nmais non douloureuse",
        )
    thisExp.addData(
        "vas_context_presented", "painful" if context_is_painful else "nonpainful"
    )

    scale = visual.Line(
        win, start=(-0.5, 0), end=(0.5, 0), lineColor="white", lineWidth=3
    )
    marker = visual.Rect(win, width=0.01, height=0.08, fillColor="red", lineColor="red")
    instr = visual.TextStim(win, text=instr_txt, pos=(0, 0.2), height=0.05)
    anchor_L = visual.TextStim(
        win, text=left_txt, pos=(-0.5, -0.06), height=0.035, anchorHoriz="center"
    )
    anchor_R = visual.TextStim(
        win, text=right_txt, pos=(0.5, -0.06), height=0.035, anchorHoriz="center"
    )

    kb = keyboard.Keyboard()
    kb.clearEvents()
    event.clearEvents(eventType="keyboard")

    def trigger_vas_onset():
        if trigger_port and trigger_port.is_open:
            trigger_port.write(config.TRIG_VAS_ON)

    win.callOnFlip(trigger_vas_onset)
    vas_start_time = core.monotonicClock.getTime()

    frame_dur = (
        win.monitorFramePeriod if getattr(win, "monitorFramePeriod", None) else 1 / 60.0
    )

    continue_routine = True
    waiting_for_release = False

    while continue_routine:
        increment = config.VAS_SPEED_UNITS_PER_SEC * frame_dur

        keys = kb.getKeys(["3", "2", "1", "s", "escape"], waitRelease=False, clear=False)

        move_keys = [k for k in keys if k.name in ["3", "2"]]
        if move_keys and move_keys[-1].duration is None:
            key = move_keys[-1].name
            if key == "3":
                current_pos = min(100.0, current_pos + increment)
                interaction_occurred = True
            elif key == "2":
                current_pos = max(0.0, current_pos - increment)
                interaction_occurred = True

        action_names = {k.name for k in keys}
        if "escape" in action_names:
            core.quit()
        if "s" in action_names:
            main_loop.finished = True
            continue_routine = False

        confirm_pressed = "1" in action_names
        move_held = any(k.name in ["3", "2"] and k.duration is None for k in keys)
        at_boundary = current_pos <= 0.0 or current_pos >= 100.0

        if confirm_pressed and not move_held:
            continue_routine = False

        marker_x = -0.5 + (current_pos / 100.0)
        marker.setPos((marker_x, 0))

        scale.draw()
        marker.draw()
        instr.draw()
        anchor_L.draw()
        anchor_R.draw()
        win.flip()

        elapsed_time = vas_timer.getTime()
        if elapsed_time - last_sample_time >= config.VAS_SAMPLING_INTERVAL_SECS:
            vas_rating_trace.append(current_pos)
            vas_time_trace.append(elapsed_time)
            last_sample_time = elapsed_time

        if elapsed_time >= config.VAS_MAX_DURATION_SECS:
            if move_held and at_boundary:
                waiting_for_release = True
            else:
                continue_routine = False

        if waiting_for_release and not move_held:
            continue_routine = False

    final_rating_raw = current_pos
    vas_rating_trace.append(final_rating_raw)
    vas_time_trace.append(vas_timer.getTime())

    final_rating_coded = final_rating_raw
    vas_trace_coded = list(vas_rating_trace)
    if context_is_painful:
        final_rating_coded += 100.0
        vas_trace_coded = [r + 100.0 for r in vas_trace_coded]
    else:
        final_rating_coded = min(final_rating_raw, 99.0)
        vas_trace_coded = [min(r, 99.0) for r in vas_trace_coded]

    thisExp.addData("vas_final_coded_rating", round(final_rating_coded, 2))
    thisExp.addData("vas_interaction_occurred", int(interaction_occurred))
    thisExp.addData("vas_initial_position", round(initial_pos, 2))

    vas_end_time = core.monotonicClock.getTime()
    thisExp.addData("vas_end_time", vas_end_time)
    thisExp.addData("vas_actual_duration", round(vas_end_time - vas_start_time, 4))
    if trigger_port and trigger_port.is_open:
        trigger_port.write(config.TRIG_RESET)

    # --- Append data to collector for final saving ---
    exp_data_collector["trial_number"].append(current_loop_index + 1)
    exp_data_collector["stimulus_temp"].append(current_temp)
    exp_data_collector["selected_surface"].append(current_surface)
    exp_data_collector["pain_binary_coded"].append(pain_response)
    exp_data_collector["vas_final_coded_rating"].append(round(final_rating_coded, 2))
    exp_data_collector["vas_traces"].append(vas_trace_coded)
    exp_data_collector["vas_times"].append(vas_time_trace)
    exp_data_collector["iti_start_time"].append(iti_start_time)
    exp_data_collector["iti_end_time"].append(iti_end_time)
    exp_data_collector["stim_start_time"].append(stim_start_time)
    exp_data_collector["stim_end_time"].append(stim_end_time)
    exp_data_collector["pain_q_start_time"].append(pain_q_start_time)
    exp_data_collector["pain_q_end_time"].append(pain_q_end_time)
    exp_data_collector["vas_start_time"].append(vas_start_time)
    exp_data_collector["vas_end_time"].append(vas_end_time)
    exp_data_collector["temperature_traces"].append(temp_array.tolist())
    exp_data_collector["temperature_times"].append(temp_sample_times)

    thisExp.nextEntry()


# =================================================================
# 3. END EXPERIMENT & SAVE DATA
# =================================================================

if rcs:
    try:
        rcs.stopRecording()
        core.wait(1.0)
        rcs.close()
        logger.info("EEG recording stopped and RCS connection closed.")
    except Exception as e:
        logger.error("EEG stop/close error: %s", e)

if trigger_port and trigger_port.is_open:
    trigger_port.write(config.TRIG_RESET)
    trigger_port.close()
    logger.info("Trigger port closed.")

dm.save_all_data(exp_info, exp_name, exp_data_collector, _thisDir)

end_msg = visual.TextStim(
    win, text="Merci! L'exp\u00e9rience est termin\u00e9e.", height=0.07, color="white"
)
end_timer = core.CountdownTimer(5.0)
while end_timer.getTime() > 0:
    end_msg.draw()
    win.flip()
    if event.getKeys(keyList=["escape"]):
        core.quit()

win.close()
core.quit()

