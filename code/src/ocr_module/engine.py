import os
import pytesseract
import mss
from PIL import Image, ImageEnhance, ImageFilter
from ctypes import windll


class OCREngine:
    def __init__(self, tesseract_cmd):
        """
        Initialize OCR Engine with path to Tesseract executable.
        """
        if not os.path.exists(tesseract_cmd):
            raise FileNotFoundError(f"Tesseract executable not found at: {tesseract_cmd}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # Ensure DPI awareness (important for Windows high-DPI screens)
        try:
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass  # Safe to ignore if not on Windows

    def _preprocess(self, img):
        """
        Preprocess image using PIL only.
        Steps:
        - Convert to grayscale
        - Resize (2x for better OCR on small text)
        - Slight contrast enhancement
        - Optional sharpen
        """
        img = img.convert("L")  # grayscale
        img = img.resize((img.size[0] * 2, img.size[1] * 2), Image.LANCZOS)
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = img.filter(ImageFilter.SHARPEN)
        return img

    def capture_and_extract(self, bbox, psm=6):
        """
        Capture a screen region and extract text via OCR.

        Args:
            bbox (tuple): (x1, y1, x2, y2) region to capture
            psm (int): Tesseract page segmentation mode
        """
        try:
            # Capture region with mss
            with mss.mss() as sct:
                monitor = {
                    "left": bbox[0],
                    "top": bbox[1],
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1]
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Preprocess
            img = self._preprocess(img)

            # Debug: save preprocessed image if needed
            # img.save("debug_preprocessed.png")

            # OCR
            config = f"--psm {psm}"
            text = pytesseract.image_to_string(img, config=config)
            return text.strip()

        except Exception as e:
            print(f"Error during OCR: {e}")
            return ""