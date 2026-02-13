"""Browser launcher using Camoufox with auto-fingerprint."""

import json
import logging
from pathlib import Path
from typing import Callable
import asyncio

from playwright.async_api import Page, BrowserContext
from camoufox.async_api import AsyncCamoufox
from camoufox.utils import launch_options as camoufox_launch_options
import orjson

from .models import BrowserProfile, ProfileStatus, ProxyConfig

logger = logging.getLogger(__name__)


# Performance optimization: Async file I/O helpers to prevent UI freezes
async def _read_json_async(file_path: Path) -> dict:
    """Read JSON file asynchronously to avoid blocking UI thread.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON dict

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    loop = asyncio.get_event_loop()

    def _read():
        return json.loads(file_path.read_text())

    return await loop.run_in_executor(None, _read)


async def _write_json_async(file_path: Path, data: dict) -> None:
    """Write JSON file asynchronously to avoid blocking UI thread.

    Args:
        file_path: Path to write JSON
        data: Dictionary to serialize
    """
    loop = asyncio.get_event_loop()

    def _write():
        file_path.write_text(json.dumps(data, indent=2, default=str))

    await loop.run_in_executor(None, _write)


# Screen/window dimension keys that should NOT be persisted or spoofed
# These values are spoofed by Camoufox via JavaScript API overrides
# If we set them, window/screen dimensions return constants
# regardless of actual window size = broken scaling!
SCREEN_WINDOW_KEYS_TO_EXCLUDE = {
    # Window dimensions
    "window.outerWidth",
    "window.outerHeight",
    "window.innerWidth",
    "window.innerHeight",
    "window.screenX",
    "window.screenY",
    # Screen dimensions - let browser use real screen
    "screen.width",
    "screen.height",
    "screen.availWidth",
    "screen.availHeight",
    "screen.availTop",
    "screen.availLeft",
    "screen.colorDepth",
    "screen.pixelDepth",
    # Document body dimensions
    "document.body.clientWidth",
    "document.body.clientHeight",
}


def _remove_screen_window_keys_from_env(env: dict) -> dict:
    """Remove screen/window keys from CAMOU_CONFIG_* env vars.

    Camoufox serializes config into CAMOU_CONFIG_1, CAMOU_CONFIG_2, etc.
    We need to deserialize, remove keys, and re-serialize.
    """
    # Collect all CAMOU_CONFIG chunks
    chunks = []
    i = 1
    while f"CAMOU_CONFIG_{i}" in env:
        chunks.append(env[f"CAMOU_CONFIG_{i}"])
        i += 1

    if not chunks:
        return env

    # Reconstruct full config JSON
    full_config_str = "".join(chunks)
    try:
        config = orjson.loads(full_config_str)
    except Exception as e:
        logger.warning(f"Failed to parse CAMOU_CONFIG: {e}")
        return env

    # Remove screen/window keys
    removed = []
    for key in list(config.keys()):
        if key in SCREEN_WINDOW_KEYS_TO_EXCLUDE:
            del config[key]
            removed.append(key)

    if removed:
        logger.debug(f"Removed screen/window keys from config: {removed}")

    # Re-serialize
    new_config_str = orjson.dumps(config).decode("utf-8")

    # Clear old chunks
    for j in range(1, i):
        del env[f"CAMOU_CONFIG_{j}"]

    # Split into new chunks (same chunk size logic as Camoufox)
    import sys

    chunk_size = 2047 if sys.platform == "win32" else 32767
    for j, start in enumerate(range(0, len(new_config_str), chunk_size)):
        chunk = new_config_str[start : start + chunk_size]
        env[f"CAMOU_CONFIG_{j + 1}"] = chunk

    return env


class BrowserLauncher:
    """Manages browser instances using Camoufox with automatic fingerprinting."""

    def __init__(self, data_dir: Path, settings=None):
        self._data_dir = data_dir
        self._settings = settings  # AppSettings for browser config
        self._browsers: dict[str, AsyncCamoufox] = {}
        self._browser_instances: dict[str, BrowserContext] = {}
        self._pages: dict[str, Page] = {}
        self._monitor_tasks: dict[str, asyncio.Task] = {}
        self._stopping: set[str] = set()
        self._on_status_change: Callable[[str, ProfileStatus], None] | None = None
        self._on_browser_closed: Callable[[str], None] | None = None
        # Watchdog for periodic health checks
        self._watchdog_task: asyncio.Task | None = None
        self._watchdog_interval: float = 5.0  # seconds

    def set_status_callback(self, callback: Callable[[str, ProfileStatus], None]) -> None:
        """Set callback for status changes."""
        self._on_status_change = callback

    def set_browser_closed_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for when browser is manually closed."""
        self._on_browser_closed = callback

    def start_watchdog(self) -> None:
        """Start periodic health check watchdog.

        Detects orphaned browser references where Playwright lost connection
        but the 'close' event never fired.
        """
        if self._watchdog_task is not None:
            return
        self._watchdog_task = asyncio.create_task(self._watchdog_loop())
        logger.debug("Browser watchdog started (interval=%ss)", self._watchdog_interval)

    def stop_watchdog(self) -> None:
        """Stop the watchdog task."""
        if self._watchdog_task is not None:
            self._watchdog_task.cancel()
            self._watchdog_task = None
            logger.debug("Browser watchdog stopped")

    async def _watchdog_loop(self) -> None:
        """Periodic health check for running browsers.

        Detects browsers where the Playwright context is disconnected
        but the monitor task failed to clean up.
        """
        while True:
            try:
                await asyncio.sleep(self._watchdog_interval)
                await self._check_browser_health()
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.warning("Watchdog error: %s", e)

    async def _check_browser_health(self) -> None:
        """Check health of all tracked browser instances.

        Cleans up any browser references where the context
        has been disconnected without a proper close event.
        """
        stale_profiles: list[str] = []

        for profile_id, context in list(self._browser_instances.items()):
            if profile_id in self._stopping:
                continue
            try:
                # Check if the browser context is still connected
                # Accessing .pages on a dead context raises
                _ = context.pages
            except Exception:
                logger.warning(
                    "Browser context disconnected for profile %s, cleaning up",
                    profile_id,
                )
                stale_profiles.append(profile_id)

        for profile_id in stale_profiles:
            # Cancel monitor task if still running
            task = self._monitor_tasks.pop(profile_id, None)
            if task is not None:
                task.cancel()
            await self._cleanup_profile(profile_id)
            if self._on_status_change:
                self._on_status_change(profile_id, ProfileStatus.STOPPED)
            if self._on_browser_closed:
                self._on_browser_closed(profile_id)

    async def launch_profile(self, profile: BrowserProfile) -> bool:
        """Launch browser for profile with auto-configured fingerprint.

        Camoufox + BrowserForge handles:
        - User-Agent generation
        - Platform/OS fingerprint
        - WebGL vendor/renderer
        - Screen resolution
        - Hardware concurrency
        - Device memory
        - And more...

        If proxy is set with geoip=True:
        - Timezone auto-detected from IP
        - Locale auto-detected from IP
        - Language headers auto-configured
        """
        try:
            # Browser data directory for cookies/storage persistence
            user_data_dir = self._data_dir / profile.id
            user_data_dir.mkdir(parents=True, exist_ok=True)

            proxy = profile.proxy.to_camoufox()

            # Debug: log proxy config (hide password)
            if proxy:
                debug_proxy = {k: (v if k != "password" else "***") for k, v in proxy.items()}
                logger.debug(f"Proxy config: {debug_proxy}")

            # Detect current IP for timezone and geolocation
            # Use Camoufox's MaxMind database for accurate timezone matching
            from camoufox.ip import public_ip, Proxy as CamoufoxProxy
            from camoufox.locale import get_geolocation, geoip_allowed

            geoip_info = None
            try:
                geoip_allowed()  # Check if geoip extra is installed

                # Run blocking IP/geo detection in thread pool to avoid blocking event loop
                loop = asyncio.get_event_loop()

                async def detect_ip_and_geo():
                    """Detect IP and geolocation in thread pool."""

                    def _sync_detect():
                        # Get public IP (through proxy if configured)
                        if proxy:
                            proxy_str = CamoufoxProxy(**proxy).as_string()
                            ip = public_ip(proxy_str)
                        else:
                            ip = public_ip()

                        # Get geolocation from MaxMind database
                        geolocation = get_geolocation(ip)
                        return ip, geolocation

                    return await loop.run_in_executor(None, _sync_detect)

                ip, geolocation = await detect_ip_and_geo()

                # Create geoip_info compatible object
                class GeoIPInfoCompat:
                    def __init__(self, ip, geolocation):
                        self.ip = ip
                        self.country_code = geolocation.locale.region or "XX"
                        self.timezone = geolocation.timezone
                        self.city = ""
                        self.lat = geolocation.latitude
                        self.lon = geolocation.longitude

                geoip_info = GeoIPInfoCompat(ip, geolocation)
                logger.info(
                    f"Detected IP: {geoip_info.ip} ({geoip_info.country_code}, {geoip_info.timezone})"
                )
                # Update profile with IP info for display (flag emoji)
                if not profile.proxy:
                    profile.proxy = ProxyConfig()
                profile.proxy.country_code = geoip_info.country_code
                profile.proxy.timezone = geoip_info.timezone
                profile.proxy.city = geoip_info.city
            except Exception as e:
                logger.warning(f"Failed to get GeoIP info: {e}")

            logger.info("Starting profile: %s", profile.name)
            logger.debug(
                "Proxy configured: host=%s, port=%s",
                profile.proxy.host if profile.proxy else None,
                profile.proxy.port if profile.proxy else None,
            )
            logger.debug("Data dir: %s", user_data_dir)

            # Camoufox options - maximum protection + user settings
            camoufox_options = {
                "headless": False,
                # We handle geoip ourselves via ip-api.com to ensure timezone matches IP
                # Camoufox geoip uses MaxMind which may return different timezone
                "geoip": False,
                # Block WebRTC to prevent IP leak
                "block_webrtc": True,
                # Human-like cursor movement (from settings)
                "humanize": self._settings.humanize if self._settings else 1.5,
                # Disable Cross-Origin-Opener-Policy for Turnstile/Cloudflare
                "disable_coop": True,
                # Suppress warnings for intentional settings
                "i_know_what_im_doing": True,
                # Persistent storage for cookies/localStorage
                "persistent_context": True,
                "user_data_dir": str(user_data_dir),
                # Disable fixed viewport so browser content scales with window
                "no_viewport": True,
                # Performance settings
                "block_images": (self._settings.block_images if self._settings else False),
                "enable_cache": self._settings.enable_cache if self._settings else True,
                # Debug mode
                "debug": self._settings.debug_mode if self._settings else False,
                # Firefox user prefs - only session settings from launcher
                # All styles and UI customizations are handled via browser build
                "firefox_user_prefs": {
                    # Session restore settings - controlled by save_tabs
                    **(
                        {
                            "browser.startup.page": 3,  # 3 = restore previous session
                            "browser.sessionstore.resume_from_crash": True,
                            "browser.sessionstore.max_resumed_crashes": 3,
                        }
                        if (self._settings and getattr(self._settings, "save_tabs", True))
                        else {
                            "browser.startup.page": 0,  # 0 = blank page
                            "browser.sessionstore.max_resumed_crashes": 0,
                        }
                    ),
                    # Performance optimizations - hardware acceleration
                    "gfx.webrender.all": True,  # Enable WebRender compositor
                    "gfx.webrender.enabled": True,
                    "gfx.webrender.software": False,  # Prefer hardware WebRender
                    "layers.acceleration.force-enabled": True,  # Force GPU acceleration
                    "layers.gpu-process.enabled": True,
                    "media.hardware-video-decoding.enabled": True,  # Hardware video decode
                    "media.ffmpeg.vaapi.enabled": True,  # VA-API for Linux
                    # Compositor and rendering
                    "gfx.compositor.glcontext.opaque": True,  # Faster compositing
                    "layers.offmainthreadcomposition.enabled": True,  # Off-main-thread compositing
                    "layers.async-pan-zoom.enabled": True,  # Smoother scrolling
                    "apz.allow_double_tap_zooming": False,  # Disable double-tap zoom for faster response
                    "apz.gtk.kinetic_scroll.enabled": False,  # Disable kinetic scroll (can cause lags)
                    # Reduce paint flashing and reflows
                    "nglayout.initialpaint.delay": 0,  # No delay for initial paint
                    "nglayout.initialpaint.delay_in_oopif": 0,
                    "content.notify.interval": 100000,  # Less frequent content updates
                    # Memory and performance
                    "browser.sessionstore.restore_tabs_lazily": True,  # Lazy load tabs
                    "browser.sessionstore.restore_on_demand": True,
                    "browser.tabs.unloadOnLowMemory": True,  # Unload tabs when low memory
                    "javascript.options.mem.gc_incremental": True,  # Incremental GC
                    "javascript.options.mem.gc_per_zone": True,
                    # Reduce disk I/O
                    "browser.sessionstore.interval": 60000,  # Save session every 60s instead of 15s
                    "browser.cache.disk.smart_size.enabled": True,
                    # Tab unloading for better multi-tab performance
                    "browser.tabs.min_inactive_duration_before_unload": 300000,  # 5min before unload
                    # Reduce animation overhead
                    "ui.prefersReducedMotion": 1,  # Reduce animations
                    "toolkit.cosmeticAnimations.enabled": False,  # Disable cosmetic animations
                },
            }

            if proxy:
                camoufox_options["proxy"] = proxy

            # Custom browser executable path
            if self._settings and self._settings.browser_executable_path:
                browser_path = Path(self._settings.browser_executable_path)
                if browser_path.exists():
                    camoufox_options["executable_path"] = str(browser_path)
                    logger.info(f"Using custom browser: {browser_path}")
                else:
                    logger.warning(f"Custom browser not found: {browser_path}")

            # Extensions (default: uBlock Origin, BPC)
            if self._settings:
                from camoufox import DefaultAddons

                exclude_addons = []
                if self._settings.exclude_ublock:
                    exclude_addons.append(DefaultAddons.UBO)
                if self._settings.exclude_bpc:
                    exclude_addons.append(DefaultAddons.BPC)
                if exclude_addons:
                    camoufox_options["exclude_addons"] = exclude_addons

                # Custom addons
                if self._settings.custom_addons:
                    camoufox_options["addons"] = self._settings.custom_addons

            # OS hint for fingerprint generation
            os_map = {
                "windows": "windows",
                "macos": "macos",
                "linux": "linux",
            }
            # Short OS codes for WebGL lookup
            os_short_map = {
                "windows": "win",
                "macos": "mac",
                "linux": "lin",
            }
            if profile.os_type in os_map:
                camoufox_options["os"] = [os_map[profile.os_type]]

            # Save complete fingerprint config for consistent profiles across sessions
            # Same profile must have same fingerprint to avoid detection
            # Screen/window keys are removed later via _remove_screen_window_keys_from_env()

            fingerprint_file = user_data_dir / "fingerprint.json"

            # Check if OS changed - if so, regenerate fingerprint
            regenerate_fingerprint = False
            if fingerprint_file.exists():
                # Async I/O to prevent UI freeze (50-200ms blocking → non-blocking)
                fp_data = await _read_json_async(fingerprint_file)
                saved_os = fp_data.get("os", "")
                current_os = profile.os_type or "windows"
                if saved_os != current_os:
                    logger.info(
                        f"OS changed from '{saved_os}' to '{current_os}' - regenerating fingerprint"
                    )
                    regenerate_fingerprint = True
                    fingerprint_file.unlink()  # Delete old fingerprint

            if fingerprint_file.exists() and not regenerate_fingerprint:
                # Load saved fingerprint config (async to avoid blocking)
                fp_data = await _read_json_async(fingerprint_file)
                fp_config = fp_data.get("fingerprint", {})

                # Remove old timezone - we'll set fresh one from current IP
                fp_config.pop("locale:timezone", None)
                fp_config.pop("timezone", None)
                fp_config.pop("geolocation:latitude", None)
                fp_config.pop("geolocation:longitude", None)
                fp_config.pop("locale:region", None)
                fp_config.pop("locale:language", None)

                # Set fresh timezone/geolocation from current IP
                # This ensures timezone always matches current IP
                if geoip_info:
                    fp_config["timezone"] = geoip_info.timezone
                    if geoip_info.lat and geoip_info.lon:
                        fp_config["geolocation:latitude"] = geoip_info.lat
                        fp_config["geolocation:longitude"] = geoip_info.lon
                    fp_config["locale:region"] = geoip_info.country_code
                    country_to_lang = {
                        "RU": "ru",
                        "US": "en",
                        "GB": "en",
                        "DE": "de",
                        "FR": "fr",
                        "ES": "es",
                        "IT": "it",
                        "PT": "pt",
                        "NL": "nl",
                        "PL": "pl",
                        "UA": "uk",
                        "BY": "be",
                        "KZ": "kk",
                        "CN": "zh",
                        "JP": "ja",
                        "KR": "ko",
                        "BR": "pt",
                        "AR": "es",
                        "MX": "es",
                        "IN": "hi",
                        "TR": "tr",
                        "SA": "ar",
                        "IL": "he",
                        "TH": "th",
                        "VN": "vi",
                    }
                    fp_config["locale:language"] = country_to_lang.get(
                        geoip_info.country_code, "en"
                    )

                # Remove screen/window dimension keys so Camoufox uses real sizes
                for key in list(fp_config.keys()):
                    if key in SCREEN_WINDOW_KEYS_TO_EXCLUDE:
                        del fp_config[key]

                # Restore random values that Camoufox normally generates
                # These are set via set_into() which only sets if key not exists
                if "canvas" in fp_data:
                    fp_config["canvas:aaOffset"] = fp_data["canvas"]["aaOffset"]
                if "fonts" in fp_data:
                    fp_config["fonts:spacing_seed"] = fp_data["fonts"]["spacing_seed"]
                if "history_length" in fp_data:
                    fp_config["window.history.length"] = fp_data["history_length"]

                # Pass config dict - Camoufox will generate new fingerprint but
                # merge_into() won't overwrite our existing keys!
                camoufox_options["config"] = fp_config

                # Restore WebGL config to maintain GPU fingerprint
                webgl = fp_data.get("webgl")
                if webgl:
                    camoufox_options["webgl_config"] = (
                        webgl["vendor"],
                        webgl["renderer"],
                    )
                logger.info(f"Loaded fingerprint config from {fingerprint_file}")
            else:
                # Generate new fingerprint and convert to config
                from browserforge.fingerprints import FingerprintGenerator
                from camoufox.fingerprints import from_browserforge
                from camoufox.webgl import sample_webgl
                from random import randint, randrange

                # Use OS from profile config (windows/macos/linux)
                # Camoufox handles platform hints spoofing internally
                fp_os = profile.os_type or "windows"

                generator = FingerprintGenerator(
                    browser="firefox",
                    os=fp_os,
                )
                fingerprint = generator.generate()
                # Convert to Camoufox config dict
                fp_config = from_browserforge(fingerprint)

                # Generate random values that Camoufox would generate
                # We pre-generate them so we can save and restore later
                canvas_aa_offset = randint(-50, 50)
                fonts_spacing_seed = randint(0, 1_073_741_823)
                history_length = randrange(1, 6)

                # Add to config so Camoufox won't overwrite
                fp_config["canvas:aaOffset"] = canvas_aa_offset
                fp_config["fonts:spacing_seed"] = fonts_spacing_seed
                fp_config["window.history.length"] = history_length

                # Fix Firefox version to match Camoufox real version (135)
                # BrowserForge may generate newer versions which triggers detection
                if "navigator.userAgent" in fp_config:
                    ua = fp_config["navigator.userAgent"]
                    # Replace any Firefox version with 135.0
                    import re

                    ua = re.sub(r"Firefox/\d+\.\d+", "Firefox/135.0", ua)
                    ua = re.sub(r"rv:\d+\.\d+", "rv:135.0", ua)
                    fp_config["navigator.userAgent"] = ua

                # Set timezone, geolocation and locale from our GeoIP detection
                # This ensures timezone matches IP (BrowserScan checks this)
                if geoip_info:
                    # Timezone must match IP location exactly
                    fp_config["timezone"] = geoip_info.timezone
                    # Geolocation coordinates
                    if geoip_info.lat and geoip_info.lon:
                        fp_config["geolocation:latitude"] = geoip_info.lat
                        fp_config["geolocation:longitude"] = geoip_info.lon
                    # Locale based on country
                    fp_config["locale:region"] = geoip_info.country_code
                    # Language based on country (simplified mapping)
                    country_to_lang = {
                        "RU": "ru",
                        "US": "en",
                        "GB": "en",
                        "DE": "de",
                        "FR": "fr",
                        "ES": "es",
                        "IT": "it",
                        "PT": "pt",
                        "NL": "nl",
                        "PL": "pl",
                        "UA": "uk",
                        "BY": "be",
                        "KZ": "kk",
                        "CN": "zh",
                        "JP": "ja",
                        "KR": "ko",
                        "BR": "pt",
                        "AR": "es",
                        "MX": "es",
                        "IN": "hi",
                        "TR": "tr",
                        "SA": "ar",
                        "IL": "he",
                        "TH": "th",
                        "VN": "vi",
                    }
                    fp_config["locale:language"] = country_to_lang.get(
                        geoip_info.country_code, "en"
                    )
                    logger.info(
                        f"Set geolocation from IP: tz={geoip_info.timezone}, lat={geoip_info.lat}, lon={geoip_info.lon}"
                    )

                # Remove screen/window dimension keys so Camoufox uses real sizes
                for key in list(fp_config.keys()):
                    if key in SCREEN_WINDOW_KEYS_TO_EXCLUDE:
                        del fp_config[key]

                # Pass as config dict for first launch too (for consistency)
                camoufox_options["config"] = fp_config

                # Generate WebGL fingerprint matching the OS from profile
                webgl_os = os_short_map.get(profile.os_type, "win")
                webgl_fp = sample_webgl(webgl_os)
                webgl_vendor = webgl_fp["webGl:vendor"]
                webgl_renderer = webgl_fp["webGl:renderer"]
                camoufox_options["webgl_config"] = (webgl_vendor, webgl_renderer)

                # Save complete fingerprint data
                fp_data = {
                    "fingerprint": fp_config,
                    "webgl": {
                        "vendor": webgl_vendor,
                        "renderer": webgl_renderer,
                    },
                    "canvas": {
                        "aaOffset": canvas_aa_offset,
                    },
                    "fonts": {
                        "spacing_seed": fonts_spacing_seed,
                    },
                    "history_length": history_length,
                    "os": profile.os_type or "windows",
                }
                # Async write to prevent UI freeze (50-200ms blocking → non-blocking)
                await _write_json_async(fingerprint_file, fp_data)
                logger.info(f"Generated and saved new fingerprint config to {fingerprint_file}")

            # Create launch options manually to remove screen/window keys
            # This is needed because Camoufox generates these inside launch_options()
            # and we need to remove them AFTER generation but BEFORE launching
            from functools import partial

            # Extract persistent_context flag - it's handled separately by AsyncCamoufox
            persistent_context = camoufox_options.pop("persistent_context", False)

            # Generate launch options
            from_options = await asyncio.get_event_loop().run_in_executor(
                None,
                partial(camoufox_launch_options, **camoufox_options),
            )

            # Remove screen/window keys from CAMOU_CONFIG env vars for dynamic window sizing
            from_options["env"] = _remove_screen_window_keys_from_env(from_options["env"])

            # Add no_viewport for Playwright - let content scale with window
            from_options["no_viewport"] = True

            # Create and launch Camoufox with pre-generated options
            camoufox = AsyncCamoufox(
                from_options=from_options,
                persistent_context=persistent_context,
            )
            context = await camoufox.__aenter__()

            self._browsers[profile.id] = camoufox
            self._browser_instances[profile.id] = context

            # Get page (Firefox will restore tabs automatically if enabled)
            if context.pages:
                page = context.pages[-1]
            else:
                page = await context.new_page()

            # Navigate to start page if settings exist and page is blank
            if self._settings and page.url == "about:blank":
                start_page = self._settings.start_page or "about:blank"
                if start_page != "about:blank":
                    # Add https:// if no protocol specified
                    if not start_page.startswith(("http://", "https://", "about:", "file://")):
                        start_page = "https://" + start_page
                    try:
                        await page.goto(start_page, wait_until="domcontentloaded", timeout=10000)
                    except Exception as e:
                        logger.warning(f"Failed to load start page {start_page}: {e}")

            self._pages[profile.id] = page

            # Monitor for browser close
            task = asyncio.create_task(self._monitor_browser(profile.id, context))
            self._monitor_tasks[profile.id] = task

            if self._on_status_change:
                self._on_status_change(profile.id, ProfileStatus.RUNNING)

            return True

        except Exception as e:
            logger.exception("Error launching profile: %s", e)
            if self._on_status_change:
                self._on_status_change(profile.id, ProfileStatus.ERROR)
            return False

    async def _monitor_browser(self, profile_id: str, context: BrowserContext) -> None:
        """Monitor browser for manual close or crash.

        Waits for the Playwright BrowserContext 'close' event.
        Handles three scenarios:
        1. CancelledError → programmatic stop (stop_profile called), no cleanup here
        2. 'close' event → user closed the browser window, run cleanup
        3. Exception → Playwright transport error / crash, run cleanup
        """
        cancelled = False
        try:
            # Wait for context to close (user closed window)
            await context.wait_for_event("close", timeout=0)
        except asyncio.CancelledError:
            cancelled = True
        except Exception as e:
            logger.warning("Browser monitor error for profile %s: %s", profile_id, e)
        finally:
            if cancelled:
                return
            # Browser was closed manually or crashed
            logger.info("Browser closed for profile %s", profile_id)
            await self._cleanup_profile(profile_id)
            if self._on_status_change:
                self._on_status_change(profile_id, ProfileStatus.STOPPED)
            if self._on_browser_closed:
                self._on_browser_closed(profile_id)
            self._stopping.discard(profile_id)

    async def _cleanup_profile(self, profile_id: str) -> None:
        """Clean up profile resources from internal tracking dicts."""
        if profile_id in self._browsers:
            del self._browsers[profile_id]
        if profile_id in self._browser_instances:
            del self._browser_instances[profile_id]
        if profile_id in self._pages:
            del self._pages[profile_id]
        self._monitor_tasks.pop(profile_id, None)

    async def stop_profile(self, profile_id: str) -> bool:
        """Stop browser for profile.

        Lifecycle: RUNNING → STOPPING → (close browser) → STOPPED
        """
        try:
            if profile_id in self._stopping:
                return True
            self._stopping.add(profile_id)

            if profile_id not in self._browsers and profile_id not in self._browser_instances:
                if self._on_status_change:
                    self._on_status_change(profile_id, ProfileStatus.STOPPED)
                self._stopping.discard(profile_id)
                return True

            # Notify STOPPING state for UI feedback
            if self._on_status_change:
                self._on_status_change(profile_id, ProfileStatus.STOPPING)

            # Cancel monitor task first to prevent double-cleanup
            task = self._monitor_tasks.pop(profile_id, None)
            if task is not None:
                task.cancel()

            # Firefox saves sessions automatically via sessionstore.jsonlz4
            if profile_id in self._browsers:
                camoufox = self._browsers[profile_id]
                try:
                    await asyncio.wait_for(camoufox.__aexit__(None, None, None), timeout=10)
                except asyncio.TimeoutError:
                    logger.warning("Timed out closing browser for %s", profile_id)
                except Exception as e:
                    logger.warning("Error closing browser: %s", e)

            await self._cleanup_profile(profile_id)

            if self._on_status_change:
                self._on_status_change(profile_id, ProfileStatus.STOPPED)

            self._stopping.discard(profile_id)
            return True

        except Exception as e:
            logger.exception("Error stopping profile: %s", e)
            if self._on_status_change:
                self._on_status_change(profile_id, ProfileStatus.ERROR)
            return False
        finally:
            self._stopping.discard(profile_id)

    def is_running(self, profile_id: str) -> bool:
        """Check if profile browser is running."""
        return profile_id in self._browser_instances

    def is_stopping(self, profile_id: str) -> bool:
        """Check if profile is currently stopping."""
        return profile_id in self._stopping

    def get_running_profiles(self) -> list[str]:
        """Return list of profile IDs with running browsers."""
        return list(self._browser_instances.keys())

    def get_running_count(self) -> int:
        """Return count of running browsers."""
        return len(self._browser_instances)

    async def cleanup(self) -> None:
        """Stop all running browsers gracefully.

        Called on application exit. Stops watchdog first,
        then closes all browsers concurrently with a timeout.
        """
        self.stop_watchdog()

        profile_ids = list(self._browser_instances.keys())
        if not profile_ids:
            return

        logger.info("Cleaning up %d running browsers...", len(profile_ids))

        # Stop all browsers concurrently with overall timeout
        tasks = [self.stop_profile(pid) for pid in profile_ids]
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "Cleanup timed out, %d browsers may still be running",
                len(self._browser_instances),
            )

        # Force-cleanup any remaining references
        remaining = list(self._browser_instances.keys())
        for pid in remaining:
            logger.warning("Force-cleaning stale browser reference: %s", pid)
            await self._cleanup_profile(pid)

        logger.info("Browser cleanup complete")
