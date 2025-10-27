# Release Process

This document explains how to create releases for netmiko-collector with automatically built Windows executables.

## Automated Release Workflow

The project uses GitHub Actions to automatically build Windows executables and create releases. The workflow is defined in `.github/workflows/release.yml`.

### Trigger Methods

The release workflow can be triggered in **three ways**:

#### Method 1: Push a Git Tag (Recommended)

```bash
# Update version in pyproject.toml first
# Then create and push a tag
git tag v2.0.1
git push origin v2.0.1
```

**What happens:**
- ✅ Automatically builds Windows executable
- ✅ Creates GitHub release with tag
- ✅ Uploads executable to release
- ✅ Generates release notes

#### Method 2: Merge PR with "release" Label or Title

Create a PR with either:
- A label named `release`
- "release" in the PR title (e.g., "Release v2.0.1" or "Prepare release 2.0.1")

**What happens when merged:**
- ✅ Automatically builds Windows executable
- ✅ Creates GitHub release using version from `pyproject.toml`
- ✅ Uploads executable to release
- ✅ Posts comment on PR with release link

#### Method 3: Manual Workflow Dispatch

Go to **Actions** → **Build and Release** → **Run workflow**

Specify the version (e.g., `2.0.1`)

**What happens:**
- ✅ Builds Windows executable for specified version
- ✅ Creates or updates release
- ✅ Uploads executable

## Release Checklist

### Pre-Release

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `installer.iss` (if changed)
- [ ] Update `CHANGELOG.md` with changes
- [ ] Run tests locally: `pytest`
- [ ] Test executable locally: `build_installer.bat`
- [ ] Verify executable works: `dist\netmiko-collector.exe --version`
- [ ] Commit all changes

### Creating Release

**Option A: Tag Method**
```bash
git tag v2.0.1
git push origin v2.0.1
```

**Option B: PR Method**
```bash
git checkout -b release/v2.0.1
# Make changes
git add .
git commit -m "chore: prepare release v2.0.1"
git push origin release/v2.0.1
# Create PR with "release" label or "Release v2.0.1" title
# Merge PR → workflow runs automatically
```

### Post-Release

- [ ] Verify release created on GitHub
- [ ] Download and test the executable from release
- [ ] Update documentation if needed
- [ ] Announce release (if applicable)

## What the Workflow Does

### 1. Check Trigger
- Determines if build should run
- Extracts version number
- Validates trigger conditions

### 2. Build Windows Executable
Runs on: `windows-latest`

Steps:
1. Sets up Python 3.11
2. Installs dependencies
3. Builds executable with PyInstaller
4. Tests executable (`--version`)
5. Creates build info markdown
6. Uploads artifacts

Time: ~5-10 minutes

### 3. Create/Update Release
Runs on: `ubuntu-latest`

Steps:
1. Downloads build artifacts
2. Checks if release exists
3. Creates new release OR updates existing
4. Uploads executable
5. Generates release notes
6. Comments on PR (if applicable)

## Release Assets

Each release includes:

**1. netmiko-collector.exe**
- Standalone Windows executable
- ~22 MB
- No Python required
- All dependencies bundled

**2. Auto-generated release notes**
- Commit history since last release
- PR links
- Contributors

**3. Build information**
- Executable size
- Python version used
- Build date and commit
- Usage instructions

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes
- **Minor** (x.X.0): New features, backward compatible
- **Patch** (x.x.X): Bug fixes, backward compatible

Examples:
- `v2.0.0` → Major release with breaking changes
- `v2.1.0` → New features added
- `v2.1.1` → Bug fixes

## Troubleshooting

### Workflow doesn't trigger on PR merge

**Check:**
- Does PR have "release" label?
- Does PR title contain "release"?
- Was PR actually merged (not just closed)?

**Solution:**
Use manual workflow dispatch or tag method instead.

### Executable build fails

**Common issues:**
1. **Import errors** → Check `hiddenimports` in `netmiko-collector.spec`
2. **Missing dependencies** → Verify `requirements.txt` is complete
3. **Test failure** → Executable doesn't run → Check `run_netmiko_collector.py`

**Debug locally:**
```bash
build_installer.bat
dist\netmiko-collector.exe --version
```

### Release already exists

The workflow will **update** the existing release with the new executable.

To create a new release:
1. Update version in `pyproject.toml`
2. Create new tag: `git tag v2.0.2`
3. Push: `git push origin v2.0.2`

### Wrong version in release

The workflow gets version from:
1. **Tag method**: Tag name (e.g., `v2.0.1`)
2. **PR method**: `pyproject.toml`
3. **Manual**: Input parameter

Make sure version is correct in the appropriate source.

## Manual Release (Without Workflow)

If you need to create a release manually:

1. **Build executable locally:**
   ```batch
   build_installer.bat
   ```

2. **Create release on GitHub:**
   - Go to Releases → New Release
   - Create tag (e.g., `v2.0.1`)
   - Upload `dist\netmiko-collector.exe`
   - Write release notes
   - Publish

## CI/CD Pipeline

```
┌─────────────────────┐
│   Trigger Event     │
│  (Tag/PR/Manual)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Check Trigger      │
│  - Validate event   │
│  - Get version      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Build Windows      │
│  - Install deps     │
│  - PyInstaller      │
│  - Test exe         │
│  - Upload artifact  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Create Release     │
│  - Download assets  │
│  - Create/update    │
│  - Upload exe       │
│  - Comment on PR    │
└─────────────────────┘
```

## Best Practices

### ✅ Do

- Always test locally before tagging
- Use semantic versioning
- Update CHANGELOG.md
- Write clear commit messages
- Test the downloaded executable from release

### ❌ Don't

- Don't push tags without updating version in `pyproject.toml`
- Don't create releases for every PR (use release label)
- Don't manually edit release assets (use workflow)
- Don't skip testing the executable

## Examples

### Example 1: Patch Release

```bash
# Update version
# pyproject.toml: version = "2.0.1"

# Commit
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 2.0.1"
git push

# Tag and push
git tag v2.0.1
git push origin v2.0.1

# Wait for workflow to complete (~5-10 minutes)
# Check: https://github.com/lammesen/netmiko-script/releases
```

### Example 2: Feature Release via PR

```bash
# Create feature branch
git checkout -b release/v2.1.0

# Update version
# pyproject.toml: version = "2.1.0"

# Update changelog
# CHANGELOG.md: Add ## [2.1.0] section

# Commit and push
git add .
git commit -m "feat: add new feature X

Prepare release v2.1.0"
git push origin release/v2.1.0

# Create PR with title: "Release v2.1.0"
# Or add "release" label
# Merge PR → workflow runs automatically
```

### Example 3: Hotfix Release

```bash
# Fix critical bug
git checkout -b hotfix/v2.0.2
# ... make fixes ...
git commit -m "fix: critical security issue"

# Update version
# pyproject.toml: version = "2.0.2"

# Push and tag
git push origin hotfix/v2.0.2
git tag v2.0.2
git push origin v2.0.2

# Workflow creates release immediately
```

## Support

For issues with the release process:
- Check workflow logs: Actions → Build and Release → Latest run
- Review this document
- Open an issue: https://github.com/lammesen/netmiko-script/issues

---

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")
**Workflow Version:** 2.0
