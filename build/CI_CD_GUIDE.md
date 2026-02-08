# CI/CD Setup Guide for Antidetect Browser

Complete guide for setting up and maintaining CI/CD pipelines for automated builds across all platforms.

## Architecture Overview

```
GitHub Actions Workflows
├── build-windows.yml    # Windows builds (EXE installer + portable ZIP)
├── build-linux.yml      # Linux builds (DEB, AppImage, Flatpak)
├── build.yml           # Main release workflow (all platforms)
├── ci.yml              # Linting and tests
└── tests.yml           # Integration tests
```

## GitHub Actions Setup

### Required Secrets

Configure these in repository Settings > Secrets and variables > Actions:

#### Code Signing (Optional but Recommended)

**Windows:**
```
SIGNING_CERTIFICATE      # Base64-encoded .pfx certificate
SIGNING_PASSWORD         # Certificate password
```

To create:
```powershell
# Encode certificate
$certBytes = [IO.File]::ReadAllBytes("cert.pfx")
$certBase64 = [Convert]::ToBase64String($certBytes)
# Add $certBase64 to GitHub secrets
```

**macOS:**
```
MACOS_CERTIFICATE        # Base64-encoded .p12 certificate
MACOS_CERTIFICATE_PWD    # Certificate password
APPLE_ID                 # Apple ID for notarization
APPLE_APP_PASSWORD       # App-specific password
APPLE_TEAM_ID           # Team ID
```

#### Optional Secrets

```
DISCORD_WEBHOOK          # For build notifications
SLACK_WEBHOOK           # For build notifications
UPDATE_SERVER_TOKEN     # For auto-update manifest uploads
```

### Repository Settings

**Required:**
- Enable Actions in Settings > Actions > General
- Set workflow permissions: Read and write permissions
- Allow GitHub Actions to create and approve pull requests

**Recommended:**
- Enable branch protection for `main`
- Require status checks to pass before merging
- Require signed commits for releases

## Workflows

### Windows Build Workflow

**File:** `.github/workflows/build-windows.yml`

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main`
- Tags matching `v*`
- Manual dispatch

**Steps:**
1. Setup Python 3.12
2. Install dependencies
3. Generate icons
4. Build with PyInstaller
5. Validate build
6. Create Inno Setup installer
7. Code signing (if secrets configured)
8. Create portable ZIP
9. Generate checksums
10. Upload artifacts
11. Test installation (separate job)
12. Create release (on tags)

**Artifacts:**
- `windows-installer` - Signed installer
- `windows-portable` - Portable ZIP
- `build-logs` - Logs on failure

**Duration:** ~10-15 minutes

### Linux Build Workflow

**File:** `.github/workflows/build-linux.yml`

**Formats:**
- DEB package (Ubuntu/Debian)
- AppImage (universal)
- Flatpak (Flathub-ready)

**Triggers:**
- Same as Windows workflow

**Steps:**
1. Setup Python 3.12
2. Install build tools (devscripts, flatpak-builder, etc.)
3. Build each format in parallel jobs
4. Run lintian checks (DEB)
5. Test installation
6. Upload artifacts

**Artifacts:**
- `deb-package` - .deb file
- `appimage` - .AppImage file
- `flatpak` - .flatpak bundle

**Duration:** ~15-20 minutes (parallel)

### Main Release Workflow

**File:** `.github/workflows/build.yml`

**Purpose:** Coordinate multi-platform builds and create GitHub releases

**Triggers:**
- Tags matching `v*.*.*`
- Manual dispatch with version input

**Jobs:**
1. `build-windows` - Windows builds
2. `build-linux` - Linux builds
3. `build-macos` - macOS builds
4. `create-release` - Aggregate and release
5. `publish-update-manifest` - Update auto-update system

**Release Assets:**
- Windows installer (signed)
- Windows portable ZIP
- Linux DEB package
- Linux AppImage
- Linux Flatpak
- macOS DMG (future)
- checksums.txt (SHA256)
- RELEASE_NOTES.md

### CI Workflow

**File:** `.github/workflows/ci.yml`

**Purpose:** Code quality checks

**Jobs:**
- Linting (ruff, mypy)
- Type checking
- Code formatting
- Security scanning

**Triggers:**
- Every push
- Pull requests

### Test Workflow

**File:** `.github/workflows/tests.yml`

**Purpose:** Run test suite

**Jobs:**
- Unit tests
- Integration tests
- GUI tests (headless)

## Caching Strategy

### Python Dependencies

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.cache/pypoetry
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
```

**Benefits:**
- Faster builds (3-5 minutes saved)
- Reduced bandwidth
- Consistent dependency versions

### PyInstaller Build

```yaml
- name: Cache PyInstaller builds
  uses: actions/cache@v3
  with:
    path: build/
    key: ${{ runner.os }}-pyinstaller-${{ hashFiles('antidetect-browser.spec') }}
```

## Build Optimization

### Parallel Builds

Run platform builds in parallel:
```yaml
jobs:
  build-windows:
    runs-on: windows-latest
  build-linux:
    runs-on: ubuntu-latest
  build-macos:
    runs-on: macos-latest
```

**Result:** 3 platforms build simultaneously (~15 min total vs ~45 min sequential)

### Conditional Jobs

Skip unnecessary work:
```yaml
- name: Sign builds
  if: |
    github.event_name == 'push' &&
    startsWith(github.ref, 'refs/tags/v') &&
    secrets.SIGNING_CERTIFICATE != ''
```

### Matrix Builds

Test on multiple platforms/versions:
```yaml
strategy:
  matrix:
    os: [windows-latest, ubuntu-22.04, macos-latest]
    python: ['3.12', '3.13']
```

## Artifact Management

### Retention Policy

```yaml
- uses: actions/upload-artifact@v4
  with:
    retention-days: 30  # Release artifacts
```

**Guidelines:**
- Release builds: 90 days
- Development builds: 30 days
- Test artifacts: 7 days
- Logs: 7 days

### Artifact Organization

```
artifacts/
├── windows-build/
│   ├── AntidetectBrowser-Setup-0.1.0.exe
│   └── AntidetectBrowser-Windows-x64-Portable.zip
├── linux-build/
│   ├── antidetect-browser_0.1.0-1_amd64.deb
│   ├── AntidetectBrowser-0.1.0-x86_64.AppImage
│   └── antidetect-browser-0.1.0.flatpak
└── macos-build/
    └── AntidetectBrowser-0.1.0.dmg
```

## Release Process

### Automated Release

1. **Tag version:**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **CI automatically:**
   - Builds all platforms
   - Runs tests
   - Signs executables (if configured)
   - Creates GitHub release
   - Uploads all artifacts
   - Generates release notes
   - Updates auto-update manifest

### Manual Release

1. **Trigger workflow:**
   - Go to Actions tab
   - Select "Build & Release"
   - Click "Run workflow"
   - Enter version number

2. **Review artifacts:**
   - Download and test installers
   - Verify signatures
   - Check checksums

3. **Publish:**
   - Edit release from draft
   - Update release notes
   - Publish release

## Monitoring & Notifications

### Build Status Badges

Add to README.md:
```markdown
![Windows Build](https://github.com/user/repo/workflows/Build%20Windows%20Installer/badge.svg)
![Linux Build](https://github.com/user/repo/workflows/Build%20Linux%20Packages/badge.svg)
```

### Discord Notifications

```yaml
- name: Notify Discord
  if: always()
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    status: ${{ job.status }}
```

### Slack Notifications

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Build failed: ${{ github.repository }}"
      }
```

### Email Notifications

GitHub sends automatic emails for:
- Workflow failures
- First-time contributor PRs
- Security alerts

Configure in: Settings > Notifications

## Troubleshooting

### Common Issues

**Build Timeout:**
```yaml
timeout-minutes: 60  # Default is 360
```

**Disk Space:**
```yaml
- name: Free disk space
  run: |
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
```

**Windows - Inno Setup Not Found:**
```yaml
- name: Install Inno Setup
  run: choco install innosetup -y
```

**Linux - Missing Dependencies:**
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libqt6core6 libqt6gui6 libqt6widgets6
```

### Debug Workflow

Enable debug logging:
```bash
# In repository secrets
ACTIONS_STEP_DEBUG = true
ACTIONS_RUNNER_DEBUG = true
```

### Re-run Failed Jobs

- Go to failed workflow run
- Click "Re-run failed jobs"
- Or re-run entire workflow

## Security Best Practices

### Secrets Management

**Never:**
- Commit secrets to repository
- Echo secrets in logs
- Use secrets in PR from forks

**Always:**
- Use GitHub secrets
- Rotate secrets regularly
- Use minimal permissions
- Audit secret access

### Dependency Security

```yaml
- name: Security audit
  run: |
    pip install safety
    safety check
```

### Code Signing

**Windows:**
- Use EV code signing certificate
- Timestamp all signatures
- Verify signature after signing

**macOS:**
- Use Developer ID certificate
- Notarize all releases
- Staple notarization ticket

## Performance Metrics

### Target Build Times

| Platform | Target | Current | Status |
|----------|--------|---------|--------|
| Windows  | 10 min | 12 min  | ⚠️ Optimize |
| Linux    | 15 min | 18 min  | ⚠️ Optimize |
| macOS    | 20 min | N/A     | 🚧 Pending |
| Full Release | 25 min | N/A | 🚧 Pending |

### Optimization Targets

- [ ] Implement dependency caching
- [ ] Parallelize build steps
- [ ] Use pre-built wheels
- [ ] Optimize PyInstaller settings
- [ ] Enable incremental builds

## Maintenance

### Regular Tasks

**Weekly:**
- Review failed builds
- Check artifact storage usage
- Update dependencies

**Monthly:**
- Rotate secrets
- Review workflow performance
- Update GitHub Actions versions
- Test full release process

**Quarterly:**
- Security audit
- Dependency updates
- Workflow optimization
- Documentation updates

### Dependency Updates

Use Dependabot:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Migration Guide

### From Local Builds to CI/CD

1. **Test locally:**
   ```bash
   .\build\build_windows.ps1
   ```

2. **Commit build scripts:**
   ```bash
   git add build/
   git commit -m "Add build automation"
   ```

3. **Add workflow:**
   ```bash
   git add .github/workflows/build-windows.yml
   git commit -m "Add Windows CI/CD workflow"
   ```

4. **Test workflow:**
   - Push to develop branch
   - Monitor Actions tab
   - Fix any issues

5. **Enable for main:**
   - Merge to main
   - Tag release: `git tag v0.1.0`
   - Push tag: `git push --tags`

### From Other CI Systems

**From Travis CI:**
- Convert `.travis.yml` to GitHub Actions
- Update environment variables
- Migrate build matrix

**From Jenkins:**
- Convert Jenkinsfile to workflow YAML
- Setup self-hosted runners if needed
- Migrate credentials to secrets

**From GitLab CI:**
- Convert `.gitlab-ci.yml`
- Adjust caching strategy
- Update artifact paths

## Advanced Topics

### Self-Hosted Runners

For faster builds or special requirements:

```yaml
runs-on: self-hosted
```

**Benefits:**
- Faster builds
- Custom tools pre-installed
- Larger disk/memory
- Private network access

**Setup:**
- Settings > Actions > Runners
- Add new self-hosted runner
- Follow installation instructions

### Custom Actions

Create reusable actions:

```yaml
# .github/actions/build-installer/action.yml
name: 'Build Installer'
description: 'Build platform-specific installer'
inputs:
  platform:
    required: true
runs:
  using: 'composite'
  steps:
    - run: ./build/build_${{ inputs.platform }}.sh
```

Usage:
```yaml
- uses: ./.github/actions/build-installer
  with:
    platform: windows
```

### Matrix Strategy

Test multiple configurations:

```yaml
strategy:
  matrix:
    include:
      - os: windows-latest
        arch: x64
      - os: windows-latest
        arch: arm64
      - os: ubuntu-latest
        arch: x64
```

## Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Actions Marketplace:** https://github.com/marketplace?type=actions
- **Workflow Syntax:** https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Security Hardening:** https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions

## Support

For CI/CD issues:
1. Check workflow logs
2. Review this guide
3. Search GitHub Community
4. Open issue with `ci/cd` label
