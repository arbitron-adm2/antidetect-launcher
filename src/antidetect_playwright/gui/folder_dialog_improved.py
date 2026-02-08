"""Folder management dialog with improved architecture."""

from typing import Final
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QWidget,
)
from PyQt6.QtGui import QColor, QPixmap, QIcon

from .base_dialog import BaseDialog
from .models import Folder
from .styles import COLORS
from .constants import FOLDER_COLORS, DIALOG_MIN_WIDTH_SMALL
from .validation import validate_folder_name
from .components import InlineAlert, make_combobox_searchable


class FolderDialog(BaseDialog):
    """Dialog for creating or editing a folder.

    This dialog allows users to set folder name and color.
    Uses base dialog for common functionality.

    Attributes:
        folder: Folder instance being edited or created.
    """

    def __init__(self, folder: Folder | None = None, parent: QWidget | None = None) -> None:
        """Initialize folder dialog.

        Args:
            folder: Existing folder to edit, or None for new folder.
            parent: Parent widget, if any.
        """
        super().__init__(parent)
        self.folder: Folder = folder or Folder()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        """Setup dialog UI components."""
        # Setup dialog properties
        title = "Edit Folder" if self.folder.name and self.folder.name != "New Folder" else "New Folder"
        layout = self._setup_standard_dialog(title, DIALOG_MIN_WIDTH_SMALL)

        # Alert widget
        self._alert = InlineAlert(self)
        layout.addWidget(self._alert)

        # Name input
        layout.addWidget(QLabel("Folder Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Folder name")
        self.name_input.textChanged.connect(
            lambda _t: self._clear_error(self.name_input)
        )
        layout.addWidget(self.name_input)

        # Color selection
        layout.addWidget(QLabel("Color:"))
        self.color_combo = self._create_color_combobox()
        layout.addWidget(self.color_combo)

        # Buttons
        btn_layout = self._create_button_row(
            save_text="Save",
            save_callback=self._save,
        )
        layout.addLayout(btn_layout)

    def _create_color_combobox(self) -> QComboBox:
        """Create color selection combobox.

        Returns:
            QComboBox populated with folder colors.
        """
        combo = QComboBox()

        for color_hex, color_name in FOLDER_COLORS:
            # Create colored icon
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(color_hex))
            icon = QIcon(pixmap)
            combo.addItem(icon, color_name, color_hex)

        make_combobox_searchable(combo, "Search color")
        combo.setStyleSheet("QComboBox::item { padding: 4px 8px; }")

        return combo

    def _load_data(self) -> None:
        """Load existing folder data into form fields."""
        # Set name (clear "New Folder" default)
        if self.folder.name and self.folder.name != "New Folder":
            self.name_input.setText(self.folder.name)

        # Set color
        for i, (color_hex, _) in enumerate(FOLDER_COLORS):
            if color_hex == self.folder.color:
                self.color_combo.setCurrentIndex(i)
                break

    def _save(self) -> None:
        """Validate and save folder data."""
        name = self.name_input.text().strip()

        # Validate name
        is_valid, error_msg = validate_folder_name(name)
        if not is_valid:
            self._set_error(self.name_input, True)
            if self._alert:
                self._alert.show_error("Validation Error", error_msg)
            return

        # Update folder object
        self.folder.name = name
        self.folder.color = self.color_combo.currentData()

        # Accept dialog
        self.accept()

    def get_folder(self) -> Folder:
        """Get the folder instance.

        Returns:
            Folder instance with updated data.
        """
        return self.folder
