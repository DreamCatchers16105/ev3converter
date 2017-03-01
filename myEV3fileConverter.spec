# -*- mode: python -*-

block_cipher = None

a = Analysis(['EV3fileConverter.py'],
             pathex=['C:\\Users\\Kevin.Choi\\PycharmProjects\\ev3converter'],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

a.datas += [('right.gif','C:\\Users\\Kevin.Choi\\PycharmProjects\\ev3converter\\images\\right.gif','Data' )]
a.datas += [('left.gif','C:\\Users\\Kevin.Choi\\PycharmProjects\\ev3converter\\images\\left.gif','Data' )]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='EV3fileConverter.exe',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='C:\\Users\\Kevin.Choi\\PycharmProjects\\ev3converter\\images\\Main_icon.ico')
