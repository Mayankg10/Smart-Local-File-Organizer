# Smart Local File Organizer

A personal tool that keeps your Downloads and Desktop clean — automatically.

---

## What It Does

Your Downloads and Desktop folders get messy. PDFs, screenshots, zip files, random installers — everything piles up. This tool:

1. **Sorts files into folders** by type (Images, Documents, Videos, etc.)
2. **Finds and removes junk** (empty files, broken downloads, temp files)
3. **Detects duplicate files** so you can reclaim wasted space
4. **Runs automatically every week** so you never have to think about it
5. **Has a web dashboard** so you can see what's happening and control it from your browser

Everything runs locally on your Mac. No cloud, no accounts, no internet needed.

---

## How It Works

### File Organization

When you run the organizer on a folder (say `~/Downloads`), it:

1. **Scans** every file in the folder
2. **Categorizes** each file by its extension (`.pdf` → Documents, `.jpg` → Images, etc.)
3. **Detects screenshots** by name patterns ("Screenshot 2024-...", "CleanShot...", etc.) and groups them separately
4. **Creates an `Organized/` folder** inside the target directory
5. **Moves files** into subfolders like `Organized/Images/2026/03.28/photo.jpg`

The folder structure looks like:
```
Downloads/
  Organized/
    Images/
      2026/
        03.28/
          photo.jpg
          wallpaper.png
        03.15/
          old-pic.heic
    Documents/
      2026/
        03.28/
          report.pdf
          notes.txt
    Screenshots/
      2026/
        03.27/
          Screenshot 2026-03-27.png
    Videos/
      2025/
        12.10/
          demo.mp4
```

The year folder keeps things tidy over time, and the `MM.DD` subfolder tells you exactly when each file arrived.

### Smart Detection

The organizer doesn't just look at file extensions. It also:

- **Screenshot detection**: Recognizes files named "Screenshot...", "CleanShot...", "IMG_1234...", "Snip...", etc. Even though they're `.png` files, they get sorted into `Screenshots/` instead of `Images/`.
- **Junk detection**: Finds empty files (0 bytes), broken downloads (`.crdownload`, `.part`), temp files (`.tmp`, `.swp`), Office lock files (`~$...`), and OS metadata (`Thumbs.db`, `.DS_Store`).
- **Duplicate detection**: Groups files by size first (quick filter), then computes SHA-256 hashes of files that share the same size. If hashes match, they're duplicates. Only hashes the first 1MB of large files for speed.

### Filename Cleanup

Messy filenames like `report (1) copy (2).pdf` get cleaned to `report.pdf`. The cleanup removes:
- Copy suffixes: `(1)`, `(2)`, etc.
- "copy" / "Copy" text
- Extra spaces

This only happens when you use `--clean-names`. The organizer shows you what would change before doing anything.

### Safety Features

- **Dry-run by default**: Running the organizer without `--run` just shows a preview. Nothing moves.
- **Full undo**: Every operation is logged to `~/.file-organizer/history.json`. You can reverse any operation with `--undo`, or reverse everything with `--undo-all`.
- **No overwrites**: If a file with the same name already exists at the destination, it gets a number suffix (`file (1).pdf`).
- **History kept for 200 operations**: That's roughly 4 years of weekly runs.

---

## The CLI Tool (`organize.py`)

This is the command-line interface. You run it from your terminal.

### Basic Commands

```bash
# Preview what would happen (safe, moves nothing)
python3 ~/file-organizer/organize.py

# Actually organize the files
python3 ~/file-organizer/organize.py --run

# Organize Desktop instead of Downloads
python3 ~/file-organizer/organize.py --path ~/Desktop --run

# Approve each category before moving (interactive)
python3 ~/file-organizer/organize.py --interactive --run
```

### Analysis Commands

```bash
# Find duplicate files by content hash
python3 ~/file-organizer/organize.py --duplicates

# Find junk/temp/empty files
python3 ~/file-organizer/organize.py --junk

# Find files untouched for 30/90/180+ days
python3 ~/file-organizer/organize.py --stale

# Show top 20 largest files with visual bar chart
python3 ~/file-organizer/organize.py --large

# All-in-one disk space reclaimer (junk + duplicates + stale)
python3 ~/file-organizer/organize.py --reclaim
python3 ~/file-organizer/organize.py --reclaim --run  # interactive deletion

# View files grouped as Today / This Week / This Month / Older
python3 ~/file-organizer/organize.py --recency

# Full intelligence report with smart insights
python3 ~/file-organizer/organize.py --stats
```

### Undo & History

```bash
# Reverse the last organize operation
python3 ~/file-organizer/organize.py --undo

# Reverse ALL operations (back to original state)
python3 ~/file-organizer/organize.py --undo-all

# See all past operations
python3 ~/file-organizer/organize.py --history
```

### Watch Mode

```bash
# Auto-organize new files as they appear in Downloads
python3 ~/file-organizer/organize.py --watch
```

This polls the folder every 2 seconds. When a new file appears, it waits 1 second (for the file to finish writing), then organizes it.

---

## The Dashboard (`dashboard.py`)

A local web UI that runs at `http://localhost:8787`.

```bash
python3 ~/file-organizer/dashboard.py
```

It auto-opens in your browser and has 4 tabs:

### Overview Tab
- **Stat cards**: Total operations, files organized, categories, directories
- **Category breakdown**: Bar chart showing how many files per type
- **Monthly activity**: Column chart of files organized per month
- **Recent operations**: Last 10 runs with file name pills

### Reclaim Tab
- Click **"Scan Now"** to analyze Downloads & Desktop
- Shows 3 sections: Junk, Duplicates, Stale files
- Each section has a red **"Delete"** button with a confirmation dialog
- Shows total reclaimable space

### History Tab
- **Organize Timeline**: Every organize operation with visual bars
- **Reclaim History**: Every delete from the Reclaim tab, with category icons and space freed

### Logs Tab
- Weekly auto-organize logs (expandable, click to open)

### Action Buttons (top of every page)
- **▶ Run Now**: Organizes Downloads + Desktop immediately
- **↩ Undo Last**: Reverses the most recent operation
- **↩ Undo All**: Reverses everything

The dashboard auto-refreshes every 30 seconds. All data is read from `~/.file-organizer/`.

### How the Dashboard Works Technically

The dashboard is a single Python HTTP server (no frameworks, no dependencies). It:
1. Serves the HTML/CSS/JS as a single page
2. Exposes JSON API endpoints (`/api/stats`, `/api/logs`, `/api/reclaim/scan`, etc.)
3. The frontend fetches these APIs and renders the data
4. For "Run Now" and "Undo", it spawns the organizer CLI as a subprocess

---

## Weekly Auto-Organizer

A bash script (`auto-organize.sh`) runs every Sunday at 10 AM via macOS launchd:

1. Organizes `~/Downloads` with filename cleanup
2. Organizes `~/Desktop` with filename cleanup
3. Logs everything to `~/.file-organizer/logs/auto-organize-YYYY-MM-DD.log`
4. Sends a macOS notification: "Organized 47 files from Downloads & Desktop"
5. Cleans up logs older than 30 days

### The launchd Job

Located at `~/Library/LaunchAgents/com.mayank.file-organizer.plist`. This is macOS's built-in task scheduler (more reliable than cron). If your Mac was asleep at the scheduled time, it runs when the Mac wakes up.

**Manage it:**
```bash
# Stop the weekly schedule
launchctl unload ~/Library/LaunchAgents/com.mayank.file-organizer.plist

# Re-enable it
launchctl load ~/Library/LaunchAgents/com.mayank.file-organizer.plist
```

---

## macOS Notifications

Native macOS notifications fire in 3 situations:
1. After every `--run` organize → "Organized 47 files in Downloads"
2. After `--reclaim --run` → "Reclaimed 352.6 MB by removing 22 files"
3. After the weekly auto-run → "Organized 31 files from Downloads & Desktop"

Uses `osascript` under the hood (AppleScript). No extra permissions needed.

---

## File Categories

The organizer recognizes 13 file categories:

| Category | Example Extensions |
|---|---|
| Screenshots | Auto-detected by name pattern |
| Images | .jpg, .png, .gif, .heic, .svg, .webp, .raw |
| Documents | .pdf, .doc, .docx, .txt, .csv, .xls, .ppt |
| Videos | .mp4, .mov, .mkv, .avi, .webm |
| Music | .mp3, .wav, .flac, .aac, .m4a |
| Archives | .zip, .rar, .7z, .tar, .dmg, .iso |
| Code | .py, .js, .ts, .html, .css, .json, .sh, .go |
| Design | .psd, .ai, .sketch, .fig, .blend |
| Fonts | .ttf, .otf, .woff, .woff2 |
| Installers | .exe, .msi, .app, .apk |
| Ebooks | .epub, .mobi, .azw, .djvu |
| Data | .db, .sqlite, .parquet, .pickle, .log |
| Torrents | .torrent |

Anything that doesn't match goes into `Other/`.

---

## Project Structure

```
file-organizer/
  organize.py           # CLI entry point (131 lines)
  dashboard.py          # Web dashboard server (115 lines)
  auto-organize.sh      # Weekly automation script

  lib/                  # All logic lives here
    __init__.py
    config.py           # Constants: categories, patterns, colors, paths
    utils.py            # Shared helpers: detection, formatting, hashing, I/O
    core.py             # Core: scan files, plan moves, execute moves
    analyzers.py        # Smart features: duplicates, junk, stale, reclaim, stats
    history.py          # Undo, undo-all, history, watch mode
    dashboard_api.py    # Dashboard backend: APIs, reclaim, stats
    dashboard_html.py   # Dashboard frontend: HTML/CSS/JS template
```

### Data Files (in `~/.file-organizer/`)

| File | Purpose |
|---|---|
| `history.json` | Log of all organize operations (for undo) |
| `reclaim-history.json` | Log of all reclaim deletions |
| `logs/auto-organize-*.log` | Weekly auto-run output logs |

---

## Dependencies

**None.** Everything uses Python 3 standard library only. No pip install, no npm, no brew, nothing.

---

## Quick Start

```bash
# Preview your Downloads
python3 ~/file-organizer/organize.py

# Organize for real
python3 ~/file-organizer/organize.py --run

# Open the dashboard
python3 ~/file-organizer/dashboard.py

# The weekly auto-organizer is already running via launchd
```
