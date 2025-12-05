# Lemiex Record App – Release Notes

## v1.0.1 (2025-12-05)

### Highlights
- **Recording limit controls**: Added a dropdown to choose preset durations (3–60 seconds) and auto-stop once the limit is reached.
- **Self-healing device connections**: Scanner and camera auto-refresh in the background, prioritizing `COM3` for scanners and restoring the last-used camera with clear status messaging.
- **Safer order input**: The "Mã đơn" field now accepts numeric characters only, preventing mistakes from manual entry.
- **Dynamic QR experience**: Each session generates a unique QR; scanning it triggers a flash and notification sound so staff can verify the correct workstation.
- **Metadata privacy**: `url_json` is no longer stored locally; JSON metadata is uploaded to Backblaze and scrubbed on disk.

### Packaging & Deployment
- Writable configs for EXE builds: configuration files are copied next to the executable on first run so they can be edited without unpacking the bundle.
- Updated `build.bat`: activates the virtual environment, ensures PyInstaller is available, reads the version from `config/config.yaml`, and assembles a ready-to-ship `LemiexRecordApp_v1.0.1.zip` folder (with config, docs, and requirements).
- Dependency fixes: bundled wheels now include `pygame==2.6.1` and `qrcode[pil]==7.4.2`, eliminating earlier `ModuleNotFoundError` crashes.

### Bug Fixes
- Scanner reconnect loop now guards against missing references and restores the combo-box selection after auto-detection.
- QR flash animation safely skips when the widget is absent to avoid runtime errors during startup.
- Progress tracking can handle multiple concurrent uploads and remains visible while transfers overlap.

### Known Issues
- PyInstaller still warns about vendored `setuptools` modules (`typing_extensions`, `importlib_metadata`, etc.); these do not affect runtime behavior.
- `b2sdk.v2.B2Api` warnings persist because the hook attempts to force-include optional modules; uploads continue to function normally.

### Upgrade Steps
1. Download `LemiexRecordApp_v1.0.1.zip` from GitHub Releases.
2. Extract to a writable directory.
3. Copy your existing `.env` (or edit the new `.env.example`) with Backblaze credentials.
4. Adjust `config/config.yaml` in the extracted folder if you need custom ports or recording limits.
5. Launch `LemiexRecordApp.exe` and verify scanner/camera indicators turn green.
6. Remove older distribution folders to avoid confusion, then tag/publish the new release.
