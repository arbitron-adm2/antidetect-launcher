# Configuration and User Data Storage

This document describes where Antidetect Launcher Launcher stores configuration, user profiles, and application data.

## Storage Directory

The application uses **platform-specific data directories** that follow operating system conventions:

### Platform-Specific Paths

#### Development Mode (running from source)
```
./data/  (relative to project root)
```

#### Installed Package Locations

**Linux:**
```
~/.local/share/antidetect-launcher/
```
Following XDG Base Directory specification. Can be overridden with `XDG_DATA_HOME`.

**Windows:**
```
%APPDATA%\AntidetectLauncher\
```
Typically: `C:\Users\{username}\AppData\Roaming\AntidetectLauncher\`

**macOS:**
```
~/Library/Application Support/AntidetectLauncher/
```

### How Detection Works

The application automatically detects if it's running:
1. **From source** (development) → uses `./data/`
2. **As PyInstaller bundle** → uses platform-specific path
3. **As installed package** (from `/usr/bin`, `/opt`, etc.) → uses platform-specific path

**Implementation:** `src/antidetect_launcher/gui/paths.py:get_data_dir()`

## Migrating Existing Data

If you have data in the old `./data/` directory and want to migrate to the new platform-specific location:

### Automatic Migration Script

```bash
python migrate_data.py
```

This will:
1. Detect your platform
2. Show old and new data locations
3. Copy all data to new location
4. Optionally delete old directory

### Manual Migration

**Linux:**
```bash
cp -r data/ ~/.local/share/antidetect-launcher/
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse data\ $env:APPDATA\AntidetectLauncher\
```

**macOS:**
```bash
cp -r data/ ~/Library/Application\ Support/AntidetectLauncher/
```

---

## File Structure

### Main Configuration Files

Located in the root of `data/` directory:

```
data/
├── profiles.json           # Browser profiles database
├── folders.json            # Folder organization
├── settings.json           # Application settings
├── proxy_pool.json         # Proxy pool with encrypted passwords
├── labels_pool.json        # Tags, statuses, note templates
├── trash.json              # Deleted profiles (restorable)
└── browser_data/           # Browser profile data
    └── {profile-id}/       # Individual profile directories
```

### Configuration Files Details

#### 1. `profiles.json`
**Purpose:** Stores all browser profile configurations

**Contains:**
- Profile ID (UUID)
- Profile name
- Folder assignment
- Tags
- Status and color
- Notes
- Proxy configuration
- Fingerprint settings
- User agent
- Canvas/WebGL settings
- Geolocation
- Timezone
- Language preferences
- Browser customization
- Created/updated timestamps

**Storage Implementation:** `storage.py:53` - `Storage.__init__()`
```python
self._profiles_file = self._data_dir / "profiles.json"
```

**Loading:** `storage.py:236` - `_load_profiles()`

**Saving:** `storage.py:333` - `save_profiles()`

**Format:** JSON with atomic write protection to prevent corruption

---

#### 2. `folders.json`
**Purpose:** Stores folder hierarchy for organizing profiles

**Contains:**
- Folder ID (UUID)
- Folder name
- Color (hex)
- Icon (optional)
- Parent folder ID (for nested folders)

**Storage Implementation:** `storage.py:58`
```python
self._folders_file = self._data_dir / "folders.json"
```

**Loading:** `storage.py:276` - `_load_folders()`

**Saving:** `storage.py:339` - `save_folders()`

---

#### 3. `settings.json`
**Purpose:** Application-wide settings and preferences

**Contains:**
- Window size and position
- Theme (dark/light)
- Language preference
- Default browser settings
- Performance options
- Update settings
- Privacy preferences

**Storage Implementation:** `storage.py:59`
```python
self._settings_file = self._data_dir / "settings.json"
```

**Loading:** `storage.py:289` - `_load_settings()`

**Saving:** `storage.py:344` - `save_settings()`

---

#### 4. `proxy_pool.json`
**Purpose:** Stores proxy servers pool with encrypted credentials

**Contains:**
- Proxy type (http/https/socks5)
- Host and port
- Username and password (encrypted)
- Country code and name
- Rotation settings

**Security:** Passwords are encrypted using `SecurePasswordEncryption` before storage

**Storage Implementation:** `storage.py:60`
```python
self._proxy_pool_file = self._data_dir / "proxy_pool.json"
```

**Loading:** `storage.py:302` - `_load_proxy_pool()`
- Automatically decrypts passwords on load

**Saving:** `storage.py:350` - `save_proxy_pool()`
- Automatically encrypts passwords before save

**Encryption:** `security.py` - Uses Fernet symmetric encryption

---

#### 5. `labels_pool.json`
**Purpose:** Unified pool for tags, statuses, and note templates

**Contains:**
- **Tags:** List of available tags
- **Statuses:** Custom status names and colors
- **Note Templates:** Reusable note templates

**Storage Implementation:** `storage.py:64`
```python
self._labels_pool_file = self._data_dir / "labels_pool.json"
```

**Loading:** `storage.py:155` - `_load_labels_pool()`
- Backward compatible with legacy `tags_pool.json`

**Saving:** `storage.py:225` - `save_labels_pool()`

**Migration:** Automatically migrates from `tags_pool.json` if `labels_pool.json` doesn't exist

---

#### 6. `trash.json`
**Purpose:** Stores deleted profiles for recovery

**Contains:**
- Profile ID
- Profile name
- Deletion timestamp
- Full profile data (for restoration)

**Storage Implementation:** `storage.py:65`
```python
self._trash_file = self._data_dir / "trash.json"
```

**Loading:** `storage.py:706` - `_load_trash()`

**Saving:** `storage.py:716` - `_save_trash()`

**Operations:**
- `restore_from_trash(profile_id)` - Restore profile
- `permanently_delete(profile_id)` - Delete forever
- `empty_trash()` - Clear all trash

---

### Browser Profile Data

#### Directory: `data/browser_data/{profile-id}/`

Each browser profile has a dedicated directory containing:

```
data/browser_data/{profile-id}/
├── cookies.sqlite          # Browser cookies
├── places.sqlite           # History and bookmarks
├── formhistory.sqlite      # Form autocomplete data
├── permissions.sqlite      # Site permissions
├── cert9.db                # Certificate database
├── key4.db                 # Password database
├── prefs.js                # Firefox preferences
├── extensions/             # Browser extensions
├── cache2/                 # Browser cache
├── storage/                # Local storage, IndexedDB
└── ...                     # Other browser files
```

**Directory Creation:** `storage.py:752` - `get_profile_data_dir()`
```python
def get_profile_data_dir(self, profile_id: str) -> Path:
    """Get browser data directory for profile."""
    path = self._data_dir / "browser_data" / profile_id
    path.mkdir(parents=True, exist_ok=True)
    return path
```

**Referenced in:** `constants.py:39`
```python
BROWSER_DATA_DIR: Final[str] = "data/browser_data"
```

---

## Storage Implementation Details

### Atomic Writes

All file writes use atomic operations to prevent corruption:

**Implementation:** `storage.py:112` - `_atomic_write()`

**Process:**
1. Write to temporary file in same directory
2. Atomic rename (POSIX guarantees atomicity)
3. Cleanup on error

**Benefits:**
- Prevents corruption if application crashes during write
- No partial/corrupted JSON files
- Safe for concurrent access

---

### Performance Optimizations

#### 1. Profile Index
**Purpose:** O(1) profile lookup by ID

**Implementation:** `storage.py:78`
```python
self._profile_index: dict[str, BrowserProfile] = {}
```

**Rebuild:** `storage.py:87` - `_rebuild_index()`

**Usage:** `storage.py:395` - `get_profile(profile_id)`

---

#### 2. Tag Index
**Purpose:** Fast tag-based queries (40x improvement)

**Implementation:** `storage.py:82`
```python
self._tag_index: dict[str, set[str]] = {}
```

**Rebuild:** `storage.py:93` - `_rebuild_tag_index()`
- Only rebuilds when dirty (after profile changes)
- O(profiles × avg_tags) once vs O(tags × profiles) per query

**Usage:**
- `get_all_tags()` - Get unique tags
- `get_tag_counts()` - Get usage statistics

**Performance:**
- Without index: 50 tags × 100 profiles = 5000 iterations per query
- With index: 1 rebuild + O(1) lookups

---

## Data Directory Constants

**Definition:** `constants.py:39-40`

```python
BROWSER_DATA_DIR: Final[str] = "data/browser_data"
STORAGE_DIR: Final[str] = "data"
```

**Usage in Storage Class:** `storage.py:53`
```python
def __init__(self, data_dir: str = "data"):
    self._data_dir = Path(data_dir)
    self._data_dir.mkdir(parents=True, exist_ok=True)
```

---

## Security Features

### 1. Password Encryption
**File:** `security.py` - `SecurePasswordEncryption`

**Algorithm:** Fernet (AES-128 CBC with HMAC)

**Usage:**
- Proxy passwords in `proxy_pool.json`
- Automatic encryption on save
- Automatic decryption on load

### 2. Path Sanitization
**Function:** `security.py` - `sanitize_path_component()`

**Purpose:** Prevent directory traversal attacks

**Validation:**
- Removes `..` path segments
- Blocks absolute paths
- Validates UUID formats

### 3. UUID Validation
**Function:** `security.py` - `validate_uuid()`

**Purpose:** Ensure profile IDs are valid UUIDs

**Implementation:**
- Rejects invalid formats
- Prevents injection attacks
- Used in all profile operations

---

## Backup and Migration

### Backup Strategy

To backup all user data, copy the entire `data/` directory:

```bash
cp -r data/ backup/data_$(date +%Y%m%d_%H%M%S)/
```

### Migration

To migrate to a new installation:

1. Copy entire `data/` directory to new location
2. Launch application
3. All profiles, settings, and data will be preserved

### Portable Installation

For portable installation, ensure `data/` directory is in the same location as the executable.

---

## File Permissions

### Linux/macOS
- Configuration files: `644` (rw-r--r--)
- Data directory: `755` (rwxr-xr-x)
- Profile directories: `755` (rwxr-xr-x)

### Windows
- Uses ICACLS for proper ACL management
- User-only access to sensitive data

**Implementation:** `security.py` - Platform-specific permission handling

---

## Data Retention

### Active Profiles
- Stored indefinitely in `profiles.json`
- Browser data preserved in `data/browser_data/{profile-id}/`

### Deleted Profiles
- Moved to `trash.json` with deletion timestamp
- Restorable until permanently deleted
- Empty trash manually or after 30 days (configurable)

### Logs
- Application logs: `logs/` directory
- Rotated automatically (7 days retention by default)
- Configurable in settings

---

## Environment Variables

### Custom Data Directory

Override default data directory:

```bash
export ANTIDETECT_DATA_DIR="/custom/path/to/data"
```

**Implementation:** Check in `storage.py` initialization

---

## Troubleshooting

### Corrupted Configuration

If configuration files become corrupted:

1. **Backup existing data:**
   ```bash
   cp -r data/ data_backup/
   ```

2. **Remove corrupted file:**
   ```bash
   rm data/profiles.json  # or other corrupted file
   ```

3. **Restart application** - will create fresh file

4. **Restore from backup if needed**

### Reset to Defaults

To reset application to factory defaults:

```bash
rm -rf data/
```

**Warning:** This deletes all profiles and settings permanently.

---

## Code References

### Main Storage Class
- **File:** `src/antidetect_launcher/gui/storage.py`
- **Class:** `Storage`
- **Initialization:** Line 53
- **Profile CRUD:** Lines 374-500
- **Folder CRUD:** Lines 502-531
- **Settings:** Lines 533-541
- **Proxy Pool:** Lines 543-565
- **Tags/Labels:** Lines 572-704
- **Trash:** Lines 706-750

### Constants
- **File:** `src/antidetect_launcher/gui/constants.py`
- **Data paths:** Lines 39-40

### Security
- **File:** `src/antidetect_launcher/gui/security.py`
- **Encryption:** `SecurePasswordEncryption` class
- **Validation:** `validate_uuid()`, `sanitize_path_component()`

---

## Summary

**Configuration Location:** `data/` directory in application root

**Main Files:**
- `profiles.json` - Browser profiles
- `folders.json` - Organization
- `settings.json` - App settings
- `proxy_pool.json` - Encrypted proxies
- `labels_pool.json` - Tags/statuses/templates
- `trash.json` - Deleted profiles

**Browser Data:** `data/browser_data/{profile-id}/`

**Security:** Encrypted passwords, atomic writes, UUID validation

**Performance:** Indexed lookups, tag caching, incremental updates

**Backup:** Copy entire `data/` directory
