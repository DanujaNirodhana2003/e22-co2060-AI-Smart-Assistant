try:
    import tkinter
    import pystray
    import PIL
    import pytesseract
    import serial
    import keyboard
    import pyperclip
    print("All imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
