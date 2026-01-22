import pyperclip
import serial
import time

def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        print("Text copied to clipboard.")
    except Exception as e:
        print(f"Failed to copy to clipboard: {e}")

def send_via_serial(text, port, baud_rate=9600):
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            time.sleep(2) # Wait for connection to stabilize
            # Send text encoded as bytes
            ser.write(text.encode('utf-8'))
            print(f"Text sent to {port}.")
    except serial.SerialException as e:
        print(f"Serial communication error on {port}: {e}")
    except Exception as e:
        print(f"Error sending serial data: {e}")
