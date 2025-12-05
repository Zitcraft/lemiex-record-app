# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/config.yaml', 'config'),
        ('voice/1_start_record.mp3', 'voice'),
        ('voice/2_end_record.mp3', 'voice'),
        ('voice/3_dupcode_continue.mp3', 'voice'),
        ('logo/logo.ico', 'logo'),
        ('qr_codes/USB-COM.png', 'qr_codes'),
        ('qr_codes/Factory-Default.png', 'qr_codes'),
        ('qr_codes/app-identifier.png', 'qr_codes'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        # B2SDK internal modules
        'b2sdk.v2',
        'b2sdk.v2.B2Api',
        'b2sdk.v2.InMemoryAccountInfo',
        'b2sdk.v2.exception',
        # Serial port tools
        'serial.tools.list_ports',
        # Logging handlers
        'logging.handlers',
        # Pygame mixer for audio
        'pygame',
        'pygame.mixer',
        'pygame._sdl2',
        'pygame._sdl2.audio',
        'pygame._sdl2.mixer',
        # CustomTkinter internals
        'customtkinter',
        'PIL._tkinter_finder',
        # YAML loader
        'yaml',
        # Dotenv
        'dotenv',
        # Updater dependencies
        'tempfile',
        'subprocess',
        # Dynamic QR generator
        'uuid',
        'qrcode',
        'qrcode.image.pil',
        'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'notebook',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LemiexRecordApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo/logo.ico',
    version_file='version_info.txt',
)
