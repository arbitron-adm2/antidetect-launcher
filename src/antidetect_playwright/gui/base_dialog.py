"""Base dialog class with common functionality for all dialogs."""

from typing import Callable
from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt

from .styles import COLORS


class BaseDialog(QDialog):
    """Base dialog with common UI functionality.

    This class provides common dialog utilities like error handling,
    button row creation, and styling helpers.

    Attributes:
        _alert: Optional inline alert widget for showing errors/warnings.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize base dialog.

        Args:
            parent: Parent widget, if any.
        """
        super().__init__(parent)
        self.setModal(True)
        self._alert = None  # Subclasses can set this if needed

    def _set_error(self, widget: QWidget, is_error: bool) -> None:
        """Set error state on widget.

        Args:
            widget: Widget to set error state on.
            is_error: True to set error, False to clear.
        """
        widget.setProperty("error", "true" if is_error else "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _clear_error(self, widget: QWidget) -> None:
        """Clear error state from widget.

        Args:
            widget: Widget to clear error from.
        """
        self._set_error(widget, False)
        if self._alert is not None:
            self._alert.hide()

    def _create_button_row(
        self,
        save_text: str = "Save",
        save_callback: Callable[[], None] | None = None,
        cancel_callback: Callable[[], None] | None = None,
        primary_button: str = "save",  # "save" or "cancel"
    ) -> QHBoxLayout:
        """Create standard save/cancel button row.

        Args:
            save_text: Text for the save/action button.
            save_callback: Callback for save button click.
            cancel_callback: Callback for cancel button click.
            primary_button: Which button should have primary styling.

        Returns:
            QHBoxLayout containing the button row.
        """
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(cancel_callback or self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton(save_text)
        if primary_button == "save":
            save_btn.setStyleSheet(
                f"background-color: {COLORS['accent']}; color: white; font-weight: 600;"
            )
        save_btn.clicked.connect(save_callback or self.accept)
        btn_layout.addWidget(save_btn)

        return btn_layout

    def _setup_standard_dialog(
        self,
        title: str,
        min_width: int = 400,
        min_height: int | None = None,
    ) -> QVBoxLayout:
        """Setup standard dialog properties and return main layout.

        Args:
            title: Dialog window title.
            min_width: Minimum dialog width in pixels.
            min_height: Minimum dialog height in pixels (optional).

        Returns:
            QVBoxLayout to use as main dialog layout.
        """
        self.setWindowTitle(title)
        self.setMinimumWidth(min_width)
        if min_height is not None:
            self.setMinimumHeight(min_height)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        return layout
