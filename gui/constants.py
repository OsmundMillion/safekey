from pathlib import Path

ACCENT_COLOR = "#00c9a7"
SIDEBAR_BG   = "#1e1e1e"
HOVER_BG     = "#046958"

BASE_DIR   = Path(__file__).resolve().parent
ASSETS_DIR = (BASE_DIR / ".." / "assets").resolve()
ICON_DIR   = ASSETS_DIR / "icons"
FONT_S     = ("Segoe UI", 12)
FONT_M     = ("Segoe UI", 14)
FONT_L     = ("Segoe UI", 20, "bold")

ICON_DIR   = Path(__file__).resolve().parent / ".." / "assets" / "icons"
APP_ICON   = ICON_DIR / "app_icon.ico"