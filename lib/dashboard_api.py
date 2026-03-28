"""Dashboard backend: stats computation, reclaim scan/delete, logs, run commands."""

import re
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from .config import LOG_DIR, RECLAIM_HISTORY_FILE, SCAN_DIRS
from .utils import is_junk, file_hash

ORGANIZER = str(Path(__file__).parent.parent / "organize.py")
LOGS_DIR = LOG_DIR / "logs"
HISTORY_FILE = LOG_DIR / "history.json"


# ─── Organize / Undo Commands ────────────────────────────────────────────────

def run_organizer(target_dir, clean_names=True):
    """Run the organizer on a directory. Returns stdout."""
    cmd = [sys.executable, ORGANIZER, "--path", target_dir, "--run"]
    if clean_names:
        cmd.append("--clean-names")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"


def run_undo(undo_all=False):
    """Run undo or undo-all. Returns stdout."""
    cmd = [sys.executable, ORGANIZER, "--undo-all" if undo_all else "--undo"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"


# ─── History Loading ──────────────────────────────────────────────────────────

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def load_reclaim_history():
    if RECLAIM_HISTORY_FILE.exists():
        with open(RECLAIM_HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_reclaim_event(category, deleted, freed, file_names):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    history = load_reclaim_history()
    history.append({
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "deleted": deleted,
        "freed": freed,
        "sample_files": file_names[:8],
    })
    history = history[-200:]
    with open(RECLAIM_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# ─── Logs ─────────────────────────────────────────────────────────────────────

def load_logs():
    logs = []
    if LOGS_DIR.exists():
        for log_file in sorted(LOGS_DIR.glob("auto-organize-*.log"), reverse=True):
            try:
                content = log_file.read_text()
                logs.append({
                    "filename": log_file.name,
                    "date": log_file.name.replace("auto-organize-", "").replace(".log", ""),
                    "content": content,
                    "size": log_file.stat().st_size,
                })
            except OSError:
                pass
    return logs


# ─── Stats ────────────────────────────────────────────────────────────────────

def get_stats(history):
    reclaim_history = load_reclaim_history()
    if not history and not reclaim_history:
        return {
            "total_operations": 0, "total_files_moved": 0,
            "categories": {}, "by_month": {}, "by_directory": {},
            "recent_operations": [], "timeline": [],
            "reclaim_history": [], "total_reclaimed": 0,
        }

    total_files = sum(len(op["moves"]) for op in history)
    categories = defaultdict(int)
    by_month = defaultdict(int)
    by_directory = defaultdict(int)
    timeline = []

    for op in history:
        ts = op["timestamp"][:10]
        month = op["timestamp"][:7]
        target = op.get("target_dir", "unknown")
        count = len(op["moves"])
        by_month[month] += count
        by_directory[target] += count
        timeline.append({"date": ts, "count": count, "target": target})

        for move in op["moves"]:
            parts = Path(move["destination"]).parts
            for i, part in enumerate(parts):
                if part == "Organized" and i + 1 < len(parts):
                    categories[parts[i + 1]] += 1
                    break

    recent = []
    for op in reversed(history[-10:]):
        recent.append({
            "timestamp": op["timestamp"],
            "target_dir": op.get("target_dir", ""),
            "files_moved": len(op["moves"]),
            "sample_files": [Path(m["destination"]).name for m in op["moves"][:5]],
        })

    return {
        "total_operations": len(history),
        "total_files_moved": total_files,
        "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
        "by_month": dict(sorted(by_month.items())),
        "by_directory": dict(by_directory),
        "recent_operations": recent,
        "timeline": timeline,
        "reclaim_history": list(reversed(reclaim_history[-50:])),
        "total_reclaimed": sum(r["freed"] for r in reclaim_history),
    }


# ─── Reclaim Scan / Delete ───────────────────────────────────────────────────

def _file_hash(filepath, chunk_size=8192):
    return file_hash(filepath, chunk_size)


def scan_reclaimable():
    """Scan Downloads + Desktop for junk, duplicates, stale files."""
    all_files = []
    all_files_for_junk = []
    for d in SCAN_DIRS:
        p = Path(d)
        if not p.exists():
            continue
        for f in p.iterdir():
            if f.is_file():
                all_files_for_junk.append(f)
                if not f.name.startswith("."):
                    all_files.append(f)

    # Junk
    junk = []
    for f in all_files_for_junk:
        try:
            sz = f.stat().st_size
        except OSError:
            continue
        ext = f.suffix.lower()
        if sz == 0 or ext in {".crdownload", ".part", ".download"} or is_junk(f):
            junk.append({"path": str(f), "name": f.name, "size": sz,
                         "age": time.time() - f.stat().st_mtime})

    # Duplicates
    by_size = defaultdict(list)
    for f in all_files:
        try:
            by_size[f.stat().st_size].append(f)
        except OSError:
            pass
    hash_map = defaultdict(list)
    for size, group in by_size.items():
        if len(group) < 2:
            continue
        for f in group:
            h = _file_hash(f)
            if h:
                hash_map[h].append(f)
    dup_groups_raw = {h: fs for h, fs in hash_map.items() if len(fs) > 1}
    duplicates = []
    dup_groups_out = []
    for h, dups in sorted(dup_groups_raw.items(), key=lambda x: x[1][0].stat().st_size, reverse=True):
        group = []
        for i, f in enumerate(dups):
            entry = {"path": str(f), "name": f.name, "size": f.stat().st_size,
                     "is_original": i == 0}
            group.append(entry)
            if i > 0:
                duplicates.append(entry)
        dup_groups_out.append(group)

    # Stale (90+ days)
    now = time.time()
    stale = []
    for f in all_files:
        try:
            age = now - f.stat().st_mtime
            if age >= 90 * 86400:
                stale.append({"path": str(f), "name": f.name,
                              "size": f.stat().st_size, "age": age})
        except OSError:
            pass
    stale.sort(key=lambda x: x["age"], reverse=True)

    return {
        "junk": junk,
        "junk_size": sum(j["size"] for j in junk),
        "duplicates": duplicates,
        "dup_groups": dup_groups_out,
        "dup_size": sum(d["size"] for d in duplicates),
        "stale": stale,
        "stale_size": sum(s["size"] for s in stale),
        "total_reclaimable": sum(j["size"] for j in junk) + sum(d["size"] for d in duplicates),
        "total_with_stale": sum(j["size"] for j in junk) + sum(d["size"] for d in duplicates) + sum(s["size"] for s in stale),
        "scanned_dirs": SCAN_DIRS,
    }


def delete_files(paths, category="unknown"):
    """Delete files by path. Returns count deleted and bytes freed."""
    deleted = 0
    freed = 0
    names = []
    for p in paths:
        try:
            fp = Path(p)
            if not any(str(fp).startswith(d) for d in SCAN_DIRS):
                continue
            sz = fp.stat().st_size
            name = fp.name
            fp.unlink()
            deleted += 1
            freed += sz
            names.append(name)
        except OSError:
            pass
    if deleted > 0:
        save_reclaim_event(category, deleted, freed, names)
    return deleted, freed
