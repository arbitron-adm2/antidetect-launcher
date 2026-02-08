"""Constants used throughout the GUI application."""

from typing import Final

# UI Constants
WINDOW_MIN_WIDTH: Final[int] = 1200
WINDOW_MIN_HEIGHT: Final[int] = 700

# Auto-collapse sidebar thresholds
SIDEBAR_COLLAPSE_WIDTH: Final[int] = 1400
SIDEBAR_EXPAND_WIDTH: Final[int] = 1500

# Pagination
DEFAULT_ITEMS_PER_PAGE: Final[int] = 50
ITEMS_PER_PAGE_OPTIONS: Final[list[int]] = [25, 50, 100, 200]

# Performance
BATCH_START_CONCURRENCY_LIMIT: Final[int] = 5  # Max simultaneous browser starts
BATCH_PING_CONCURRENCY_LIMIT: Final[int] = 10  # Max simultaneous proxy pings
SEARCH_DEBOUNCE_MS: Final[int] = 300  # Search input debounce delay

# Validation
MAX_PROFILE_NAME_LENGTH: Final[int] = 100
MAX_FOLDER_NAME_LENGTH: Final[int] = 50
MAX_TAG_NAME_LENGTH: Final[int] = 30
MAX_NOTE_LENGTH: Final[int] = 10000
MAX_PROXY_STRING_LENGTH: Final[int] = 500

# Table Display
MAX_COOKIE_VALUE_DISPLAY_LENGTH: Final[int] = 50
MAX_URL_DISPLAY_LENGTH: Final[int] = 80
MAX_HISTORY_ENTRIES: Final[int] = 200
MAX_COOKIES_DISPLAY: Final[int] = 500

# Proxy Types
ALLOWED_PROXY_TYPES: Final[set[str]] = {"http", "https", "socks5"}

# File Paths
BROWSER_DATA_DIR: Final[str] = "data/browser_data"
STORAGE_DIR: Final[str] = "data"

# Dialog Sizes
DIALOG_MIN_WIDTH_SMALL: Final[int] = 350
DIALOG_MIN_WIDTH_MEDIUM: Final[int] = 450
DIALOG_MIN_WIDTH_LARGE: Final[int] = 650
DIALOG_MIN_HEIGHT_SMALL: Final[int] = 300
DIALOG_MIN_HEIGHT_MEDIUM: Final[int] = 400
DIALOG_MIN_HEIGHT_LARGE: Final[int] = 550

# Folder Colors (name, hex)
FOLDER_COLORS: Final[list[tuple[str, str]]] = [
    ("#6366f1", "Indigo"),
    ("#ec4899", "Pink"),
    ("#22c55e", "Green"),
    ("#f59e0b", "Orange"),
    ("#3b82f6", "Blue"),
    ("#8b5cf6", "Purple"),
    ("#14b8a6", "Teal"),
    ("#f43f5e", "Rose"),
]

# Status Colors
STATUS_COLORS: Final[list[str]] = ["green", "red", "yellow", "blue", "gray"]

# OS Types
SUPPORTED_OS_TYPES: Final[list[str]] = ["macOS", "Windows", "Linux"]
OS_TYPE_MAP: Final[dict[str, int]] = {"macos": 0, "windows": 1, "linux": 2}
OS_INDEX_MAP: Final[dict[int, str]] = {0: "macos", 1: "windows", 2: "linux"}

# Alert TTL
DEFAULT_ALERT_TTL_MS: Final[int] = 3000

# Icons
ICON_SIZE_SMALL: Final[int] = 14
ICON_SIZE_MEDIUM: Final[int] = 16
ICON_SIZE_LARGE: Final[int] = 24
