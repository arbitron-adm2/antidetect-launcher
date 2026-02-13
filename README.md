# Antidetect Playwright

**Stealth browser automation with anti-detection capabilities**

PyQt6-based GUI launcher for managing browser profiles with fingerprint spoofing (Camoufox). Dolphin Anty-style dark theme interface.

## 📥 Download

### Latest Release — [v0.1.0](https://github.com/arbitron-adm2/antidetect-playwright/releases/tag/v0.1.0)

| Platform | File | How to install |
|----------|------|----------------|
| **Windows** | [`AntidetectBrowser-Windows-x64.zip`](https://github.com/arbitron-adm2/antidetect-playwright/releases/download/v0.1.0/AntidetectBrowser-Windows-x64.zip) | Extract and run `AntidetectBrowser.exe` |
| **Linux (deb)** | [`antidetect-browser_0.1.0_amd64.deb`](https://github.com/arbitron-adm2/antidetect-playwright/releases/download/v0.1.0/antidetect-browser_0.1.0_amd64.deb) | `sudo dpkg -i antidetect-browser_0.1.0_amd64.deb` |
| **Linux (portable)** | [`AntidetectBrowser-Linux-x86_64.tar.gz`](https://github.com/arbitron-adm2/antidetect-playwright/releases/download/v0.1.0/AntidetectBrowser-Linux-x86_64.tar.gz) | Extract and run `./AntidetectBrowser` |

## ✨ Features

- 🎭 **Fingerprint Spoofing** - Canvas, WebGL, fonts, timezone, geolocation
- 🌐 **Proxy Support** - HTTP/HTTPS/SOCKS5 with auto-rotation
- 📁 **Profile Management** - Save/restore browser sessions with tags
- 🚀 **Batch Operations** - Start/stop/ping multiple profiles in parallel
- 🎨 **Modern GUI** - Dark theme, responsive design, inline editing
- 🔒 **Privacy-Focused** - All data stored locally, no telemetry
- ⚡ **High Performance** - Threaded IP checks, async operations

## 📋 Requirements

- Python 3.12+
- Git

## 🚀 Quick Start

### Linux / macOS

```bash
git clone https://github.com/arbitron-adm2/antidetect-playwright.git
cd antidetect-playwright
chmod +x setup.sh
./setup.sh

# Activate environment
source .venv/bin/activate

# Launch GUI
antidetect-browser
```

### Windows

```cmd
git clone https://github.com/arbitron-adm2/antidetect-playwright.git
cd antidetect-playwright
setup.bat

REM Activate environment
.venv\Scripts\activate.bat

REM Launch GUI
antidetect-browser
```

---

## 🖼️ Screenshots

### Profiles Page

![Profiles](docs/screenshots/profiles.png)

### Proxy Management

![Proxy](docs/screenshots/proxy.png)

### Tags & Organization

![Tags](docs/screenshots/tags.png)

---

## 🎯 Usage

### Create Profile

1. Click **New Profile** → Quick Create
2. Enter name, select OS/browser
3. Optional: Add proxy, tags, labels
4. Click **Start** to launch

### Batch Operations

1. Select multiple profiles (Ctrl+Click)
2. Click **⋮** → Batch Start/Stop/Ping
3. Progress shown in status bar

### Proxy Setup

1. Go to **Proxy** tab
2. Click **⋮** → Add Proxy
3. Enter host:port:user:pass (or HTTP URL)
4. Click **Ping** to verify

### Tags & Organization

1. **Tags** tab → Create tag groups
2. Assign colors and icons
3. Drag tags to profiles or inline edit

---

## ⚙️ Configuration

### Data Storage Locations

The application uses **platform-specific directories** following OS conventions:

**Development Mode (from source):**
- `./data/` (relative to project root)

**Installed Package:**
- **Linux:** `~/.local/share/antidetect-browser/`
- **Windows:** `%APPDATA%\AntidetectBrowser\`
- **macOS:** `~/Library/Application Support/AntidetectBrowser/`

### Configuration Files

All settings are managed through the GUI:

- **Browser profiles** - `profiles.json`
- **Proxy settings** - `proxy_pool.json` (encrypted passwords)
- **Tags & labels** - `labels_pool.json`
- **GUI preferences** - `settings.json` (window size, theme, etc.)
- **Browser data** - `browser_data/{profile-id}/` (cookies, history, etc.)

See [CONFIGURATION_STORAGE.md](docs/CONFIGURATION_STORAGE.md) for detailed documentation.

### Migrating Existing Data

If upgrading from a previous version with data in `./data/`:

```bash
python migrate_data.py
```

This will automatically move your data to the platform-specific location.

---

## 🔧 Development

### Install Dev Dependencies

```bash
pip install -e ".[gui,dev]"
```

### Run Tests

```bash
pytest tests/
```

### Type Checking

```bash
mypy src/antidetect_playwright
```

### Code Formatting

```bash
ruff check src/
ruff format src/
```

---

## 🛣️ Roadmap

- [ ] Headless browser mode
- [ ] Profile import/export
- [ ] Fingerprint templates
- [ ] Automation scripting
- [ ] Cloud sync (optional)
- [ ] Team collaboration features

---

## 📄 License

MIT License — See [LICENSE](LICENSE)
