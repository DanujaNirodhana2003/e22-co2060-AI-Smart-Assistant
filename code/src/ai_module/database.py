import json
import os

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'errors_db.json')


def normalize_text(text: str) -> str:
    """
    Normalize OCR text for matching
    """
    return (
        text.lower()
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("’", "'")
        .strip()
    )


def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_error_solution(text: str):
    """
    Returns solution dict if found, else None
    """
    db = load_db()
    normalized = normalize_text(text)

    for key, value in db.items():
        if key in normalized:
            return value

    return None
