# Thermal Pain EEG Experiment

A PsychoPy-based experimental platform for thermal pain perception research with synchronized EEG recording. Delivers precisely controlled thermal stimuli via TCSII thermode while recording subjective pain responses and neural activity.

## 🚀 Quick Start

**For experienced users:**
1. `pip install -r requirements.txt`
2. Connect hardware: TCSII thermode, EEG trigger interface
3. Configure COM ports and EEG IP in the startup dialog
4. Run: `python main_experiment.py`

**For first-time setup:** See [Installation Guide](#installation-guide) below.

**Testing without hardware:** Run `python main_experiment_sim.py`

## Table of Contents

### Essential Information
- [Overview](#overview)
- [Experimental Design](#experimental-design)
- [Installation Guide](#installation-guide)
- [Running the Experiment](#running-the-experiment)
- [Data Output](#data-output)

### Detailed Documentation
- [Hardware Requirements](#hardware-requirements)
- [Hardware Setup](#hardware-setup)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Overview

### What This Experiment Does
- **Thermal Stimulation**: Controlled heat (44.3-49.3°C) via TCSII thermode
- **Subjective Assessment**: Binary pain judgment + Visual Analogue Scale rating
- **Neural Recording**: Synchronized EEG with millisecond-precision triggers
- **Multi-Session Design**: 5 runs × 12 trials = complete experimental protocol

### Key Features
- ✅ **Hardware Integration**: TCSII thermode, BrainProducts EEG, serial triggers
- ✅ **Simulation Mode**: Test without hardware connections
- ✅ **Balanced Randomization**: Advanced constraint-based trial generation
- ✅ **Comprehensive Data**: Trial summaries, continuous VAS traces, raw backups
- ✅ **Robust Error Handling**: Graceful degradation when hardware unavailable

## Experimental Design

### Trial Structure
Each trial follows this sequence:

| Phase | Duration | Description | Trigger Code |
|-------|----------|-------------|--------------|
| **ITI** | 15-20s | Fixation cross | `0x02` |
| **Thermal Stimulation** | 12.5s | 3s ramp-up + 7.5s hold + 2s ramp-down | `0x04` |
| **Pain Question** | Variable | "Était-ce douloureux? (o/n)" | `0x08` |
| **VAS Rating** | ≤30s | Context-dependent intensity scale | `0x20` |

### Multi-Run Design
- **5 Runs Total**: 12 trials each (60 trials total)
- **Complete Coverage**: Every temperature × surface combination tested exactly twice
- **Constraint Randomization**: No consecutive stimulation on same surface
- **Fixed First Trial**: Run 1 always starts with maximum temperature

### Stimulus Parameters
- **Temperatures**: 44.3°C, 45.3°C, 46.3°C, 47.3°C, 48.3°C, 49.3°C
- **Surfaces**: 5 thermode surfaces with balanced distribution
- **Baseline**: 35.0°C between trials

## Installation Guide

### 1. System Requirements
- **OS**: Windows 10/11 (primary), Linux/Mac (limited support)
- **Python**: 3.8+ recommended
- **Hardware**: See [Hardware Requirements](#hardware-requirements)

### 2. Software Installation
```bash
# Create virtual environment (recommended)
python -m venv thermal_pain_env
thermal_pain_env\Scripts\activate  # Windows
# source thermal_pain_env/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Hardware Drivers
| Component | Driver Source |
|-----------|---------------|
| **TCSII Thermode** | Manufacturer USB-to-serial drivers |
| **EEG System** | BrainProducts drivers + RCS software |
| **Trigger Interface** | Serial device drivers |

### 4. Initial Configuration
1. **Identify COM Ports**: Windows Device Manager → Ports (COM & LPT)
2. **Network Setup**: Configure EEG computer IP address
3. **EEG Workspace**: Create .rwksp file with appropriate montage
4. **Test Connections**: Run `python main_experiment_sim.py`

## Running the Experiment

### Pre-Experiment Checklist
- [ ] All hardware powered and connected
- [ ] EEG recording software running with RCS enabled
- [ ] Thermode at baseline temperature (35°C)
- [ ] Participant positioned and briefed
- [ ] Emergency procedures reviewed

### Execution Steps

#### 1. Launch Experiment
```bash
python main_experiment.py
```

#### 2. Configure Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| **Participant** | `sub001` | Unique participant ID |
| **COM Thermode** | `COM15` | Thermode serial port |
| **COM Trigger** | `COM17` | Trigger device port |
| **EEG IP** | `192.168.1.2` | EEG computer network address |
| **EEG Workspace** | `C:\path\to\workspace.rwksp` | Full path to EEG workspace |
| **Run Number** | `1` | Current run (1-5) |

#### 3. System Initialization
The system automatically:
- Establishes hardware connections
- Starts EEG recording
- Generates trial sequences
- Displays participant instructions

#### 4. Data Collection
- **12 trials per run** with automatic progression
- **Real-time monitoring** via console output
- **Emergency stop**: Press `ESC` key
- **Run completion**: Data saved automatically

#### 5. Multiple Runs
Execute each run separately by restarting the script and changing the run number.

## Data Output

### File Structure
```
data/
└── [participant_id]/
    ├── [id]_ThermalPainEEGFMRI_run[X]_[date]_TrialSummary.csv
    ├── [id]_ThermalPainEEGFMRI_run[X]_[date]_VASTraces_Long.csv
    └── [id]_ThermalPainEEGFMRI_run[X]_[date]_BACKUP.npz
```

### Data Types

#### Trial Summary (`*_TrialSummary.csv`)
One row per trial with key outcomes:
- `stimulus_temp`: Applied temperature (°C)
- `selected_surface`: Thermode surface (1-5)
- `pain_binary_coded`: Pain judgment (0=No, 1=Yes)
- `vas_final_coded_rating`: Final VAS rating (0-99 or 100-199)
- Timestamps for all experimental phases

#### VAS Traces (`*_VASTraces_Long.csv`)
Continuous rating data sampled at 5 Hz:
- `vas_time_in_trial_secs`: Time from VAS onset
- `vas_coded_rating`: Slider position (pain ratings +100 offset)
- Trial and context information

#### Raw Backup (`*_BACKUP.npz`)
Complete data archive for custom analysis.

## Hardware Requirements

### Essential Components

| Component | Specifications |
|-----------|----------------|
| **TCSII Thermode** | Multi-surface, 115200 baud, 30-60°C range |
| **EEG System** | BrainProducts amplifier with RCS |
| **Trigger Interface** | Serial triggers, 2M baud, 8-bit hex codes |
| **Presentation System** | 1920×1080 display, standard keyboard |

### Connection Diagram
```
Stimulus Computer ─┬─[Serial]─→ TCSII Thermode
                   ├─[Serial]─→ Trigger Device ─→ EEG Amplifier
                   └─[Network]─→ EEG Computer (RCS)
```

## Hardware Setup

### TCSII Thermode
1. **Physical Setup**: Mount on adjustable arm, ensure stable forearm contact
2. **Test Communication**: 
   ```python
   from pytcsii import tcsii_serial
   thermode = tcsii_serial('COM15', baseline=35.0)
   thermode.print_temp()
   ```
3. **Safety Check**: Verify temperature limits and emergency stop

### EEG System
1. **RCS Configuration**: Launch BrainVision Recorder, enable RCS
2. **Network Setup**: Ensure stimulus computer can reach EEG system
3. **Trigger Testing**: Run simulation mode, verify trigger reception

### System Integration
```bash
# Full system test
python main_experiment_sim.py  # Verify all hardware commands

# Hardware integration test  
python main_experiment.py     # Single trial with actual hardware
```

## Configuration

All parameters are in `config.py`:

### Core Parameters
```python
# Experimental design
POSSIBLE_THERMODE_TEMPS = [44.3, 45.3, 46.3, 47.3, 48.3, 49.3]
AVAILABLE_SURFACES = [1, 2, 3, 4, 5]
BASELINE_TEMP = 35.0

# Timing
RAMP_UP_SECS_CONST = 3.0
STIM_HOLD_DURATION_SECS = 7.5
RAMP_DOWN_SECS_CONST = 2.0
ITI_DURATION_RANGE = (15, 20)

# VAS settings
VAS_SPEED_UNITS_PER_SEC = 22.0
VAS_MAX_DURATION_SECS = 30.0
VAS_SAMPLING_INTERVAL_SECS = 0.2

# Triggers
TRIG_EEG_REC_START = b'\x01'
TRIG_ITI_START = b'\x02'
TRIG_STIM_ON = b'\x04'
TRIG_PAIN_Q_ON = b'\x08'
TRIG_VAS_ON = b'\x20'
TRIG_RESET = b'\x00'
```

## Troubleshooting

### Quick Fixes

| Problem | Solution |
|---------|----------|
| **Thermode not responding** | Check COM port, verify drivers |
| **EEG connection failed** | Confirm RCS running, test network connectivity |
| **Triggers not working** | Verify baud rate (2M), test with simulation |
| **VAS not responding** | Check keyboard connection, verify no stuck keys |
| **Data saving failed** | Check disk space, verify file permissions |

### Diagnostic Commands
```bash
# Check COM ports
python -c "import serial.tools.list_ports; print(list(serial.tools.list_ports.comports()))"

# Test thermode
python -c "from pytcsii import tcsii_serial; tcsii_serial('COM15')"

# Network test
ping 192.168.1.2

# Debug mode
# Edit main_experiment.py: logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

#### Hardware Problems
- **Port Access Denied**: Close other applications using COM ports
- **Timing Issues**: Disable Windows power management
- **Memory Problems**: Restart between participants (≥8GB RAM recommended)

#### Experiment Execution
- **Trial Generation Errors**: Delete `trial_lists.json` to regenerate
- **Performance Issues**: Close unnecessary applications, use dedicated computer

## Development

### Code Architecture
```
├── main_experiment.py      # Main control loop
├── config.py              # All parameters
├── hardware_setup.py      # Device initialization
├── experiment_logic.py     # Trial generation/randomization
├── data_management.py     # Data collection/export
├── triggering.py          # Event synchronization
└── pytcsii.py            # Thermode communication
```

### Adding Features

#### New Parameters
1. Add to `config.py`
2. Update hardware initialization
3. Modify experiment logic
4. Extend data collection

#### Testing
```bash
# Unit tests
python -m pytest tests/

# Integration testing
python main_experiment_sim.py  # Simulation
python main_experiment.py      # Hardware test
```

### Key Implementation Details

#### Trial Randomization
- **Complete factorial design**: 6 temps × 5 surfaces × 2 repetitions = 60 trials
- **Constraint-based randomization**: Prevents consecutive same-surface stimulation
- **Persistent sequences**: Saved in `trial_lists.json` for consistency

#### VAS System
- **Real-time sampling**: 5 Hz continuous tracking
- **Context-dependent**: Different anchors for pain vs. heat ratings
- **Coding system**: Pain ratings offset by +100 for analysis

#### Trigger Timing
- **Hardware precision**: Direct serial communication at 2M baud
- **Frame-locked**: PsychoPy `callOnFlip` for precise timing
- **Reset protocol**: Each trigger followed by explicit reset

---

## Support

For technical support, see the [Troubleshooting](#troubleshooting) section or consult the development team.

## License

This project is open source.
