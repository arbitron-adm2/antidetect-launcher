# Antidetect Launcher

Stealth browser automation launcher with anti-detection powered by Camoufox and a PyQt6 desktop UI.

## Releases

Download builds from: https://github.com/arbitron-adm2/antidetect-launcher/releases

## Core features

- Fingerprint spoofing (Canvas, WebGL, fonts, timezone, geolocation)
- Proxy support (HTTP/HTTPS/SOCKS5)
- Profile management and batch start/stop operations
- System tray integration with running browser count
- Cross-platform autostart and app data handling

## Quick start from source

```bash
git clone https://github.com/arbitron-adm2/antidetect-launcher.git
cd antidetect-launcher
pip install -e ".[gui]"
antidetect-launcher
```

Requires Python 3.12+.

## Data locations

| Mode | Path |
|------|------|
| Dev (from source) | `./data/` |
| Installed - Linux | `~/.local/share/antidetect-launcher/` |
| Installed - Windows | `%APPDATA%\AntidetectLauncher\` |
| Installed - macOS | `~/Library/Application Support/AntidetectLauncher/` |

## License

MIT
