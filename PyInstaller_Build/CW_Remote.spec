# -*- mode: python -*-

block_cipher = None


a = Analysis(['CW_Remote.py'],
             pathex=['/Users/Ken/Documents/CW_Remote_PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='CW_Remote',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='appIcon.icns')
app = BUNDLE(exe,
             name='CW_Remote.app',
             icon='appIcon.icns',
             bundle_identifier='com.techview.cwremote')
