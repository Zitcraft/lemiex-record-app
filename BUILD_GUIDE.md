# Build Guide - Lemiex Record App

Hướng dẫn build ứng dụng Lemiex Record thành file executable (.exe) cho Windows.

## 📋 Yêu cầu

- Python 3.8+
- PyInstaller (đã cài: `pip install pyinstaller`)
- Tất cả dependencies trong `requirements.txt`
- Windows OS (để build file .exe)

## 🚀 Build Nhanh

### Option 1: Sử dụng Build Script (Khuyến nghị)

```powershell
.\build.bat
```

Script sẽ tự động:
1. Kiểm tra và cài PyInstaller nếu cần
2. Dọn dẹp build cũ
3. Build executable với PyInstaller
4. Tạo distribution folder với structure đầy đủ
5. Tạo ZIP archive để phân phối

### Option 2: Build Thủ Công

```powershell
# Build với .spec file
pyinstaller --clean Lemiex-record-app.spec

# Executable sẽ ở: dist\LemiexRecordApp.exe
```

## 📦 Cấu trúc Build

### Files quan trọng:

- **`Lemiex-record-app.spec`** - PyInstaller configuration
- **`version_info.txt`** - Windows version information
- **`build.bat`** - Automated build script
- **`logo/logo.ico`** - Application icon (256x256)

### Build Output:

```
dist/
└── LemiexRecordApp.exe     ← Main executable (~80-120 MB)

LemiexRecordApp_v1.0.0/     ← Distribution folder
├── LemiexRecordApp.exe
├── .env.example
├── README.md
├── USER_MANUAL.md
├── INSTALL_PORTABLE.md
├── logs/                   ← Empty folder (created at runtime)
├── temp_videos/           ← Empty folder (created at runtime)
└── metadata/              ← Empty folder (created at runtime)

LemiexRecordApp_v1.0.0.zip  ← Distribution archive
```

## ⚙️ Cấu hình Build

### Data Files (Bundled inside .exe):

- `config/config.yaml` - Application configuration
- `voice/1_start_record.mp3` - Start recording sound
- `voice/2_end_record.mp3` - End recording sound
- `voice/3_dupcode_continue.mp3` - Duplicate warning sound
- `logo/logo.ico` - Application icon
- `.env.example` - Environment template

### Hidden Imports (Python modules):

```python
'b2sdk.v2',                    # Backblaze B2 SDK
'serial.tools.list_ports',     # Scanner COM port detection
'logging.handlers',            # Log rotation
'pygame.mixer',                # Audio playback
'pygame._sdl2',               # Pygame SDL2 backend
'customtkinter',              # GUI framework
'PIL._tkinter_finder',        # Pillow Tkinter integration
'yaml',                       # YAML config parser
'dotenv',                     # Environment variables
'tempfile',                   # Update system
'subprocess',                 # Update system
```

### Excluded Modules (Reduce size):

```python
'matplotlib',  # Not used
'scipy',       # Not used
'pandas',      # Not used
'notebook',    # Not used
'IPython',     # Not used
'jupyter',     # Not used
```

## 🔄 Auto-Update System

### Configuration:

File `config/config.yaml`:
```yaml
app:
  version: "1.0.0"
  github_repo: "yourusername/lemiex-record-app"  # ← Update this!
  check_updates_on_startup: true
```

### Update Flow (Portable Version):

1. App checks GitHub Releases API on startup
2. If newer version found, shows dialog
3. User clicks "Yes" to download
4. Downloads new .exe to temp folder
5. Opens Explorer with the file
6. User manually replaces old .exe with new one

### Publishing Updates:

1. Update version in `config/config.yaml` (e.g., "1.0.1")
2. Update version in `version_info.txt`
3. Build new executable
4. Create GitHub Release:
   ```
   Tag: v1.0.1
   Title: Lemiex Record App v1.0.1
   Upload: LemiexRecordApp.exe (from dist/)
   ```
5. Users will be notified on next app launch

## 🛠️ Troubleshooting

### Build fails with "module not found"

**Solution:** Add missing module to `hiddenimports` in `.spec` file:
```python
hiddenimports=[
    # ... existing imports ...
    'missing_module_name',
]
```

### Executable crashes on startup

**Causes:**
- Missing data files → Check `datas` in `.spec`
- Missing DLLs → Add `--collect-all opencv-python`
- Config file not found → Ensure `config/config.yaml` is bundled

**Debug:**
```powershell
# Run with console to see errors
# In .spec file, change:
console=True  # instead of False
```

### Icon not showing

**Causes:**
- Icon file not found at build time
- Icon format incorrect (must be .ico)
- Icon too large (use 256x256 max)

**Solution:**
```powershell
# Verify icon exists
dir logo\logo.ico

# Rebuild with clean
pyinstaller --clean Lemiex-record-app.spec
```

### Large file size

**Current size:** ~80-120 MB (expected for OpenCV + CustomTkinter app)

**To reduce:**
1. Add more exclusions in `.spec`:
   ```python
   excludes=['tkinter.test', 'unittest', 'test'],
   ```
2. Use UPX compression (already enabled):
   ```python
   upx=True,
   ```
3. Remove unused imports from source code

### Audio not working

**Causes:**
- pygame mixer DLLs missing
- Sound files not bundled

**Solution:**
```python
# In .spec file, ensure:
hiddenimports=[
    'pygame.mixer',
    'pygame._sdl2',
    'pygame._sdl2.audio',
    'pygame._sdl2.mixer',
]

datas=[
    ('voice/*.mp3', 'voice'),
]
```

### Camera not detected

**Causes:**
- OpenCV backend missing
- MSMF framework not available

**Solution:**
- Ensure running on Windows 10/11
- Install Visual C++ Redistributable
- Try different camera index (0, 1, 2) in app

### Update check fails

**Causes:**
- Invalid GitHub repo format
- Network/firewall blocking GitHub API
- Rate limit exceeded (60 requests/hour unauthenticated)

**Solution:**
```yaml
# Disable auto-update temporarily:
check_updates_on_startup: false
```

## 📝 Version Update Checklist

Khi release version mới:

- [ ] Update `config/config.yaml` → `app.version`
- [ ] Update `version_info.txt` → `filevers` và `prodvers`
- [ ] Update changelog/release notes
- [ ] Build executable: `.\build.bat`
- [ ] Test executable on clean Windows machine
- [ ] Create GitHub Release with tag (e.g., `v1.0.1`)
- [ ] Upload `LemiexRecordApp.exe` to release
- [ ] Attach `LemiexRecordApp_v1.0.1.zip` for full package
- [ ] Notify users

## 🔐 Code Signing (Optional)

Để tránh Windows SmartScreen warning:

1. Purchase Code Signing Certificate (~$100-200/year)
2. Install certificate on build machine
3. Sign executable:
   ```powershell
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\LemiexRecordApp.exe
   ```

## 📊 Build Performance

| Stage | Time | Output |
|-------|------|--------|
| Clean | ~2s | Removes build/, dist/ |
| Analysis | ~15s | Analyzes imports |
| Build | ~30-60s | Creates executable |
| Package | ~5s | Creates distribution folder |
| ZIP | ~10s | Creates archive |
| **Total** | **~1-2 min** | Ready to distribute |

## 🎯 Distribution

### For End Users:

1. Provide `LemiexRecordApp_v1.0.0.zip`
2. Extract to desired location (e.g., `C:\Program Files\LemiexRecordApp\`)
3. Copy `.env.example` → `.env` and configure B2 credentials
4. Run `LemiexRecordApp.exe`
5. Folders `logs/`, `temp_videos/`, `metadata/` created automatically

### Portable Features:

✅ No installation required
✅ No registry changes
✅ Self-contained executable
✅ Can run from USB drive
✅ Easy to backup (just copy folder)
✅ Auto-update via GitHub Releases

## 📚 Additional Resources

- PyInstaller Documentation: https://pyinstaller.org/
- CustomTkinter: https://github.com/TomSchimansky/CustomTkinter
- B2 SDK: https://github.com/Backblaze/b2-sdk-python
- GitHub Releases API: https://docs.github.com/en/rest/releases

## 🐛 Support

Issues with build process?
1. Check logs in `build/` folder
2. Run with console enabled for debugging
3. Verify all dependencies installed: `pip list`
4. Try clean build: `pyinstaller --clean Lemiex-record-app.spec`
