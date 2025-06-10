# triggering.py

from psychopy import core
import config

def send_state_change(port, code_to_send):
    """Writes a trigger code to change the state of the trigger lines."""
    if port and port.is_open:
        try:
            port.write(code_to_send)
        except Exception as e:
            print(f"ERROR writing state change {code_to_send.hex()}: {e}")
    else:
        print(f"SKIPPED state change {code_to_send.hex()} (port not available/open).")

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
