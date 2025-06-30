import os
import logging
from psychopy import core, visual, event, gui, data

import config
import hardware_setup as hw
import triggering

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
    "eeg_workspace": "C:\\Users\\labmp-eeg\\Desktop\\workspace\\workspace.rwksp"  # Change this path
}

dlg = gui.DlgFromDict(dictionary=exp_info, title="5-Min Baseline EEG")
if not dlg.OK:
    core.quit()

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
if rcs:
    try:
        logger.info("Commanding EEG to start recording...")
        rcs.startRecording()
        triggering.send_event_pulse(trigger_port, config.TRIG_EEG_REC_START, config.TRIG_RESET)
    except Exception as e:
        logger.error("EEG start recording error: %s", e)
else:
    logger.warning("EEG RCS unavailable; recording must be started manually.")

# -----------------------------------------------------------------
# 5. Baseline Period
# -----------------------------------------------------------------
baseline_timer = core.CountdownTimer(300.0)  # 5 minutes
while baseline_timer.getTime() > 0:
    fixation_cross.draw()
    win.flip()
    if event.getKeys(keyList=["escape"]):
        break

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
    trigger_port.write(config.TRIG_RESET)
    trigger_port.close()

win.close()
core.quit()
