# triggering.py

from psychopy import core
import config

def send_event_pulse(port, code_to_pulse, reset_code):
    """Sends a short trigger pulse followed by a reset."""
    if port and port.is_open:
        try:
            port.write(code_to_pulse)
            core.wait(config.TRIGGER_PULSE_SECS)
            port.write(reset_code)
        except Exception as e:
            print(f"ERROR writing pulse trigger {code_to_pulse.hex()}: {e}")
    else:
        print(f"SKIPPED pulse trigger {code_to_pulse.hex()} (port not available/open).")
