# -*- mode: python -*-

block_cipher = None

a = Analysis(['EV3fileConverter.py'],
             pathex=['/Users/kchoi/PycharmProjects/ev3converter'],
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

a.datas += [('right.gif','/Users/kchoi/PycharmProjects/ev3converter/images/right.gif','Data' )]
a.datas += [('left.gif','/Users/kchoi/PycharmProjects/ev3converter/images/left.gif','Data' )]
a.datas += [('lego-512.gif','/Users/kchoi/PycharmProjects/ev3converter/images/lego-512.gif','Data' )]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='EV3fileConverter',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='/Users/kchoi/PycharmProjects/ev3converter/images/lego-512.gif')

app = BUNDLE(exe,
             name='EV3fileConverter.app',
             icon='/Users/kchoi/PycharmProjects/ev3converter/images/lego-512.gif',
             bundle_identifier=None)

