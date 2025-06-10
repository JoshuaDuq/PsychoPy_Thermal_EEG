# Thermal Pain EEG/fMRI Experiment

This repository contains the PsychoPy Coder implementation for a thermal pain perception experiment. The experiment delivers calibrated thermal stimuli, records subjective pain ratings, and sends precise time-locking triggers to an EEG system.

## Table of Contents
- [Overview](#overview)
- [Experimental Task](#experimental-task)
- [Trial Flow](#trial-flow)
- [Features](#features)
- [System Requirements](#system-requirements)
  - [Software](#software)
  - [Hardware](#hardware)
- [Setup and Installation](#setup-and-installation)
- [How to Run the Experiment](#how-to-run-the-experiment)
- [Customization](#customization)
- [Data Output](#data-output)
- [Code Structure](#code-structure)

## Overview

The primary goal of this experiment is to investigate the neural correlates of thermal pain perception. On each trial, a participant receives a thermal stimulus of a specific temperature. They are then asked to make a binary judgment on whether the stimulus was painful, followed by a rating of the sensation's intensity on a Visual Analogue Scale (VAS). The experiment is designed with robust hardware integration for precise stimulus delivery and neural data synchronization.

## Experimental Task

Participants are instructed to focus on a fixation cross presented at the center of the screen. They receive a series of thermal stimulations on their forearm. Each stimulation is followed by two questions:

1.  **Pain Judgment:** Participants answer `"Était-ce douloureux? (o/n)"` (Was that painful?) by pressing 'o' for *Oui* (Yes) or 'n' for *Non* (No).
2.  **Intensity Rating:** Participants rate the intensity of the sensation on a Visual Analogue Scale (VAS).
    * If the stimulus was rated **painful**, the scale is labeled `"aucune douleur"` (no pain) and `"pire douleur\nimaginable"` (worst pain imaginable).
    * If the stimulus was rated **not painful**, the scale is labeled `"aucune sensation"` (no sensation) and `"chaleur très intense\nmais non douloureuse"` (very intense but not painful heat).

Participants use the 'n' (left) and 'm' (right) keys to move the VAS slider and press the `space` bar to confirm their rating.

## Trial Flow

The experiment consists of a sequence of trials, each following a precise structure. EEG triggers, defined in `config.py`, are sent at the onset of each key phase.

1.  **Inter-Trial Interval (ITI)**
    * A fixation cross (`+`) is displayed for a random duration between a specified minimum and maximum. The default range is 15-20 seconds.
    * **EEG Trigger:** `TRIG_ITI_START` (`0x02`) is sent at the start of the ITI.

2.  **Thermal Stimulation**
    * A pre-determined temperature is applied via the thermode. The temperature ramps up from a baseline, holds for a fixed duration, and then ramps back down.
    * The participant continues to view the fixation cross.
    * **EEG Trigger:** `TRIG_STIM_ON` (`0x04`) is sent at the moment the thermode begins the temperature ramp-up.

3.  **Pain Question**
    * The question `Était-ce douloureux? (o/n)` is displayed.
    * The experiment waits for a keyboard response ('o' or 'n').
    * **EEG Trigger:** `TRIG_PAIN_Q_ON` (`0x08`) is sent at the onset of the question screen.

4.  **Visual Analogue Scale (VAS) Rating**
    * The VAS is presented with anchors corresponding to the pain judgment.
    * The participant adjusts the slider and confirms their rating.
    * **EEG Trigger:** `TRIG_VAS_ON` (`0x20`) is sent at the onset of the VAS screen.

At the end of each phase, a `TRIG_RESET` (`0x00`) trigger is sent to reset the trigger port lines.

## Features

* **Modular Codebase:** Logic, hardware control, data management, and configuration are separated into distinct Python modules for clarity and maintainability.
* **Hardware Integration:**
    * **TCSII Thermode:** Provides control over a thermode device via the `pytcsii` serial wrapper.
    * **BrainProducts EEG:** Integrates with BrainProducts Remote Control Server (RCS) to start and stop EEG recordings automatically.
    * **Serial Port Triggers:** Sends precise 8-bit hexadecimal triggers for event marking.
* **Advanced Trial Randomization:**
    * Generates a fully randomized sequence of stimulus temperatures.
    * Pre-generates a surface order to balance temperatures across multiple thermode surfaces, with constraints to avoid repeating the last used surface if possible.
* **Comprehensive Data Logging:**
    * Saves a trial-by-trial summary in a `.csv` format.
    * Saves continuous VAS traces in a long-format `.csv` file.
    * Creates a compressed NumPy (`.npz`) backup of all raw data structures.
* **Centralized Configuration:** All key experimental parameters are centralized in `config.py` for easy modification.

## System Requirements

### Software
* **PsychoPy**
* **Python 3.x**
* **Required Python Libraries:**
    * `pandas`
    * `numpy`
    * `pyserial`
    * `psychopy`

### Hardware
* **Thermal Stimulator:** A TCSII-compatible thermode.
* **EEG System:** BrainProducts EEG system with Remote Control Server (RCS) enabled.
* **Triggering Device:** A device that accepts triggers via a serial port.
* **Display** and **Keyboard** for stimulus presentation and response.

## Setup and Installation

1.  **Clone or download the repository.**
2.  **Install required Python libraries** (e.g., `pip install pandas numpy pyserial psychopy`).
3.  **Connect Hardware:**
    * Connect the thermode and triggering device to the computer and identify their COM ports.
    * Ensure the PsychoPy computer is on the same network as the BrainProducts RCS.
4.  **Configure Paths:**
    * Open `main_experiment.py`.
    * Locate the `exp_info` dictionary.
    * **Update the `'eeg_workspace'` path** to match the full path of the `.rwksp` workspace file on your EEG recording computer.

## How to Run the Experiment

1.  Ensure all hardware is connected and powered on.
2.  Start the BrainVision Recorder software and enable the Remote Control Server.
3.  Run the main script from PsychoPy Coder or a terminal: `python main_experiment.py`.
4.  A dialog box will appear. Fill in the following information:
    * `participant`: The participant ID (default: `sub0000`).
    * `com_thermode`: The COM port for the thermode (default: `COM15`).
    * `com_trigger`: The COM port for the trigger device (default: `COM17`).
    * `eeg_ip`: The IP address of the EEG recording computer (default: `192.168.1.2`).
    * `eeg_workspace`: Verify the path to the EEG workspace file is correct.
5.  Click **OK** to start. The script initializes hardware before beginning the welcome screen.
6.  To quit the experiment at any time, press the `Escape` key.

## Customization

All primary experimental parameters can be modified in the `config.py` file.

| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| `TRIG_*` | Hex codes (e.g., `b'\x01'`) | Hexadecimal codes for each EEG trigger event. |
| `TRIGGER_PULSE_SECS` | `0.002` | Duration in seconds for short trigger pulses, specifically for the EEG recording start trigger. |
| `POSSIBLE_THERMODE_TEMPS` | `[44.3, 45.3, ..., 49.3]` | A list of all stimulus temperatures in °C to be presented. |
| `NUM_REPEATS_PER_TEMP`| `10` | The number of times each temperature is presented. |
| `AVAILABLE_SURFACES` | `[1, 2, 3, 4, 5]` | A list of the thermode surfaces to be used. |
| `BASELINE_TEMP` | `35.0` | The neutral temperature in °C from which stimuli ramp. |
| `RAMP_UP_SECS_CONST` | `3.0` | The fixed duration in seconds for the temperature ramp-up. |
| `RAMP_DOWN_SECS_CONST` | `2.0` | The fixed duration in seconds for the temperature ramp-down. |
| `STIM_HOLD_DURATION_SECS`| `7.5` | The duration in seconds the target temperature is held constant. |
| `ITI_DURATION_RANGE` | `(15, 20)` | The minimum and maximum duration in seconds for the ITI. |
| `VAS_SPEED_UNITS_PER_SEC`| `22.0` | The speed of the VAS slider in scale units per second. |
| `VAS_MAX_DURATION_SECS`| `30.0` | The maximum time allowed for the VAS rating before timeout. |
| `VAS_SAMPLING_INTERVAL_SECS`| `0.2` | The time interval in seconds at which the VAS slider position is sampled. |

## Data Output

Three data files are saved in a directory named `data/<participant_id>/`.

1.  **Trial Summary (`*_TrialSummary.csv`)**
    * This file contains one row per trial with key outcome measures and timestamps.
    * Key columns include `trial_number`, `stimulus_temp`, `selected_surface`, `pain_binary_coded` (1 for painful, 0 for non-painful), `vas_final_coded_rating`, and timestamps for each routine.
    * The VAS rating is coded with an offset of 100 for painful trials.

2.  **VAS Traces (`*_VASTraces_Long.csv`)**
    * This file contains continuous VAS rating data in a long format.
    * Columns include `participant_id`, `trial_number`, `stimulus_temp`, `pain_context_0no_1yes`, `sample_in_trace`, `vas_time_in_trial_secs`, and `vas_coded_rating`.

3.  **Raw Data Backup (`*_BACKUP.npz`)**
    * This is a Numpy compressed archive of the raw data collector dictionary. It serves as a complete backup of all collected data lists, including `vas_traces` and `vas_times`.

## Code Structure

| File | Description |
| :--- | :--- |
| `main_experiment.py` | The main executable script that controls the experiment flow, initializes hardware, presents stimuli, and manages the trial loop. |
| `config.py` | Contains all user-configurable parameters, including triggers, timings, and temperatures. |
| `hardware_setup.py` | Handles the initialization of the thermode, trigger port, and BrainProducts RCS. |
| `experiment_logic.py` | Contains functions for generating the pseudo-randomized temperature and surface orders for the trials. |
| `data_management.py` | Defines the data collection structure and handles the saving of all output files (`.csv`, `.npz`). |
| `triggering.py` | A helper module for sending a short trigger pulse followed by a reset command. |
| `pytcsii.py` | A class-based wrapper for communicating with the TCSII thermode via serial commands. |
