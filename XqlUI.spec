# -*- mode: python -*-
a = Analysis(['XqlUI.py'],
             pathex=['C:\\Users\\Sid\\Documents\\GitHub\\XQL'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='XqlUI.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
