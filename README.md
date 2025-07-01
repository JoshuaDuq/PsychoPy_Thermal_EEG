# Thermal Pain EEG Experiment

A comprehensive PsychoPy-based experimental platform for thermal pain perception research with synchronized EEG recording. This system delivers precisely controlled thermal stimuli via TCSII thermode, records subjective pain responses and VAS ratings, and provides millisecond-accurate event synchronization for neurophysiological analysis.

## Table of Contents
- [Overview](#overview)
- [Experimental Design](#experimental-design)
- [System Architecture](#system-architecture)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation Guide](#installation-guide)
- [Hardware Setup Guide](#hardware-setup-guide)
- [Running the Experiment](#running-the-experiment)
- [Data Output and Analysis](#data-output-and-analysis)
- [Configuration and Customization](#configuration-and-customization)
- [Troubleshooting](#troubleshooting)
- [Development Guide](#development-guide)
- [Technical Implementation Details](#technical-implementation-details)

## Overview

This experimental platform investigates the neural correlates of thermal pain perception through a carefully controlled paradigm combining:

- **Thermal Stimulation**: Precisely controlled heat stimuli (44.3°C - 49.3°C) delivered via TCSII thermode
- **Subjective Assessment**: Binary pain/no-pain judgments followed by context-dependent Visual Analogue Scale (VAS) ratings
- **Neural Recording**: Synchronized EEG acquisition with millisecond-precision event marking
- **Multi-Surface Design**: Balanced stimulus delivery across multiple thermode surfaces to prevent habituation

The experiment is designed for both standalone thermal pain research and integration with fMRI studies, featuring robust hardware control, comprehensive data logging, and advanced trial randomization.

## Experimental Design

### Task Structure

Participants undergo thermal stimulation while their neural responses are recorded. Each trial follows a structured sequence:

1. **Inter-Trial Interval (ITI)**: 15-20 seconds of fixation
2. **Thermal Stimulation**: 3s ramp-up + 7.5s hold + 2s ramp-down (12.5s total)
3. **Pain Judgment**: Binary response ("Était-ce douloureux? o/n")
4. **Intensity Rating**: Context-dependent VAS rating

### Trial Generation and Randomization

The experiment uses a sophisticated multi-run design:

- **5 Runs Total**: Each run contains 12 trials
- **Complete Coverage**: All temperature × surface combinations are tested exactly twice across all runs
- **Balanced Distribution**: Temperatures are evenly distributed across thermode surfaces
- **Constraint-Based Randomization**: 
  - Prevents consecutive stimulation on the same surface
  - Special handling for maximum temperature trials
  - First trial of Run 1 is always maximum temperature on Surface 1

### Stimulus Parameters

- **Temperature Range**: 6 levels from 44.3°C to 49.3°C (1°C increments)
- **Surface Distribution**: 5 thermode surfaces with balanced assignment
- **Baseline Temperature**: 35.0°C
- **Stimulation Profile**: Controlled ramp rates ensure consistent thermal transfer

## System Architecture

The codebase follows a modular architecture for maintainability and flexibility:

```
├── main_experiment.py      # Main experimental control
├── main_experiment_sim.py  # Hardware-free simulation mode
├── config.py              # Centralized configuration
├── hardware_setup.py      # Hardware initialization
├── experiment_logic.py     # Trial generation and randomization
├── data_management.py     # Data collection and export
├── triggering.py          # Event synchronization
├── pytcsii.py            # Thermode communication protocol
└── requirements.txt       # Python dependencies
```

### Key Design Features

- **Hardware Abstraction**: Clean separation between experiment logic and hardware control
- **Simulation Mode**: Complete experiment testing without physical hardware
- **Robust Error Handling**: Graceful degradation when hardware is unavailable
- **Comprehensive Logging**: Multi-level logging for debugging and analysis
- **Flexible Configuration**: Easy parameter modification without code changes

## Hardware Requirements

### Essential Components

1. **TCSII Thermal Stimulator**
   - Multi-surface thermode capability
   - Serial communication (115200 baud)
   - Temperature range: 30-60°C
   - Precision: 0.1°C

2. **EEG Recording System**
   - BrainProducts EEG amplifier
   - Remote Control Server (RCS) enabled
   - Network connectivity to stimulus computer

3. **Trigger System**
   - Serial-based trigger interface (2M baud)
   - 8-bit hexadecimal trigger codes
   - Compatible with BrainProducts trigger input

4. **Stimulus Presentation**
   - High-resolution display (recommended: 1920×1080)
   - Precise timing capabilities
   - Keyboard for participant responses

### Hardware Connections

```
Stimulus Computer ──[Serial]──→ TCSII Thermode
                 ├─[Serial]──→ Trigger Interface ──→ EEG Amplifier
                 └─[Network]─→ EEG Recording Computer (RCS)
```

## Software Requirements

### Operating System
- Windows 10/11 (primary support)
- Python 3.8+ recommended

### Python Dependencies
```bash
# Core packages
numpy>=1.21.0
pandas>=1.3.0
psychopy>=2023.1.0
pyserial>=3.5

# EEG integration (included with PsychoPy)
# psychopy.hardware.brainproducts
```

### System Libraries
- **PsychoPy**: Stimulus presentation and hardware control
- **Serial Communication**: Direct hardware interfacing
- **BrainProducts SDK**: EEG system integration

## Installation Guide

### Step 1: Python Environment Setup

```bash
# Create isolated environment (recommended)
python -m venv thermal_pain_env
source thermal_pain_env/bin/activate  # Linux/Mac
# OR
thermal_pain_env\Scripts\activate     # Windows

# Install required packages
pip install -r requirements.txt
```

### Step 2: Repository Setup

```bash
git clone <repository-url>
cd PsychoPy_Thermal_EEG
```

### Step 3: Hardware Driver Installation

1. **TCSII Drivers**: Install manufacturer-provided USB-to-serial drivers
2. **EEG Drivers**: Install BrainProducts drivers and RCS software
3. **Trigger Interface**: Configure serial trigger device drivers

### Step 4: Initial Configuration

1. **Identify Hardware Ports**:
   ```bash
   # Windows Device Manager → Ports (COM & LPT)
   # Note COM port assignments for thermode and trigger
   ```

2. **Network Configuration**:
   - Configure EEG computer IP address
   - Ensure stimulus computer can reach EEG system
   - Test RCS connectivity

3. **Workspace Setup**:
   - Create EEG workspace (.rwksp file)
   - Configure electrode montage
   - Set appropriate sampling rate (≥1000 Hz recommended)

## Hardware Setup Guide

### Step 1: Thermode Preparation

1. **Physical Setup**:
   - Mount thermode on adjustable arm
   - Ensure stable contact with participant's forearm
   - Verify all 5 surfaces are functional

2. **Calibration**:
   ```python
   # Test thermode communication
   python -c "
   from pytcsii import tcsii_serial
   thermode = tcsii_serial('COM15', baseline=35.0)
   thermode.print_temp()  # Should display current temperatures
   "
   ```

3. **Safety Verification**:
   - Set maximum temperature limit (50°C)
   - Test emergency stop functionality
   - Verify baseline temperature accuracy

### Step 2: EEG System Configuration

1. **RCS Setup**:
   - Launch BrainVision Recorder
   - Enable Remote Control Server
   - Configure network settings

2. **Workspace Preparation**:
   - Load appropriate electrode configuration
   - Set sampling rate (1000 Hz minimum)
   - Configure impedance limits

3. **Trigger Testing**:
   ```python
   # Test trigger communication
   python main_experiment_sim.py
   # Verify trigger codes appear in EEG software
   ```

### Step 3: System Integration Testing

1. **Run Simulation Mode**:
   ```bash
   python main_experiment_sim.py
   ```
   - Verify all hardware commands print correctly
   - Check trial generation logic
   - Confirm data saving functionality

2. **Hardware Integration Test**:
   ```bash
   python main_experiment.py
   # Use test participant ID: "test001"
   # Run single trial to verify all systems
   ```

## Running the Experiment

### Pre-Experiment Checklist

- [ ] All hardware powered and connected
- [ ] EEG system recording and RCS enabled
- [ ] Thermode at baseline temperature
- [ ] Participant comfortably positioned
- [ ] Emergency stop procedures reviewed

### Step-by-Step Execution

1. **Launch Experiment**:
   ```bash
   python main_experiment.py
   ```

2. **Configure Session Parameters**:
   ```
   Participant: sub001        # Unique participant ID
   COM Thermode: COM15        # Thermode serial port
   COM Trigger: COM17         # Trigger device port
   EEG IP: 192.168.1.2       # EEG computer IP
   EEG Workspace: C:\path\to\workspace.rwksp
   Run Number: 1             # Current run (1-5)
   ```

3. **System Initialization**:
   - Hardware connections established
   - EEG recording started automatically
   - Trial sequence generated

4. **Participant Instructions** (French):
   ```
   "Vous recevrez des stimulations thermiques sur l'avant-bras.
   Concentrez-vous sur la croix de fixation.
   Après chaque stimulation:
   1. Indiquez si c'était douloureux (o/n)
   2. Évaluez l'intensité sur l'échelle (n/m + espace)"
   ```

5. **Experiment Execution**:
   - 12 trials per run
   - Automatic progression between phases
   - Real-time data collection
   - Emergency stop: ESC key

6. **Run Completion**:
   - Data automatically saved
   - EEG recording stopped
   - System cleanup performed

### Multiple Runs

Execute each run separately:
```bash
# Run 1
python main_experiment.py  # Set Run Number: 1

# Run 2  
python main_experiment.py  # Set Run Number: 2
# ... continue for runs 3-5
```

## Data Output and Analysis

### File Structure
```
data/
└── sub001/
    ├── sub001_ThermalPainEEGFMRI_run1_2024-01-15_TrialSummary.csv
    ├── sub001_ThermalPainEEGFMRI_run1_2024-01-15_VASTraces_Long.csv
    └── sub001_ThermalPainEEGFMRI_run1_2024-01-15_BACKUP.npz
```

### Trial Summary Data (`*_TrialSummary.csv`)

| Column | Description | Range/Format |
|--------|-------------|--------------|
| `trial_number` | Trial index (1-based) | 1-12 |
| `stimulus_temp` | Applied temperature | 44.3-49.3°C |
| `selected_surface` | Thermode surface used | 1-5 |
| `pain_binary_coded` | Pain judgment | 0=No, 1=Yes |
| `vas_final_coded_rating` | Final VAS rating | 0-99 (non-pain), 100-199 (pain) |
| `*_start_time` | Phase onset timestamps | Seconds from experiment start |
| `*_end_time` | Phase offset timestamps | Seconds from experiment start |

### VAS Trace Data (`*_VASTraces_Long.csv`)

Continuous VAS rating data sampled at 5 Hz:

| Column | Description |
|--------|-------------|
| `participant_id` | Participant identifier |
| `trial_number` | Trial index |
| `stimulus_temp` | Applied temperature |
| `pain_context_0no_1yes` | VAS context (0=heat, 1=pain) |
| `sample_in_trace` | Sample number within trial |
| `vas_time_in_trial_secs` | Time from VAS onset |
| `vas_coded_rating` | VAS position (0-99 or 100-199) |

### Raw Data Backup (`*_BACKUP.npz`)

NumPy compressed archive containing all collected data structures for custom analysis.

## Configuration and Customization

All experimental parameters are centralized in `config.py`:

### Temperature Configuration
```python
POSSIBLE_THERMODE_TEMPS = [44.3, 45.3, 46.3, 47.3, 48.3, 49.3]
BASELINE_TEMP = 35.0
MAX_TEMP_VALUE = max(POSSIBLE_THERMODE_TEMPS)
```

### Timing Parameters
```python
RAMP_UP_SECS_CONST = 3.0        # Temperature rise time
STIM_HOLD_DURATION_SECS = 7.5   # Target temperature hold
RAMP_DOWN_SECS_CONST = 2.0      # Temperature return time
ITI_DURATION_RANGE = (15, 20)   # Inter-trial interval range
```

### VAS Configuration
```python
VAS_SPEED_UNITS_PER_SEC = 22.0     # Slider movement speed
VAS_MAX_DURATION_SECS = 30.0       # Maximum rating time
VAS_SAMPLING_INTERVAL_SECS = 0.2   # Data collection rate
```

### Trigger Definitions
```python
TRIG_EEG_REC_START = b'\x01'   # EEG recording start
TRIG_ITI_START = b'\x02'       # Inter-trial interval
TRIG_STIM_ON = b'\x04'         # Thermal stimulation
TRIG_PAIN_Q_ON = b'\x08'       # Pain question
TRIG_VAS_ON = b'\x20'          # VAS rating
TRIG_RESET = b'\x00'           # Trigger reset
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Hardware Connection Problems

**Thermode Not Responding**:
```bash
# Check COM port availability
python -c "import serial.tools.list_ports; print(list(serial.tools.list_ports.comports()))"

# Test direct communication
python -c "
from pytcsii import tcsii_serial
try:
    thermode = tcsii_serial('COM15')
    print('Thermode connected successfully')
except:
    print('Connection failed - check port and drivers')
"
```

**EEG Connection Failed**:
- Verify RCS is running on EEG computer
- Check network connectivity: `ping 192.168.1.2`
- Confirm workspace path exists on EEG computer
- Restart BrainVision Recorder and re-enable RCS

**Trigger System Issues**:
- Verify trigger device drivers
- Check COM port configuration
- Test with simulation mode first
- Confirm baud rate settings (2M baud)

#### 2. Experiment Execution Problems

**Trial Generation Errors**:
- Check `POSSIBLE_THERMODE_TEMPS` and `AVAILABLE_SURFACES` in config.py
- Verify trial_lists.json is not corrupted
- Delete trial_lists.json to regenerate sequences

**VAS Rating Issues**:
- Ensure keyboard is properly connected
- Check for stuck keys ('n' or 'm')
- Verify VAS timing parameters in config.py

**Data Saving Failures**:
- Check disk space availability
- Verify write permissions in data directory
- Ensure participant ID contains no invalid characters

#### 3. Performance Issues

**Timing Precision**:
- Close unnecessary applications
- Disable Windows power management
- Use dedicated stimulus computer
- Monitor for frame drops in PsychoPy

**Memory Problems**:
- Restart experiment between participants
- Check for memory leaks in long sessions
- Verify adequate RAM (≥8GB recommended)

### Debug Mode

Enable detailed logging:
```python
# In main_experiment.py, modify:
logging.basicConfig(level=logging.DEBUG)
```

## Development Guide

### Adding New Features

#### 1. New Stimulus Parameters

1. **Update Configuration**:
   ```python
   # config.py
   NEW_PARAMETER = default_value
   ```

2. **Modify Hardware Setup**:
   ```python
   # hardware_setup.py
   def initialize_thermode(port_name, baseline_temp, new_param=None):
       # Implementation
   ```

3. **Update Experiment Logic**:
   ```python
   # experiment_logic.py
   def generate_modified_sequences(temps, surfaces, new_param):
       # Implementation
   ```

#### 2. Additional Data Collection

1. **Extend Data Collector**:
   ```python
   # data_management.py
   def create_data_collector():
       return {
           # ... existing fields
           'new_measure': []
       }
   ```

2. **Modify Trial Loop**:
   ```python
   # main_experiment.py
   exp_data_collector['new_measure'].append(new_value)
   ```

#### 3. Custom VAS Implementations

```python
# Create new VAS routine in separate module
def custom_vas_routine(win, context, custom_params):
    # Implementation
    return final_rating, trace_data
```

### Testing Framework

#### Unit Tests
```bash
# Run existing tests
python -m pytest tests/

# Add new tests
# tests/test_new_feature.py
```

#### Integration Testing
```bash
# Full system test with simulation
python main_experiment_sim.py

# Hardware integration test
python -c "
import hardware_setup as hw
# Test each component individually
"
```

### Code Style Guidelines

- **PEP 8 Compliance**: Use black formatter
- **Type Hints**: Add for new functions
- **Documentation**: Docstrings for all public methods
- **Error Handling**: Graceful degradation preferred
- **Logging**: Use appropriate log levels

## Technical Implementation Details

### Trial Randomization Algorithm

The experiment uses a sophisticated constraint-based randomization:

1. **Complete Factorial Design**: All temperature × surface combinations tested exactly twice
2. **Run Generation**: 5 runs of 12 trials each, balanced across conditions
3. **Surface Constraints**: Prevents consecutive stimulation on same surface
4. **Special Rules**: Maximum temperature trials have additional spacing requirements

### VAS Implementation

The Visual Analogue Scale uses a sophisticated real-time sampling system:

- **Continuous Tracking**: 5 Hz sampling during rating period
- **Context-Dependent Scaling**: Different anchors for pain vs. heat ratings
- **Interaction Detection**: Distinguishes between active rating and timeout
- **Boundary Handling**: Special logic for slider endpoints
- **Coding System**: Pain ratings offset by +100 for analysis

### Trigger Synchronization

Event marking uses millisecond-precision timing:

- **Hardware Triggers**: Direct serial communication at 2M baud
- **Software Timing**: PsychoPy's `callOnFlip` for frame-accurate timing
- **Reset Protocol**: Each trigger followed by explicit reset
- **Error Handling**: Graceful degradation when trigger system unavailable

### Thermode Communication Protocol

TCSII interface implementation:

- **Serial Communication**: 115200 baud, custom command protocol
- **Temperature Control**: Precise ramp rate calculation
- **Multi-Surface Management**: Individual surface parameter setting
- **Safety Systems**: Maximum temperature limits and emergency stops

### Data Architecture

Multi-format data export for comprehensive analysis:

- **Trial Summary**: High-level outcomes in CSV format
- **VAS Traces**: Continuous rating data in long format
- **Raw Backup**: Complete data structures in NumPy format
- **Timestamp Precision**: Full floating-point precision maintained

---

## Support and Citation

For technical support, please consult the troubleshooting section or contact the development team. When using this software in research, please cite appropriately and acknowledge the open-source contributions that make this work possible.

## License

This project is licensed under [appropriate license]. See LICENSE file for details.
