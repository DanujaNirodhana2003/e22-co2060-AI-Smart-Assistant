import json
import time
import threading
import keyboard
import pystray
from PIL import Image, ImageDraw
import sys
import os

from overlay import RegionSelection
from ocr_engine import OCREngine
from comms import copy_to_clipboard, send_via_serial

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

config = load_config()
TESSERACT_CMD = config.get("tesseract_cmd", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
SERIAL_PORT = config.get("serial_port", "COM3")
BAUD_RATE = config.get("baud_rate", 9600)

ocr = None
try:
    ocr = OCREngine(TESSERACT_CMD)
except Exception as e:
    print(f"OCR Engine Init Error: {e}")

def create_icon_image():
    # Create a simple icon for the tray
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(0, 0, 0))
    return image

def on_quit(icon, item):
    icon.stop()
    sys.exit()

def perform_capture():
    print("Hotkey triggered!")
    # Capture Region
    try:
        # NOTE: Tkinter needs to run in the main thread ideally, or be very careful. 
        # Since this is called from a hotkey thread, creating a new Tk instance *might* work 
        # if no other Tk instance is running.
        region_selector = RegionSelection()
        selection = region_selector.get_region() # This blocks until selection is made
        
        if selection:
            print(f"Region selected: {selection}")
            # OCR
            if ocr:
                text = ocr.capture_and_extract(selection)
                if text:
                    print(f"Extracted Text: {text}")
                    # Outputs
                    copy_to_clipboard(text)
                    send_via_serial(text, SERIAL_PORT, BAUD_RATE)
                else:
                    print("No text detected.")
            else:
                print("OCR engine not initialized.")
        else:
            print("Selection cancelled.")
    except Exception as e:
        print(f"Error in capture logic: {e}")

def setup_hotkey():
    keyboard.add_hotkey('ctrl+shift+o', perform_capture)

def main():
    setup_hotkey()
    print("Background OCR Service Running...")
    print("Press Ctrl+Shift+O to capture.")
    
    icon = pystray.Icon("OCR Tool")
    icon.menu = pystray.Menu(pystray.MenuItem('Quit', on_quit))
    icon.icon = create_icon_image()
    icon.title = "OCR Tool"
    
    icon.run()

if __name__ == "__main__":
    main()
