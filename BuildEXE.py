import sys
import os
import shutil
import PyInstaller.__main__

# Get platform
platform = 'windows' if sys.platform == 'win32' else 'linux'

# Separator for Windows:           ';'
# Separator for Linux/MacOS/Unix:  ':'
separator = ';' if platform == 'windows' else ':'

# Set binary information for GUI version
binary_folder = './lib/' + platform
version_maxsize = '64bits'

# Update binary folder for Windows 32 bits and 64 bits
if platform == 'windows' and sys.maxsize > 2 ** 32:
    binary_folder += '/x64'
elif platform == 'windows':
    binary_folder += '/x32'
    version_maxsize = '32bits'

# Set output name
outname_cli = 'AstroSaveConverterCLI_' + version_maxsize
outname_gui = 'AstroSaveConverterGUI_' + version_maxsize

# Build CLI version
PyInstaller.__main__.run([
    '--name=%s' % outname_cli,
    '--onefile',
    '--add-data=%s' % 'assets/astroconverterlogo.ico' + separator + 'assets/astroconverterlogo.ico',
    '--icon=%s' % 'assets/astroconverterlogo.ico',
    'AstroSaveConverter.py'
])

# Build GUI version
PyInstaller.__main__.run([
    '--name=%s' % outname_gui,
    '--onefile',
    '--add-data=%s' % "assets" + separator + 'assets',
    '--add-binary=%s' % binary_folder + separator + '.',
    '--icon=%s' % 'assets/astroconverterlogo.ico',
    'AstroSaveGui.py'
])

# Remove build files
if os.path.exists('./build'):
    shutil.rmtree('./build')
if os.path.exists('./' + outname_cli + '.spec'):
    os.remove('./' + outname_cli + '.spec')
if os.path.exists('./' + outname_gui + '.spec'):
    os.remove('./' + outname_gui + '.spec')
