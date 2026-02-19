"""Auto-update mechanism for Antidetect Launcher."""

import json
import logging
import os
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request

logger = logging.getLogger(__name__)


def _resolve_current_version() -> str:
    try:
        return version("antidetect-launcher")
    except PackageNotFoundError:
        return "0.1.1"


class AutoUpdater:
    """Handles automatic updates for the application."""

    UPDATE_URL = "https://api.github.com/repos/arbitron-adm2/antidetect-launcher/releases/latest"
    CURRENT_VERSION = _resolve_current_version()
    USER_AGENT = f"Antidetect-Launcher/{CURRENT_VERSION}"

    def __init__(self, check_on_startup: bool = True):
        """Initialize auto-updater.

        Args:
            check_on_startup: Whether to check for updates on application startup
        """
        self.check_on_startup = check_on_startup
        self._update_available = False
        self._latest_version: Optional[str] = None
        self._download_url: Optional[str] = None

    def check_for_updates(self) -> dict:
        """Check if a new version is available.

        Returns:
            Dictionary with update information:
            - available: bool
            - current_version: str
            - latest_version: str
            - download_url: str (if available)
            - release_notes: str (if available)
        """
        try:
            # Fetch latest release info from GitHub
            req = Request(
                self.UPDATE_URL,
                headers={"User-Agent": self.USER_AGENT}
            )

            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())

            latest_version = data.get("tag_name", "").lstrip("v")
            self._latest_version = latest_version

            # Find Windows installer asset
            for asset in data.get("assets", []):
                if asset["name"].endswith("-Setup.exe"):
                    self._download_url = asset["browser_download_url"]
                    break

            # Compare versions
            self._update_available = self._is_newer_version(
                latest_version, self.CURRENT_VERSION
            )

            return {
                "available": self._update_available,
                "current_version": self.CURRENT_VERSION,
                "latest_version": latest_version,
                "download_url": self._download_url,
                "release_notes": data.get("body", ""),
            }

        except Exception as e:
            logger.warning(f"Failed to check for updates: {e}")
            return {
                "available": False,
                "current_version": self.CURRENT_VERSION,
                "latest_version": None,
                "error": str(e),
            }

    def download_update(self, progress_callback=None) -> Optional[Path]:
        """Download the latest update.

        Args:
            progress_callback: Optional callback function(bytes_downloaded, total_bytes)

        Returns:
            Path to downloaded installer or None if failed
        """
        if not self._download_url:
            logger.error("No download URL available")
            return None

        try:
            # Create temporary file for download
            temp_dir = Path(tempfile.gettempdir()) / "antidetect-launcher-updates"
            temp_dir.mkdir(exist_ok=True)

            installer_name = f"AntidetectLauncher-Setup-{self._latest_version}.exe"
            installer_path = temp_dir / installer_name

            # Download file
            req = Request(
                self._download_url,
                headers={"User-Agent": self.USER_AGENT}
            )

            with urlopen(req) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0

                with open(installer_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size:
                            progress_callback(downloaded, total_size)

            logger.info(f"Update downloaded to: {installer_path}")
            return installer_path

        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            return None

    def install_update(self, installer_path: Path) -> bool:
        """Install the downloaded update.

        Args:
            installer_path: Path to the installer executable

        Returns:
            True if installation started successfully
        """
        if not installer_path or not installer_path.exists():
            logger.error("Installer not found")
            return False

        try:
            # Launch installer with silent flag
            if sys.platform == "win32":
                # Run installer silently and exit current application
                subprocess.Popen(
                    [str(installer_path), "/SILENT", "/CLOSEAPPLICATIONS"],
                    creationflags=subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_NEW_PROCESS_GROUP,
                )

                # Schedule application exit
                logger.info("Update installation started, exiting application...")
                return True

            else:
                logger.warning("Auto-install only supported on Windows")
                return False

        except Exception as e:
            logger.error(f"Failed to install update: {e}")
            return False

    @staticmethod
    def _is_newer_version(latest: str, current: str) -> bool:
        """Compare version strings.

        Args:
            latest: Latest version string (e.g., "0.2.0")
            current: Current version string (e.g., "0.1.0")

        Returns:
            True if latest > current
        """
        try:
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]

            # Pad to same length
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)

            return latest_parts > current_parts

        except (ValueError, AttributeError):
            return False

    def get_update_preference(self) -> bool:
        """Get auto-update preference from registry (Windows).

        Returns:
            True if auto-updates are enabled
        """
        if sys.platform != "win32":
            return False

        try:
            import winreg

            # Try HKCU first, then HKLM
            for hive in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                try:
                    key = winreg.OpenKey(
                        hive, r"Software\Antidetect Team\Antidetect Launcher"
                    )
                    value, _ = winreg.QueryValueEx(key, "AutoUpdate")
                    winreg.CloseKey(key)
                    return bool(value)
                except FileNotFoundError:
                    continue

            # Default to enabled
            return True

        except Exception as e:
            logger.warning(f"Failed to read update preference: {e}")
            return True

    def set_update_preference(self, enabled: bool) -> bool:
        """Set auto-update preference in registry (Windows).

        Args:
            enabled: Whether to enable auto-updates

        Returns:
            True if preference was saved successfully
        """
        if sys.platform != "win32":
            return False

        try:
            import winreg

            # Save to HKCU
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Antidetect Team\Antidetect Launcher"
            )
            winreg.SetValueEx(key, "AutoUpdate", 0, winreg.REG_DWORD, int(enabled))
            winreg.CloseKey(key)

            logger.info(f"Auto-update preference set to: {enabled}")
            return True

        except Exception as e:
            logger.error(f"Failed to save update preference: {e}")
            return False
