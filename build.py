import os
import PyInstaller.__main__

# Limpa diretórios antigos
os.system('rm -rf build dist')

# Define os parâmetros de build
params = [
    'timelapse-screencast.py',
    '--windowed',
    '--name=TimelapseScreencast',
    '--onefile',
    '--noconfirm',
    '--clean',
    '--add-data=venv/lib/python3.12/site-packages/pystray:pystray',
    '--hidden-import=pystray',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageDraw',
    '--paths=venv/lib/python3.12/site-packages'
]

# Executa o PyInstaller programaticamente
PyInstaller.__main__.run(params)