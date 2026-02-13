"""Auto-update checker for Antidetect Launcher."""

import asyncio
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class UpdateChecker:
    """Check for application updates."""

    UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/antidetect/antidetect-launcher/main/update-manifest.json"
    CHECK_INTERVAL = 3600  # 1 hour

    def __init__(self, current_version: str, data_dir: Path):
        """Initialize update checker.

        Args:
            current_version: Current application version (e.g., "0.1.0")
            data_dir: Directory for storing update data
        """
        self.current_version = current_version
        self.data_dir = data_dir
        self.update_cache = data_dir / "update_cache.json"

    async def check_for_updates(self) -> Optional[dict]:
        """Check if updates are available.

        Returns:
            Update info dict if available, None otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.UPDATE_MANIFEST_URL, timeout=10) as resp:
                    if resp.status != 200:
                        logger.warning(f"Failed to fetch update manifest: {resp.status}")
                        return None

                    manifest = await resp.json()

            # Compare versions
            latest_version = manifest.get("version", "0.0.0")
            if self._is_newer_version(latest_version, self.current_version):
                logger.info(f"Update available: {latest_version}")
                return {
                    "version": latest_version,
                    "release_notes_url": manifest.get("release_notes_url"),
                    "download_url": self._get_platform_download_url(manifest),
                }

            logger.debug("No updates available")
            return None

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None

    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings.

        Args:
            latest: Latest version string
            current: Current version string

        Returns:
            True if latest is newer
        """
        try:
            latest_parts = tuple(map(int, latest.split(".")))
            current_parts = tuple(map(int, current.split(".")))
            return latest_parts > current_parts
        except ValueError:
            return False

    def _get_platform_download_url(self, manifest: dict) -> Optional[str]:
        """Get download URL for current platform.

        Args:
            manifest: Update manifest

        Returns:
            Download URL or None
        """
        import sys

        platforms = manifest.get("platforms", {})

        if sys.platform == "win32":
            return platforms.get("windows", {}).get("url")
        elif sys.platform == "darwin":
            return platforms.get("macos", {}).get("url")
        else:
            return platforms.get("linux", {}).get("url")

    async def download_update(self, update_info: dict, progress_callback=None) -> Optional[Path]:
        """Download update file.

        Args:
            update_info: Update information from check_for_updates
            progress_callback: Optional callback for progress (bytes_downloaded, total_bytes)

        Returns:
            Path to downloaded file or None
        """
        download_url = update_info.get("download_url")
        if not download_url:
            logger.error("No download URL in update info")
            return None

        try:
            # Create downloads directory
            downloads_dir = self.data_dir / "downloads"
            downloads_dir.mkdir(exist_ok=True)

            # Extract filename from URL
            filename = download_url.split("/")[-1]
            download_path = downloads_dir / filename

            logger.info(f"Downloading update from {download_url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as resp:
                    if resp.status != 200:
                        logger.error(f"Download failed: {resp.status}")
                        return None

                    total_size = int(resp.headers.get("content-length", 0))
                    downloaded = 0

                    with open(download_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback:
                                progress_callback(downloaded, total_size)

            logger.info(f"Update downloaded to {download_path}")
            return download_path

        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return None

    def verify_download(self, file_path: Path, expected_sha256: str) -> bool:
        """Verify downloaded file integrity.

        Args:
            file_path: Path to downloaded file
            expected_sha256: Expected SHA256 hash

        Returns:
            True if hash matches
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            actual_hash = sha256_hash.hexdigest()
            if actual_hash == expected_sha256:
                logger.info("Download verification successful")
                return True
            else:
                logger.error(f"Hash mismatch: expected {expected_sha256}, got {actual_hash}")
                return False

        except Exception as e:
            logger.error(f"Error verifying download: {e}")
            return False
