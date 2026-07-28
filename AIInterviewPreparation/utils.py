"""
utils.py
Shared constants, color palette, path helpers, and small utility functions
used across the AI Interview Preparation application.
"""

import os
import sys
import json
import datetime
import random
import string

# --------------------------------------------------------------------------
# BASE PATH HANDLING (works both in dev mode and when frozen by PyInstaller)
# --------------------------------------------------------------------------

def get_base_path():
    """Return the folder the app is running from (handles PyInstaller .exe)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = get_base_path()

ASSETS_DIR = os.path.join(BASE_PATH, "assets")
CERT_ASSETS_DIR = os.path.join(ASSETS_DIR, "certificates")
REPORTS_DIR = os.path.join(BASE_PATH, "reports")
RESUMES_DIR = os.path.join(BASE_PATH, "resumes")
CERTIFICATES_DIR = os.path.join(BASE_PATH, "certificates")
DATA_DIR = os.path.join(BASE_PATH, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

for folder in (ASSETS_DIR, CERT_ASSETS_DIR, REPORTS_DIR, RESUMES_DIR,
               CERTIFICATES_DIR, DATA_DIR):
    os.makedirs(folder, exist_ok=True)

# --------------------------------------------------------------------------
# COLOR PALETTE (premium modern dark theme)
# --------------------------------------------------------------------------

COLORS = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "secondary": "#3B82F6",
    "accent": "#22C55E",
    "accent_hover": "#16A34A",
    "danger": "#EF4444",
    "background": "#0F172A",
    "sidebar": "#111827",
    "card": "#1E293B",
    "card_light": "#273449",
    "text": "#FFFFFF",
    "text_muted": "#94A3B8",
    "border": "#334155",
}

FONT_FAMILY = "Segoe UI"

# --------------------------------------------------------------------------
# SETTINGS PERSISTENCE (plain JSON file — no database)
# --------------------------------------------------------------------------

DEFAULT_SETTINGS = {
    "theme": "dark",
    "voice_enabled": True,
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"[WARN] Could not save settings: {e}")


# --------------------------------------------------------------------------
# MISC HELPERS
# --------------------------------------------------------------------------

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return datetime.datetime.now().strftime("%d-%m-%Y")


def generate_certificate_number():
    rand_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CERT-{datetime.datetime.now().strftime('%Y%m%d')}-{rand_part}"


def grade_from_percentage(pct: float) -> str:
    if pct >= 90:
        return "A+"
    elif pct >= 75:
        return "A"
    elif pct >= 60:
        return "B"
    elif pct >= 40:
        return "C"
    else:
        return "D"


def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, value))


def save_json_report(filename_prefix: str, data: dict) -> str:
    """Save a dict as a timestamped JSON report inside /reports and return path."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def list_reports():
    """Return list of (filename, full_path) for all saved reports, newest first."""
    if not os.path.exists(REPORTS_DIR):
        return []
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
    files.sort(reverse=True)
    return [(f, os.path.join(REPORTS_DIR, f)) for f in files]


def load_json_report(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
