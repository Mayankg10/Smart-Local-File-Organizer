#!/bin/bash
# ─────────────────────────────────────────────
# Smart Local File Organizer — Installer
# ─────────────────────────────────────────────
# Usage:
#   git clone https://github.com/Mayankg10/Smart-Local-File-Organizer.git ~/file-organizer
#   bash ~/file-organizer/install.sh
# ─────────────────────────────────────────────

set -euo pipefail

INSTALL_DIR="$HOME/file-organizer"
PLIST_NAME="com.user.file-organizer"
PLIST_SRC="$INSTALL_DIR/com.user.file-organizer.plist"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║  Smart Local File Organizer — Installer  ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "  ✗ Python 3 is required but not found."
    echo "    Install it: https://www.python.org/downloads/"
    exit 1
fi
echo "  ✓ Python 3 found: $(python3 --version)"

# Check the repo exists
if [ ! -f "$INSTALL_DIR/organize.py" ]; then
    echo "  ✗ organize.py not found in $INSTALL_DIR"
    echo "    Run: git clone https://github.com/Mayankg10/Smart-Local-File-Organizer.git ~/file-organizer"
    exit 1
fi
echo "  ✓ Project found at $INSTALL_DIR"

# Quick test that imports work
if python3 -c "import sys; sys.path.insert(0,'$INSTALL_DIR'); from lib.config import C" 2>/dev/null; then
    echo "  ✓ Python imports OK"
else
    echo "  ✗ Python import test failed"
    exit 1
fi

# Make scripts executable
chmod +x "$INSTALL_DIR/organize.py"
chmod +x "$INSTALL_DIR/dashboard.py"
chmod +x "$INSTALL_DIR/auto-organize.sh"
echo "  ✓ Scripts made executable"

# Create data directory
mkdir -p "$HOME/.file-organizer/logs"
echo "  ✓ Data directory created at ~/.file-organizer"

# ─── Setup weekly auto-organizer ───
echo ""
read -p "  ? Set up weekly auto-organizer (Sundays 10 AM)? [Y/n] " SETUP_AUTO
SETUP_AUTO=${SETUP_AUTO:-Y}

if [[ "$SETUP_AUTO" =~ ^[Yy]$ ]]; then
    # Unload existing job if present
    launchctl unload "$PLIST_DST" 2>/dev/null || true

    # Create personalized plist (replace YOUR_USERNAME with actual username)
    sed "s|YOUR_USERNAME|$(whoami)|g" "$PLIST_SRC" > "$PLIST_DST"

    # Load the job
    launchctl load "$PLIST_DST"
    echo "  ✓ Weekly auto-organizer installed"
    echo "    Runs every Sunday at 10 AM"
    echo "    Manage: launchctl unload $PLIST_DST"
else
    echo "  ⊘ Skipped auto-organizer setup"
fi

# ─── Done ───
echo ""
echo "  ─────────────────────────────────────────"
echo "  ✓ Installation complete!"
echo ""
echo "  Quick start:"
echo "    python3 ~/file-organizer/organize.py              # Preview Downloads"
echo "    python3 ~/file-organizer/organize.py --run         # Organize for real"
echo "    python3 ~/file-organizer/organize.py --stats       # Intelligence report"
echo "    python3 ~/file-organizer/organize.py --reclaim     # Find reclaimable space"
echo "    python3 ~/file-organizer/dashboard.py              # Open web dashboard"
echo ""
echo "  Tip: Add an alias to your shell config:"
echo "    echo 'alias organizer=\"python3 ~/file-organizer/organize.py\"' >> ~/.zshrc"
echo ""
