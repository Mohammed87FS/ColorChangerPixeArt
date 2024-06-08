from PyInstaller.utils.hooks import copy_metadata, collect_submodules

datas = copy_metadata('Pillow')
hiddenimports = collect_submodules('PIL')
