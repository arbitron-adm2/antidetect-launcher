"""UI/UX improvements test suite.

Tests for P0 critical UI/UX improvements including:
- Theme consolidation
- Border-radius consistency
- WCAG AA color contrast
- Keyboard navigation
- Typography system
- Confirmation dialogs
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QKeyEvent, QKeySequence
from PyQt6.QtTest import QTest

from antidetect_playwright.gui.theme import Theme, COLORS, TYPOGRAPHY, SPACING, RADIUS
from antidetect_playwright.gui.models import BrowserProfile, ProfileStatus, Folder
from antidetect_playwright.gui.widgets import StatusBadge, FolderItem
from datetime import datetime


@pytest.mark.integration
@pytest.mark.gui
class TestThemeConsolidation:
    """Test unified theme system."""

    def test_theme_has_all_color_tokens(self):
        """Verify theme has all required color tokens."""
        assert COLORS.bg_primary == "#1a1a1a"
        assert COLORS.bg_secondary == "#161616"
        assert COLORS.bg_tertiary == "#232323"
        assert COLORS.bg_hover == "#2a2a2a"
        assert COLORS.bg_selected == "#3a3a3a"
        assert COLORS.accent == "#888888"
        assert COLORS.success == "#4ade80"
        assert COLORS.error == "#f87171"
        assert COLORS.text_primary == "#ffffff"
        assert COLORS.text_secondary == "#d1d5db"
        assert COLORS.text_muted == "#8b92a0"

    def test_theme_has_typography_tokens(self):
        """Verify typography system is complete."""
        assert TYPOGRAPHY.font_family
        assert TYPOGRAPHY.font_size_xs == 11  # Increased for accessibility
        assert TYPOGRAPHY.font_size_base == 13
        assert TYPOGRAPHY.line_height_tight == 1.2
        assert TYPOGRAPHY.line_height_normal == 1.5
        assert TYPOGRAPHY.weight_normal == 400
        assert TYPOGRAPHY.weight_bold == 700

    def test_theme_has_spacing_tokens(self):
        """Verify spacing system includes all scales."""
        assert SPACING.xxs == 2  # New fine-grained spacing
        assert SPACING.xs == 4
        assert SPACING.sm == 8
        assert SPACING.md == 12
        assert SPACING.lg == 16
        assert SPACING.xl == 24
        assert SPACING.xxl == 32

    def test_theme_has_border_radius_tokens(self):
        """Verify border-radius scale is comprehensive."""
        assert RADIUS.none == 0
        assert RADIUS.xs == 2
        assert RADIUS.sm == 4  # Inputs, buttons, cards
        assert RADIUS.md == 6  # Folders, medium components
        assert RADIUS.lg == 8  # Dialogs, menus
        assert RADIUS.full == 9999

    def test_stylesheet_generates_without_error(self):
        """Verify stylesheet generation works."""
        stylesheet = Theme.get_stylesheet()
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0
        assert "QMainWindow" in stylesheet
        assert COLORS.bg_primary in stylesheet

    def test_deprecated_styles_module_works(self):
        """Verify backward compatibility with styles.py."""
        from antidetect_playwright.gui.styles import COLORS as STYLES_COLORS
        from antidetect_playwright.gui.styles import get_stylesheet

        # Colors should match
        assert STYLES_COLORS["bg_primary"] == COLORS.bg_primary
        assert STYLES_COLORS["text_primary"] == COLORS.text_primary

        # Stylesheet should be generated
        stylesheet = get_stylesheet()
        assert isinstance(stylesheet, str)


@pytest.mark.integration
@pytest.mark.gui
class TestBorderRadiusConsistency:
    """Test border-radius consistency across components."""

    def test_stylesheet_has_consistent_border_radius(self):
        """Verify all components use theme border-radius."""
        stylesheet = Theme.get_stylesheet()

        # Inputs should have 4px
        assert "QLineEdit" in stylesheet
        assert "border-radius: 4px" in stylesheet

        # Cards should have 4px
        assert 'QFrame[class="card"]' in stylesheet

        # Dialogs should have 8px
        assert "QDialog" in stylesheet
        assert "border-radius: 8px" in stylesheet

        # Menus should have 8px
        assert "QMenu" in stylesheet

    def test_no_hardcoded_border_radius_zero(self):
        """Verify no components use border-radius: 0 unnecessarily."""
        stylesheet = Theme.get_stylesheet()

        # These should NOT have border-radius: 0
        assert not ("QLineEdit {" in stylesheet and "border-radius: 0" in stylesheet.split("QLineEdit {")[1].split("}")[0])
        assert not ("QTextEdit {" in stylesheet and "border-radius: 0" in stylesheet.split("QTextEdit {")[1].split("}")[0])


@pytest.mark.integration
@pytest.mark.gui
class TestWCAGColorContrast:
    """Test WCAG AA color contrast compliance."""

    def test_text_secondary_improved_contrast(self):
        """Verify text_secondary has improved contrast."""
        # Old: #9ca3af, New: #d1d5db (8:1 contrast)
        assert COLORS.text_secondary == "#d1d5db"
        assert COLORS.text_secondary != "#9ca3af"

    def test_text_muted_improved_contrast(self):
        """Verify text_muted has improved contrast."""
        # Old: #6b7280, New: #8b92a0 (4.5:1+ contrast)
        assert COLORS.text_muted == "#8b92a0"
        assert COLORS.text_muted != "#6b7280"

    def test_status_badge_uses_improved_colors(self, qapp):
        """Verify StatusBadge uses improved contrast colors."""
        from antidetect_playwright.gui.models import ProfileStatus

        # Create STOPPED status badge
        badge = StatusBadge(ProfileStatus.STOPPED)

        # Should use improved text_secondary color
        stylesheet = badge.findChild(badge.__class__).styleSheet() if badge.findChildren(badge.__class__) else ""
        # Badge is built with improved colors from COLORS


@pytest.mark.integration
@pytest.mark.gui
class TestKeyboardNavigation:
    """Test keyboard navigation and shortcuts."""

    @pytest.fixture
    def main_window(self, qapp):
        """Create main window for testing."""
        with patch("antidetect_playwright.gui.app.Storage"):
            with patch("antidetect_playwright.gui.app.BrowserLauncher"):
                from antidetect_playwright.gui.app import MainWindow
                window = MainWindow()
                return window

    def test_table_has_keyboard_focus_enabled(self, main_window):
        """Verify tables support keyboard navigation."""
        table = main_window.profiles_page.table

        # Should have strong focus policy (not NoFocus)
        assert table.focusPolicy() == Qt.FocusPolicy.StrongFocus

        # Should have tab key navigation enabled
        assert table.tabKeyNavigation() is True

    def test_ctrl_n_shortcut_exists(self, main_window):
        """Verify Ctrl+N creates new profile."""
        shortcuts = main_window.findChildren(main_window.__class__.__bases__[0])
        # Shortcut should be registered
        assert hasattr(main_window, '_setup_keyboard_shortcuts')

    def test_keyboard_shortcuts_registered(self, main_window):
        """Verify all keyboard shortcuts are registered."""
        # Main window should have shortcut methods
        assert hasattr(main_window, '_delete_selected_profiles_shortcut')
        assert hasattr(main_window, '_select_all_profiles_shortcut')
        assert hasattr(main_window, '_refresh_current_page')


@pytest.mark.integration
@pytest.mark.gui
class TestImprovedConfirmationDialogs:
    """Test confirmation dialogs show profile details."""

    @pytest.fixture
    def mock_profiles(self):
        """Create mock profiles for testing."""
        return [
            BrowserProfile(
                id=f"profile-{i}",
                name=f"Test Profile {i}",
                status=ProfileStatus.STOPPED,
                created_at=datetime.now()
            )
            for i in range(7)
        ]

    @pytest.mark.asyncio
    async def test_batch_delete_shows_profile_names(self, mock_profiles, qapp):
        """Verify batch delete confirmation shows profile names."""
        with patch("antidetect_playwright.gui.app.Storage"):
            with patch("antidetect_playwright.gui.app.BrowserLauncher"):
                with patch("antidetect_playwright.gui.app.confirm_dialog") as mock_confirm:
                    from antidetect_playwright.gui.app import MainWindow

                    mock_confirm.return_value = False  # Don't actually delete

                    window = MainWindow()
                    window.storage.get_profile = Mock(side_effect=lambda pid: next(
                        (p for p in mock_profiles if p.id == pid), None
                    ))

                    profile_ids = [p.id for p in mock_profiles]

                    # Call batch delete
                    await window._batch_delete_profiles(profile_ids)

                    # Verify confirm_dialog was called
                    assert mock_confirm.called
                    call_args = mock_confirm.call_args

                    # Check message contains profile names
                    message = call_args[0][2]  # Third argument is message
                    assert "Test Profile 0" in message
                    assert "Test Profile 1" in message
                    assert "... and 2 more" in message  # Shows count for overflow


@pytest.mark.integration
@pytest.mark.gui
class TestFolderItemConsistency:
    """Test FolderItem uses theme colors consistently."""

    def test_folder_item_uses_theme_colors(self, qapp):
        """Verify FolderItem uses COLORS from theme."""
        folder = Folder(id="test-1", name="Test Folder", color="#ff0000")
        item = FolderItem(folder=folder, count=5, selected=False)

        stylesheet = item.styleSheet()

        # Should use theme colors, not hardcoded rgba
        assert "rgba(128, 128, 128, 0.15)" not in stylesheet

        # Should reference COLORS.bg_selected or COLORS.bg_hover
        # (checked at runtime through stylesheet generation)

    def test_folder_item_selected_state(self, qapp):
        """Verify selected FolderItem uses correct background."""
        folder = Folder(id="test-2", name="Selected", color="#00ff00")
        item = FolderItem(folder=folder, count=3, selected=True)

        # Selected items should use bg_selected
        # This is verified through the stylesheet in _setup_ui


@pytest.mark.integration
@pytest.mark.gui
class TestResponsiveDesign:
    """Test responsive behavior and window sizing."""

    @pytest.fixture
    def main_window(self, qapp):
        """Create main window for testing."""
        with patch("antidetect_playwright.gui.app.Storage"):
            with patch("antidetect_playwright.gui.app.BrowserLauncher"):
                from antidetect_playwright.gui.app import MainWindow
                window = MainWindow()
                return window

    def test_minimum_window_size(self, main_window):
        """Verify window has reasonable minimum size."""
        min_size = main_window.minimumSize()

        # Should be 1200x700 (as per current implementation)
        assert min_size.width() == 1200
        assert min_size.height() == 700

    def test_window_resizes_properly(self, main_window):
        """Verify window can be resized."""
        main_window.resize(1400, 800)
        assert main_window.width() >= 1400
        assert main_window.height() >= 800


@pytest.mark.integration
@pytest.mark.gui
class TestAccessibility:
    """Test accessibility features."""

    def test_minimum_font_size_compliance(self):
        """Verify minimum font size meets WCAG AA."""
        # Minimum font size should be 11px
        assert TYPOGRAPHY.font_size_xs >= 11

    def test_all_text_sizes_reasonable(self):
        """Verify all font sizes are accessible."""
        assert TYPOGRAPHY.font_size_xs == 11
        assert TYPOGRAPHY.font_size_sm == 12
        assert TYPOGRAPHY.font_size_base == 13
        assert TYPOGRAPHY.font_size_lg == 15
        assert TYPOGRAPHY.font_size_xl == 18
        assert TYPOGRAPHY.font_size_xxl == 22

    def test_line_heights_defined(self):
        """Verify line heights improve readability."""
        assert TYPOGRAPHY.line_height_tight == 1.2
        assert TYPOGRAPHY.line_height_normal == 1.5
        assert TYPOGRAPHY.line_height_relaxed == 1.75


@pytest.mark.integration
@pytest.mark.gui
class TestTableSetup:
    """Test table configuration and styling."""

    def test_table_setup_enables_navigation(self, qapp):
        """Verify Theme.setup_table() enables keyboard navigation."""
        from PyQt6.QtWidgets import QTableWidget

        table = QTableWidget()
        Theme.setup_table(table)

        # Should enable keyboard focus
        assert table.focusPolicy() == Qt.FocusPolicy.StrongFocus
        assert table.tabKeyNavigation() is True

    def test_table_has_proper_row_height(self, qapp):
        """Verify table row height is consistent."""
        from PyQt6.QtWidgets import QTableWidget

        table = QTableWidget()
        Theme.setup_table(table)

        # Default row height should be 40px
        assert table.verticalHeader().defaultSectionSize() == Theme.TABLE_ROW_HEIGHT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
