import pytesseract
from PIL import ImageGrab, Image
import os

class OCREngine:
    def __init__(self, tesseract_cmd):
        if not os.path.exists(tesseract_cmd):
            raise FileNotFoundError(f"Tesseract executable not found at: {tesseract_cmd}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def capture_and_extract(self, bbox):
        """
        Captures the screen region defined by bbox (x1, y1, x2, y2)
        and returns the extracted text.
        """
        # bbox for ImageGrab is (left, top, right, bottom)
        try:
            screenshot = ImageGrab.grab(bbox=bbox)
            # Basic preprocessing could be added here (convert to grayscale, threshold) if needed
            # For now, raw image usually works well for screen captures
            text = pytesseract.image_to_string(screenshot)
            return text.strip()
        except Exception as e:
            print(f"Error during OCR: {e}")
            return ""

if __name__ == "__main__":
    # Test stub
    pass
