import json
import time
import threading
import keyboard
import pystray
from PIL import Image, ImageDraw
import sys
import os
import difflib
import re

from overlay import RegionSelection
from ocr_engine import OCREngine
from comms import copy_to_clipboard

# --------------------------
# Config and DB paths
# --------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DB_FILE = os.path.join(os.path.dirname(__file__), 'errors_db.json')

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

config = load_config()
TESSERACT_CMD = config.get("tesseract_cmd", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# --------------------------
# OCR Engine Initialize
# --------------------------
icon = None
running = True
ocr = None
try:
    ocr = OCREngine(TESSERACT_CMD)
except Exception as e:
    print(f"OCR Engine Init Error: {e}")

# --------------------------
# Error DB Helpers
# --------------------------
def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9.\s]", " ", text)  # remove punctuation except dot
    return " ".join(text.split())  # collapse whitespace



def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # normalize keys to lowercase
    return {k.lower(): v for k, v in raw.items()}

def find_error_solution(text: str):
    db = load_db()
    normalized = normalize_text(text)

    print("Normalized OCR:", normalized)  # debug

    for key, value in db.items():
        if key in normalized:
            print(f"✅ Exact match for key: {key}")
            return value
        # fuzzy similarity
        ratio = difflib.SequenceMatcher(None, key, normalized).ratio()
        if ratio > 0.6:
            print(f"🤏 Fuzzy match for key: {key} (score {ratio:.2f})")
            return value

    print("❌ No match found")
    return None

# --------------------------
# Tray Icon
# --------------------------
def create_icon_image():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(0, 0, 0))
    return image

def on_quit(icon_obj, item):
    global running
    running = False
    icon_obj.stop()

def exit_app_hotkey():
    global running
    print("Exit hotkey pressed. Exiting...")
    running = False
    if icon:
        icon.stop()

# --------------------------
# Capture Logic hey
# --------------------------
def perform_capture():
    print("Hotkey triggered!")
    try:
        region_selector = RegionSelection()
        selection = region_selector.get_region()

        if selection:
            print(f"Region selected: {selection}")

            if ocr:
                text = ocr.capture_and_extract(selection)

                if text:
                    print(f"Extracted Text: {text}")
                    copy_to_clipboard(text)

                    # 🔍 Check local error DB
                    solution = find_error_solution(text)
                    if solution:
                        print(f"[LOCAL DB MATCH] Category: {solution['category']}")
                        print(f"Suggested Fix: {solution['solution']}")
                    else:
                        print("[LOCAL DB] No match found. Consider AI fallback.")
                else:
                    print("No text detected. Try selecting a larger area or clearer text.")
            else:
                print("OCR engine not initialized.")
        else:
            print("Selection cancelled.")
    except Exception as e:
        print(f"Error in capture logic: {e}")

# --------------------------
# Hotkeys and Tray
# --------------------------
def setup_hotkey():
    keyboard.add_hotkey('ctrl+alt+shift+o', perform_capture)
    keyboard.add_hotkey('ctrl+alt+shift+p', exit_app_hotkey)

def start_tray_icon():
    global icon
    icon = pystray.Icon("OCR Tool")
    icon.menu = pystray.Menu(pystray.MenuItem('Quit', on_quit))
    icon.icon = create_icon_image()
    icon.title = "OCR Tool"
    icon.run()

# --------------------------
# Main Loop
# --------------------------
def main():
    setup_hotkey()
    print("Background OCR Service Running...")
    print("Press Ctrl+Alt+Shift+O to capture.")
    print("Press Ctrl+Alt+Shift+P to exit.")
    
    # Start tray icon in background thread
    tray_thread = threading.Thread(target=start_tray_icon, daemon=True)
    tray_thread.start()

    # Loop until exit hotkey pressed
    while running:
        time.sleep(0.5)

    print("Exiting program...")
    os._exit(0)

if __name__ == "__main__":
    main()