# Antidetect Launcher

Stealth browser with anti-detection. PyQt6 GUI + Camoufox engine.

## Download

**[v0.1.0](https://github.com/arbitron-adm2/antidetect-launcher/releases/tag/v0.1.0)**

| Platform | File | Size | Install |
|----------|------|------|---------|
| Windows | [AntidetectLauncher-Windows-x64.zip](https://github.com/arbitron-adm2/antidetect-launcher/releases/download/v0.1.0/AntidetectLauncher-Windows-x64.zip) | 93 MB | Extract → run `AntidetectLauncher.exe` |
| Linux (deb) | [antidetect-launcher_0.1.0_amd64.deb](https://github.com/arbitron-adm2/antidetect-launcher/releases/download/v0.1.0/antidetect-launcher_0.1.0_amd64.deb) | 125 MB | `sudo dpkg -i antidetect-launcher_0.1.0_amd64.deb` |
| Linux (portable) | [AntidetectLauncher-Linux-x86_64.tar.gz](https://github.com/arbitron-adm2/antidetect-launcher/releases/download/v0.1.0/AntidetectLauncher-Linux-x86_64.tar.gz) | 161 MB | Extract → `./AntidetectLauncher` |

## Features

- **Fingerprint spoofing** — Canvas, WebGL, fonts, timezone, geolocation
- **Proxy support** — HTTP/HTTPS/SOCKS5
- **Profile management** — save/restore sessions, tags, labels
- **Batch operations** — start/stop/ping multiple profiles
- **System tray** — minimize to tray, running count
- **Dark theme GUI** — Dolphin Anty style

## From source

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
| Installed — Linux | `~/.local/share/antidetect-launcher/` |
| Installed — Windows | `%APPDATA%\AntidetectLauncher\` |
| Installed — macOS | `~/Library/Application Support/AntidetectLauncher/` |

## License

MIT
