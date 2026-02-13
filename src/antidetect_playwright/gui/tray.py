"""System tray icon for Antidetect Browser."""

import logging
import sys
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

logger = logging.getLogger(__name__)


def find_icon(name: str) -> QIcon:
    """Find icon file from resources, handling dev and installed modes.

    Search order:
    1. PyInstaller bundle (_MEIPASS)
    2. Package resources (relative to this file)
    3. Project assets/ (dev mode)
    4. Build icons (PNG fallback)
    """
    candidates: list[Path] = []

    # 1. PyInstaller bundle
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", ""))
        candidates.append(meipass / "antidetect_playwright" / "resources" / name)

    # 2. Package resources
    resources_dir = Path(__file__).resolve().parent.parent / "resources"
    candidates.append(resources_dir / name)

    # 3. Project assets/ (dev mode)
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    candidates.append(project_root / "assets" / "icons" / name)

    # 4. Build icons PNG fallback
    candidates.append(project_root / "build" / "icons" / "linux" / "icon_128x128.png")

    for path in candidates:
        if path.exists():
            return QIcon(str(path))

    logger.warning("Icon not found: %s", name)
    return QIcon()


class SystemTray(QObject):
    """System tray icon with context menu.

    Provides:
    - Tray icon with tooltip
    - Show/Hide toggle via double-click or menu
    - Running browsers count in tooltip
    - Quit action (the only way to fully exit)
    """

    show_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._tray = QSystemTrayIcon(self)

        # Use Qt-compatible icon (no SVG filters)
        icon = find_icon("app-icon-256.svg")
        if icon.isNull():
            icon = find_icon("app-icon.svg")
        self._tray.setIcon(icon)
        self._tray.setToolTip("Antidetect Browser")

        # Context menu
        self._menu = QMenu()

        self._show_action = self._menu.addAction("Show / Hide")
        self._show_action.triggered.connect(self.show_requested.emit)

        self._menu.addSeparator()

        self._status_action = self._menu.addAction("No browsers running")
        self._status_action.setEnabled(False)

        self._menu.addSeparator()

        self._quit_action = self._menu.addAction("Quit")
        self._quit_action.triggered.connect(self.quit_requested.emit)

        self._tray.setContextMenu(self._menu)

        # Double-click to show/hide
        self._tray.activated.connect(self._on_activated)

    def show(self) -> None:
        """Show the tray icon."""
        self._tray.show()

    def hide(self) -> None:
        """Hide the tray icon."""
        self._tray.hide()

    def update_running_count(self, count: int) -> None:
        """Update tooltip and status with running browser count."""
        if count > 0:
            self._tray.setToolTip(f"Antidetect Browser — {count} running")
            self._status_action.setText(f"{count} browser{'s' if count != 1 else ''} running")
        else:
            self._tray.setToolTip("Antidetect Browser")
            self._status_action.setText("No browsers running")

    def show_message(
        self,
        title: str,
        message: str,
        icon_type=QSystemTrayIcon.MessageIcon.Information,
        duration: int = 3000,
    ) -> None:
        """Show a tray notification balloon."""
        self._tray.showMessage(title, message, icon_type, duration)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation (click/double-click)."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click on some platforms
            self.show_requested.emit()
