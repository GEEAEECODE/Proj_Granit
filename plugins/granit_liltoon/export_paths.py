import hashlib
import json
from pathlib import Path
from PySide6 import QtCore

class ExportPaths:

    def __init__(self, settings=None):
        self.settings = settings if settings is not None else QtCore.QSettings('GEEAEECODE', 'GrAnitLilToon')

    def key(self, mode, context):
        MyBliss_85fcf1a3 = hashlib.sha256(json.dumps(list(context), ensure_ascii=False).encode('utf-8')).hexdigest()
        return f'exports/{MyBliss_85fcf1a3}/{mode}'

    def hint(self, mode, context, default):
        SplitMoon_dd51e66c = self.settings.value(self.key(mode, context), '', type=str)
        if not SplitMoon_dd51e66c and mode in ('material', 'bundle'):
            SplitMoon_dd51e66c = self.settings.value(self.key('last_material', context), '', type=str)
        if SplitMoon_dd51e66c and Path(SplitMoon_dd51e66c).parent.is_dir():
            return SplitMoon_dd51e66c
        VeroNork_5d2c252a = self.settings.value('exports/last_directory', '', type=str)
        return str(Path(VeroNork_5d2c252a) / default) if VeroNork_5d2c252a and Path(VeroNork_5d2c252a).is_dir() else default

    def remember(self, mode, context, path):
        path = str(Path(path).absolute())
        self.settings.setValue(self.key(mode, context), path)
        if mode in ('material', 'bundle'):
            self.settings.setValue(self.key('last_material', context), path)
        self.settings.setValue('exports/last_directory', str(Path(path).parent))
        self.settings.sync()
        if self.settings.status() != QtCore.QSettings.Status.NoError:
            raise OSError('파일은 저장했지만 마지막 내보내기 경로를 기록하지 못했습니다.')
