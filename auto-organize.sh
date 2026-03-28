#!/bin/bash
# Auto-organize Downloads and Desktop folders
# Runs via launchd weekly — logs output for review

LOG_DIR="$HOME/.file-organizer/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/auto-organize-$(date +%Y-%m-%d).log"
ORGANIZER="$HOME/file-organizer/organize.py"

echo "═══════════════════════════════════════════" >> "$LOG_FILE"
echo "Auto-organize started: $(date)" >> "$LOG_FILE"
echo "═══════════════════════════════════════════" >> "$LOG_FILE"

# Organize Downloads
echo "" >> "$LOG_FILE"
echo "── Downloads ──" >> "$LOG_FILE"
/usr/bin/python3 "$ORGANIZER" --path ~/Downloads --run --clean-names >> "$LOG_FILE" 2>&1

# Organize Desktop
echo "" >> "$LOG_FILE"
echo "── Desktop ──" >> "$LOG_FILE"
/usr/bin/python3 "$ORGANIZER" --path ~/Desktop --run --clean-names >> "$LOG_FILE" 2>&1

echo "" >> "$LOG_FILE"
echo "Completed: $(date)" >> "$LOG_FILE"

# Count files moved from the log (grep for success lines)
FILES_MOVED=$(grep -c '✓' "$LOG_FILE" 2>/dev/null || echo "0")

# Send macOS notification with summary
if [ "$FILES_MOVED" -gt 0 ] 2>/dev/null; then
  osascript -e "display notification \"Organized $FILES_MOVED files from Downloads & Desktop\" with title \"📂 Weekly File Organizer\""
else
  osascript -e 'display notification "No new files to organize this week" with title "📂 Weekly File Organizer"'
fi

# Clean up logs older than 30 days
find "$LOG_DIR" -name "auto-organize-*.log" -mtime +30 -delete 2>/dev/null
