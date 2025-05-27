from setuptools import setup

APP = ['timelapse-screencast.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'tkinter', 'cv2', 'numpy', 'mss', 'pyaudio', 
        'moviepy', 'pystray', 'PIL', 'pkg_resources'
    ],
    'includes': [
        'pyaudio', 'moviepy.editor', 'pystray', 
        'PIL.Image', 'PIL.ImageDraw', 'distutils'
    ],
    'excludes': ['distutils.tests'],  # Evita erros de módulos desnecessários
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
# from setuptools import setup

# APP = ['timelapse-screencast.py']
# DATA_FILES = []
# OPTIONS = {
#     'argv_emulation': True,
#     'packages': ['cv2', 'numpy', 'mss', 'pyaudio', 'moviepy'],
#     'includes': ['moviepy.video.fx.all', 'cv2', 'numpy'],  # Inclua todas as bibliotecas necessárias
#     'plist': {
#         'CFBundleIdentifier': 'com.seuapp.timelapse',
#         'CFBundleName': 'TimelapseScreencast',
#         'CFBundleVersion': '1.0.0',
#     },
# }

# setup(
#     app=APP,
#     data_files=DATA_FILES,
#     options={'py2app': OPTIONS},
#     setup_requires=['py2app'],
# )
