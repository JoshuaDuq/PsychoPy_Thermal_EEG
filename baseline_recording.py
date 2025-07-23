import os
import csv
import logging
from psychopy import core, visual, event, gui, data

import config
import hardware_setup as hw
import triggering

# --- Baseline Trigger Codes (hex) ---
TRIG_RESET = b"\x00"             # all lines low
TRIG_EEG_REC_START = b"\x01"     # baseline EEG recording start
TRIG_BASELINE_START = b"\x02"    # baseline period onset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# 1. Participant/Session Info
# -----------------------------------------------------------------
exp_info = {
    "participant": "sub0000",
    "date": data.getDateStr(),
    "com_trigger": "COM17",
    "eeg_ip": "192.168.1.2",
    "eeg_workspace": "C:\\Users\\labmp\\Desktop\\EEG_FMRI-2025.rwksp"  # Change this path
}

dlg = gui.DlgFromDict(dictionary=exp_info, title="5-Min Baseline EEG")
if not dlg.OK:
    core.quit()

_thisDir = os.path.dirname(os.path.abspath(__file__))
participant_dir = os.path.join(_thisDir, "data", exp_info["participant"])
os.makedirs(participant_dir, exist_ok=True)
csv_path = os.path.join(
    participant_dir,
    f"{exp_info['participant']}_BaselineEEG_{exp_info['date']}_Summary.csv",
)

# -----------------------------------------------------------------
# 2. Initialize Hardware
# -----------------------------------------------------------------
trigger_port = hw.initialize_trigger_port(exp_info["com_trigger"])
rcs = hw.initialize_eeg_rcs(
    host_ip=exp_info["eeg_ip"],
    workspace_path=exp_info["eeg_workspace"],
    participant=f"{exp_info['participant']}_{exp_info['date']}",
    exp_name="BaselineEEG"
)

if trigger_port is None:
    logger.error("Trigger port failed to open. Exiting.")
    core.quit()

# -----------------------------------------------------------------
# 3. Setup PsychoPy Window
# -----------------------------------------------------------------
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
fixation_cross = visual.TextStim(win, text="+", height=0.1, color="white")

# -----------------------------------------------------------------
# 4. Start EEG Recording
# -----------------------------------------------------------------
rcs_start_status = "skipped_rcs_not_available"
eeg_rec_command_time = None
if rcs:
    try:
        logger.info("Commanding EEG to start recording...")
        rcs.startRecording()
        eeg_rec_command_time = core.monotonicClock.getTime()
        triggering.send_event_pulse(trigger_port, TRIG_EEG_REC_START, TRIG_RESET)
        rcs_start_status = "success"
    except Exception as e:
        logger.error("EEG start recording error: %s", e)
        rcs_start_status = f"failed: {e}"
else:
    logger.warning("EEG RCS unavailable; recording must be started manually.")


# --- Wait for MRI Initialization ---
scanner_wait_start = core.monotonicClock.getTime()
thisExp.addData("scanner_wait_start_time", scanner_wait_start)

scanner_text = "En attente de l'IRM. Merci de patienter."
scanner_stim = visual.TextStim(
    win, text=scanner_text, font="Arial", height=0.04, wrapWidth=1.2, color="white"
)
press_count = 0
event.clearEvents()
continue_wait = True
while continue_wait:
    scanner_stim.draw()
    win.flip()
    keys = event.getKeys(keyList=["5", "escape"])
    if "escape" in keys:
        core.quit()
    press_count += keys.count("5")
    if press_count >= 5:
        continue_wait = False

scanner_wait_end = core.monotonicClock.getTime()
thisExp.addData("scanner_wait_end_time", scanner_wait_end)
thisExp.addData("scanner_wait_presses", press_count)
thisExp.addData(
    "scanner_wait_duration", round(scanner_wait_end - scanner_wait_start, 4)
)

# -----------------------------------------------------------------
# 5. Baseline Period
# -----------------------------------------------------------------
baseline_start_time = {"t": None}
baseline_timer = core.CountdownTimer(300.0)  # 5 minutes

def mark_baseline_start():
    baseline_start_time["t"] = core.monotonicClock.getTime()
    if trigger_port and trigger_port.is_open:
        trigger_port.write(TRIG_BASELINE_START)
    else:
        print(f"SKIPPED trigger {TRIG_BASELINE_START.hex()} (port not available/open).")

win.callOnFlip(mark_baseline_start)
while baseline_timer.getTime() > 0:
    fixation_cross.draw()
    win.flip()
    if event.getKeys(keyList=["escape"]):
        break
baseline_end_time = core.monotonicClock.getTime()
if trigger_port and trigger_port.is_open:
    trigger_port.write(TRIG_RESET)
else:
    print(f"SKIPPED reset after baseline (port not available/open).")

# -----------------------------------------------------------------
# 6. Stop EEG and Clean Up
# -----------------------------------------------------------------
if rcs:
    try:
        rcs.stopRecording()
        core.wait(1.0)
        rcs.close()
    except Exception as e:
        logger.error("EEG stop/close error: %s", e)

if trigger_port and trigger_port.is_open:
    trigger_port.write(TRIG_RESET)
    trigger_port.close()

# --- Save Baseline Session Summary ---
log_data = {
    "participant": exp_info["participant"],
    "date": exp_info["date"],
    "rcs_initialized": bool(rcs),
    "rcs_start_status": rcs_start_status,
    "eeg_rec_command_time": eeg_rec_command_time,
    "baseline_start_time": baseline_start_time["t"],
    "baseline_end_time": baseline_end_time,
    "duration_secs": round(
        baseline_end_time - baseline_start_time["t"], 4
    )
    if baseline_start_time["t"] is not None
    else None,
}
try:
    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=log_data.keys())
        writer.writeheader()
        writer.writerow(log_data)
    logger.info("Baseline summary saved to %s", csv_path)
except Exception as e:
    logger.error("ERROR saving baseline summary: %s", e)

win.close()
core.quit()
