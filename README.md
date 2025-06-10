# Thermal Pain EEG Experiment

This repository contains the complete PsychoPy-based code for conducting a thermal pain experiment with simultaneous EEG recording. The experiment is designed to deliver precisely controlled thermal stimuli, send accurate event markers to an EEG system, and collect behavioral pain ratings from participants.

The code is modular and configurable, allowing for easy adaptation to different experimental parameters.

***

## Features

* **Hardware Integration**: Controls a Medoc Pathway/TCS II thermal stimulator via the provided `pytcsii.py` driver.
* **EEG Synchronization**:
    * Sends precise, bit-mapped trigger codes through a serial port for robust event marking in EEG data.
    * Integrates with BrainVision Remote Control Server (RCS) to start and stop EEG recordings automatically from within the script.
* **Experimental Control**:
    * Presents a fully scripted trial sequence using PsychoPy, including visual stimuli (fixation cross, instructions, questions) and timing control.
    * Implements a randomized trial order for temperatures and a semi-randomized order for stimulation surfaces to minimize order effects.
* **Behavioral Data Collection**:
    * Records binary (yes/no) responses to a pain question.
    * Collects continuous intensity ratings using a Visual Analogue Scale (VAS) with context-dependent instructions (rating pain vs. non-painful warmth).
    * Continuously samples the VAS rating throughout the response period for dynamic analysis.
* **Comprehensive Data Output**: Saves collected data in multiple, analysis-ready formats, including a trial-by-trial summary CSV, a long-format CSV for VAS traces, and a full data backup.

***

## Repository Structure

The project is organized into several modules to separate concerns and improve readability.

* `main_experiment.py`: The main entry point for the experiment. It orchestrates hardware initialization, the trial loop, and data saving.
* `config.py`: A central configuration file. **Modify this file to change experiment parameters** like temperatures, timings, and trigger codes.
* `hardware_setup.py`: Contains functions for initializing all hardware components (Thermode, EEG RCS, Trigger Port).
* `experiment_logic.py`: Handles the logic for generating and randomizing the experimental sequences (temperature order, surface order).
* `triggering.py`: Helper functions for sending event pulses to the EEG system. The pulse duration is set by `TRIGGER_PULSE_SECS` in `config.py`.
* `data_management.py`: Defines the data collection structure and handles the final saving of data to disk in multiple formats.
* `pytcsii.py`: A low-level Python driver for communicating with and controlling the Medoc TCS II thermal stimulator via serial commands.

***

## Requirements

* **Hardware**
    * A computer capable of running PsychoPy.
    * Medoc TCS II Thermal Stimulator: Connected via a serial port.
    * EEG System: With a trigger input port. This code is configured for a BrainVision system.
    * Triggering Device: A serial port (e.g., a USB-to-Serial adapter) configured to send triggers to the EEG system.
    * (Optional) BrainVision EEG system with Remote Control Server (RCS) enabled on the recording computer for automated recording control.

* **Software & Libraries**
    * This script is built using Python and the PsychoPy framework. The following libraries are required:
        * `psychopy`
        * `pyserial`
        * `numpy`
        * `pandas`
    * You can install the dependencies using pip:
        ```bash
        pip install psychopy numpy pandas pyserial
        ```

***

## Setup and Usage

* **Clone the Repository**
    ```bash
    git clone <repository-url>
    ```
* **Configure Hardware**
    * Connect the thermode and trigger port to your computer and note their COM port identifiers (e.g., `COM4` on Windows, `/dev/ttyUSB0` on Linux). Ensure the EEG system is ready to receive triggers.

* **Edit Configuration**
    * Open the `config.py` file to adjust the core parameters of your experimental design.
        * `TRIG_...`: Set the hexadecimal trigger codes for each event.
        * `POSSIBLE_THERMODE_TEMPS`: Define the list of temperatures to be tested.
        * `NUM_REPEATS_PER_TEMP`: Set how many times each temperature should be presented.
        * `BASELINE_TEMP`: Set the thermode's baseline temperature.
        * `RAMP_UP_SECS_CONST`, `STIM_HOLD_DURATION_SECS`, etc.: Adjust all timing parameters.

* **Run the Experiment**
    * Navigate to the repository directory in your terminal and execute the main script:
        ```bash
        python main_experiment.py
        ```
    * A dialog box will appear. Confirm or enter the participant ID, COM ports, and EEG information. Click "OK" to begin.

***

## Experimental Protocol

Once started, the experiment proceeds as follows:

* **Setup**: The script initializes hardware, generates the random trial sequences, and prepares the PsychoPy window.
* **Welcome**: An instruction screen is displayed. The experiment waits for a `spacebar` press to continue.
* **Trial Loop**: The script enters the main loop, which repeats 60 times (or as configured). Each trial consists of four parts:

    * **A. Inter-Trial Interval (ITI)**
        * **Visual**: A white fixation cross `+` is shown.
        * **Duration**: A random interval between 15 and 20 seconds.
        * **Trigger**: `TRIG_ITI_START` (`0x02`) is delivered as a brief pulse at the onset.

    * **B. Thermal Stimulation**
        * **Visual**: The fixation cross remains on screen.
        * **Stimulus**: The thermode ramps up from 35.0°C to the target temperature in 3.0s, holds for 7.5s, and ramps down in 2.0s.
        * **Trigger**: `TRIG_STIM_ON` (`0x04`) is delivered as a brief pulse at the ramp-up onset. A `TRIG_STIM_OFF` (`0x08`) pulse is sent upon completion.

    * **C. Pain Question**
        * **Visual**: The text `"Était-ce douloureux? (o/n)"` is displayed.
        * **Interaction**: The script waits for the participant to press `o` (yes) or `n` (no).
        * **Trigger**: `TRIG_PAIN_Q_ON` (`0x10`) is delivered as a brief pulse at the onset.

    * **D. Visual Analogue Scale (VAS)**
        * **Visual**: A rating scale appears. The instructions and anchors change based on the previous pain response (e.g., "rate the PAIN" vs. "rate the WARMTH").
        * **Interaction**: The participant moves a red marker with the `n` (left) and `m` (right) keys and confirms with `spacebar`. The routine times out after 30s.
        * **Trigger**: `TRIG_VAS_ON` (`0x20`) is delivered as a brief pulse at the onset.

* **Shutdown**: After the final trial, EEG recording is stopped, hardware ports are closed, and a "Thank you" message is displayed for 5 seconds.

***

## Data Output

Data is saved in a folder named `data/<participant_id>/`. Three files are generated for each session:

* **`..._TrialSummary.csv`**:
    * A summary file with one row per trial.
    * **Columns include**: `trial_number`, `stimulus_temp`, `selected_surface`, `pain_binary_coded`, `vas_final_coded_rating`, and timestamps for each phase of the trial.

* **`..._VASTraces_Long.csv`**:
    * A detailed, long-format file containing the continuous VAS rating data.
    * **Columns include**: `participant_id`, `trial_number`, `sample_in_trace`, `vas_time_in_trial_secs`, and `vas_coded_rating`. This is ideal for analyzing rating trajectories.

* **`..._BACKUP.npz`**:
    * A compressed NumPy archive containing the raw Python data structures from the experiment. This serves as a complete backup for custom post-processing.

***

## License

This project is unlicensed. You are free to use, modify, and distribute the code. Please consider citing the repository if it is used in your research.
