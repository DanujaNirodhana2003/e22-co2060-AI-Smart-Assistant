import json
import time
import threading
import multiprocessing
import keyboard
import pystray
from PIL import Image, ImageDraw
import sys
import os
import difflib
import re
import ctypes # Required for DPI fix

# --- Custom Modules ---
from overlay import RegionSelection
from ocr_engine import OCREngine
from comms import copy_to_clipboard
import animation  
import chat_ui

# --------------------------
# DPI Awareness Fix (Critical for correct coords)
# --------------------------
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

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
# Globals
# --------------------------
icon = None
running = True
ocr = None
chat_queue = None

try:
    ocr = OCREngine(TESSERACT_CMD)
except Exception as e:
    print(f"OCR Engine Init Error: {e}")

# --------------------------
# Animation Helper
# --------------------------
def run_animation_process():
    try:
        animation.main()
    except Exception as e:
        print(f"Animation error: {e}")

# --------------------------
# Error DB Helpers
# --------------------------
def normalize_text(text: str) -> str:
    text = text.lower().replace("’", "'")
    text = re.sub(r"[^a-z0-9.\s]", " ", text) 
    return " ".join(text.split())

def load_db() -> dict:
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def find_error_solution(text: str):
    db = load_db()
    normalized = normalize_text(text)
    for key, value in db.items():
        if key in normalized: return value
        ratio = difflib.SequenceMatcher(None, key, normalized).ratio()
        if ratio > 0.6: return value
    return None

# --------------------------
# Tray Icon
# --------------------------
def create_icon_image():
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(0, 0, 0))
    return image

def on_quit(icon_obj, item):
    global running
    running = False
    icon_obj.stop()

def exit_app_hotkey():
    global running
    print("Exit hotkey pressed.")
    running = False
    if icon: icon.stop()

# --------------------------
# Capture Logic
# --------------------------
def perform_capture():
    print("Hotkey triggered!")
    anim_process = None 

    try:
        # 1. Start Animation
        anim_process = multiprocessing.Process(target=run_animation_process)
        anim_process.start()

        # 2. Run Selection
        region_selector = RegionSelection()
        selection = region_selector.get_region()

        if selection:
            # 3. Stop Animation IMMEDIATELY
            if anim_process.is_alive():
                anim_process.terminate()
                anim_process.join()

            # --- [FIX] WAIT FOR OVERLAY TO CLEAR ---
            # Give the screen 0.3 seconds to repaint the desktop
            # before taking the screenshot.
            time.sleep(0.3) 
            # ---------------------------------------

            if ocr:
                print(f"Capturing region: {selection}")
                text = ocr.capture_and_extract(selection)

                if text:
                    print(f"Extracted: {text}")
                    copy_to_clipboard(text)
                    
                    # --- Send to Chat ---
                    if chat_queue:
                        chat_queue.put(text)
                    
                    solution = find_error_solution(text)
                    if solution: print(f"Fix: {solution['solution']}")
                else:
                    print("No text detected (Clean Capture).")
        else:
            print("Selection cancelled.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if anim_process and anim_process.is_alive():
            anim_process.terminate()
            anim_process.join()

# --------------------------
# Main Loop
# --------------------------
def setup_hotkey():
    keyboard.add_hotkey('ctrl+alt+shift+o', perform_capture)
    keyboard.add_hotkey('ctrl+alt+shift+p', exit_app_hotkey)

def start_tray_icon():
    global icon
    icon = pystray.Icon("OCR Tool")
    icon.menu = pystray.Menu(pystray.MenuItem('Quit', on_quit))
    icon.icon = create_icon_image()
    icon.run()

def main():
    global chat_queue
    setup_hotkey()
    
    print("Background OCR Service Running...")
    print("-------------------------------------------------")
    print("Capture: Ctrl + Alt + Shift + O")
    print("Exit:    Ctrl + Alt + Shift + P")
    print("-------------------------------------------------")
    
    chat_queue, chat_process = chat_ui.start_chat_process()

    tray_thread = threading.Thread(target=start_tray_icon, daemon=True)
    tray_thread.start()

    while running:
        time.sleep(0.5)

    print("Exiting...")
    if chat_process.is_alive():
        chat_process.terminate()
    os._exit(0)

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    main()