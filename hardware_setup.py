# hardware_setup.py

import serial
from psychopy import core
from pytcsii import tcsii_serial
from psychopy.hardware import brainproducts

# Import trigger definitions from your config file
from config import TRIG_RESET

def initialize_thermode(port_name, baseline_temp):
    """Initialize the thermode device and set its baseline temperature."""
    print(f"Initializing Thermode on {port_name}...")
    try:
        thermode = tcsii_serial(port_name, beep=True)
        thermode.set_baseline(baseline_temp)
        print(f"SUCCESS: Thermode initialized on {port_name} with baseline {baseline_temp}°C.")
        return thermode
    except Exception as e:
        print(f"FATAL ERROR: Thermode initialization failed on {port_name}: {e}")
        return None

def initialize_trigger_port(port_address, baudrate=2000000):
    """Open the serial port for triggers and send an initial reset."""
    print(f"Initializing Trigger port {port_address}...")
    try:
        port = serial.Serial(port_address, baudrate=baudrate)
        core.wait(0.1)  # Allow port to open
        port.write(TRIG_RESET) # Initial reset
        print(f"SUCCESS: Trigger port {port_address} initialized and reset.")
        return port
    except Exception as e:
        print(f"FATAL ERROR: Trigger port {port_address} initialization failed: {e}")
        return None

def initialize_eeg_rcs(host_ip, workspace_path, participant, exp_name):
    """Initialize the BrainProducts Remote Control Server connection.

    The function opens the recorder, sets the workspace, participant and
    experiment name, and puts the server in monitor mode.
    """
    print(f"Initializing EEG Remote Control Server at {host_ip}...")
    try:
        rcs = brainproducts.RemoteControlServer(host=host_ip, timeout=10)
        rcs.openRecorder()
        core.wait(1.0)
        rcs.workspace = workspace_path
        rcs.participant = participant
        rcs.expName = exp_name
        rcs.mode = 'monitor'
        core.wait(0.5)
        print(f"SUCCESS: EEG RCS initialized. Workspace: {rcs.workspace}, Participant: {rcs.participant}")
        return rcs
    except Exception as e:
        print(f"WARNING: EEG RCS initialization failed: {e}. Experiment continues without EEG control.")
        return None