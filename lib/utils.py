"""Shared utility functions: detection, formatting, hashing, I/O."""

import os
import re
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

from .config import (
    CATEGORIES, JUNK_EXTENSIONS, JUNK_PATTERNS, SCREENSHOT_PATTERNS,
    CLEANUP_PATTERNS, C, LOG_DIR, LOG_FILE,
)


# ─── History I/O ──────────────────────────────────────────────────────────────

def ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_history():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(history):
    ensure_log_dir()
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)


# ─── File Detection ───────────────────────────────────────────────────────────

def is_screenshot(filepath):
    name = filepath.stem.lower()
    img_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".heic", ".tiff"}
    if filepath.suffix.lower() not in img_exts:
        return False
    for pattern in SCREENSHOT_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    return False


def is_junk(filepath):
    name = filepath.name.lower()
    ext = filepath.suffix.lower()
    if ext in JUNK_EXTENSIONS:
        return True
    try:
        if filepath.stat().st_size == 0:
            return True
    except OSError:
        pass
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    return False


def get_category(filepath):
    if is_screenshot(filepath):
        return "Screenshots"
    ext = filepath.suffix.lower()
    for category, info in CATEGORIES.items():
        if category == "Screenshots":
            continue
        if ext in info["extensions"]:
            return category
    return "Other"


def get_category_icon(category):
    if category in CATEGORIES:
        return CATEGORIES[category]["icon"]
    return "📁"


# ─── Formatting ───────────────────────────────────────────────────────────────

def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def human_age(seconds):
    days = seconds / 86400
    if days < 1:
        return f"{seconds / 3600:.0f}h ago"
    elif days < 30:
        return f"{days:.0f}d ago"
    elif days < 365:
        return f"{days / 30:.0f}mo ago"
    else:
        return f"{days / 365:.1f}y ago"


# ─── File Utilities ───────────────────────────────────────────────────────────

def safe_destination(dest_path):
    if not dest_path.exists():
        return dest_path
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def get_date_subfolder(filepath):
    mtime = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(mtime)
    year = dt.strftime("%Y")
    month_day = dt.strftime("%m.%d")
    return os.path.join(year, month_day)


def file_hash(filepath, chunk_size=8192):
    h = hashlib.sha256()
    max_bytes = 1024 * 1024
    read_bytes = 0
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
                read_bytes += len(chunk)
                if read_bytes >= max_bytes:
                    h.update(str(filepath.stat().st_size).encode())
                    break
    except (PermissionError, OSError):
        return None
    return h.hexdigest()


def clean_filename(name):
    stem = Path(name).stem
    suffix = Path(name).suffix
    original_stem = stem
    for pattern, replacement in CLEANUP_PATTERNS:
        stem = re.sub(pattern, replacement, stem)
    stem = stem.strip()
    if not stem:
        stem = original_stem
    cleaned = stem + suffix
    return cleaned, cleaned != name


# ─── CLI Output ───────────────────────────────────────────────────────────────

def print_header():
    print()
    print(f"  {C.BOLD}{C.CYAN}╔═════════════════════════════════════════╗{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}║    Smart Local File Organizer  v2       ║{C.RESET}")
    print(f"  {C.BOLD}{C.CYAN}╚═════════════════════════════════════════╝{C.RESET}")
    print()


def print_divider():
    print(f"  {C.GRAY}{'─' * 54}{C.RESET}")


def print_section(title, icon=""):
    print()
    print(f"  {icon} {C.BOLD}{C.WHITE}{title}{C.RESET}")
    print(f"  {C.GRAY}{'─' * 54}{C.RESET}")


def ask_yes_no(prompt, default=True):
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        answer = input(f"  {C.YELLOW}?{C.RESET} {prompt} {C.DIM}{suffix}{C.RESET} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    if not answer:
        return default
    return answer in ("y", "yes")


def notify(title, message):
    """Send a macOS notification. Silently fails on other platforms."""
    try:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}"'
        ], capture_output=True, timeout=5)
    except Exception:
        pass
