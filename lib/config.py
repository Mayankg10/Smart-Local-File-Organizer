"""Configuration constants, patterns, and colors."""

from pathlib import Path

# ─── File Categories ──────────────────────────────────────────────────────────

CATEGORIES = {
    "Screenshots": {"extensions": [], "icon": "📸"},
    "Images": {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
                       ".tiff", ".tif", ".ico", ".heic", ".heif", ".raw", ".cr2",
                       ".nef", ".arw"],
        "icon": "🖼️ ",
    },
    "Documents": {
        "extensions": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages",
                       ".tex", ".epub", ".md", ".csv", ".xls", ".xlsx", ".ppt",
                       ".pptx", ".ods", ".odp", ".key", ".numbers"],
        "icon": "📄",
    },
    "Videos": {
        "extensions": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm",
                       ".m4v", ".mpg", ".mpeg", ".3gp"],
        "icon": "🎬",
    },
    "Music": {
        "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
                       ".aiff", ".alac", ".opus"],
        "icon": "🎵",
    },
    "Archives": {
        "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
                       ".dmg", ".iso", ".pkg", ".deb", ".rpm", ".tgz"],
        "icon": "📦",
    },
    "Code": {
        "extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css",
                       ".scss", ".json", ".xml", ".yaml", ".yml", ".sh", ".bash",
                       ".zsh", ".rb", ".go", ".rs", ".c", ".cpp", ".h", ".hpp",
                       ".java", ".kt", ".swift", ".sql", ".r", ".php", ".lua",
                       ".pl", ".ex", ".exs", ".hs", ".toml", ".ini", ".cfg",
                       ".env", ".gitignore", ".dockerfile", ".ipynb"],
        "icon": "💻",
    },
    "Design": {
        "extensions": [".psd", ".ai", ".sketch", ".fig", ".xd", ".indd",
                       ".afdesign", ".afphoto", ".blend", ".obj", ".fbx",
                       ".stl", ".3ds"],
        "icon": "🎨",
    },
    "Fonts": {"extensions": [".ttf", ".otf", ".woff", ".woff2", ".eot"], "icon": "🔤"},
    "Installers": {"extensions": [".exe", ".msi", ".app", ".apk", ".ipa"], "icon": "⚙️ "},
    "Ebooks": {
        "extensions": [".epub", ".mobi", ".azw", ".azw3", ".djvu", ".cbr", ".cbz"],
        "icon": "📚",
    },
    "Data": {
        "extensions": [".db", ".sqlite", ".sqlite3", ".bak", ".dat", ".log",
                       ".parquet", ".feather", ".hdf5", ".h5", ".npy", ".npz",
                       ".pickle", ".pkl"],
        "icon": "🗃️ ",
    },
    "Torrents": {"extensions": [".torrent", ".magnet"], "icon": "🔗"},
}

# ─── Detection Patterns ──────────────────────────────────────────────────────

JUNK_EXTENSIONS = {".crdownload", ".part", ".download", ".tmp", ".temp",
                   ".bak", ".old", ".swp", ".swo", ".cache"}

JUNK_PATTERNS = [
    r"^~\$", r"^\.~lock\.", r"\.tmp$",
    r"^thumbs\.db$", r"^desktop\.ini$", r"^\\.ds_store$",
]

SCREENSHOT_PATTERNS = [
    r"^screenshot", r"^screen\s*shot", r"^capture",
    r"^screen\s*recording", r"^screen\s*capture",
    r"^CleanShot", r"^Snip", r"^IMG_\d+", r"^Image\s+\d+",
    r"^\d{4}-\d{2}-\d{2}\s+at\s+\d+\.\d+",
]

CLEANUP_PATTERNS = [
    (r"\s*\(\d+\)\s*(?=\.)", ""),
    (r"\s*copy\s*\d*\s*(?=\.)", ""),
    (r"\s*-\s*Copy\s*(?:\(\d+\))?\s*(?=\.)", ""),
    (r"\s+", " "),
    (r"^\s+|\s+$", ""),
]

# ─── Colors ───────────────────────────────────────────────────────────────────

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    UNDER   = "\033[4m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    GRAY    = "\033[90m"

# ─── Paths ────────────────────────────────────────────────────────────────────

LOG_DIR = Path.home() / ".file-organizer"
LOG_FILE = LOG_DIR / "history.json"
RECLAIM_HISTORY_FILE = LOG_DIR / "reclaim-history.json"
SCAN_DIRS = [str(Path.home() / "Downloads"), str(Path.home() / "Desktop")]
