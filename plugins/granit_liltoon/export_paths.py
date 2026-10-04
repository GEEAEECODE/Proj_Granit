from .i18n import tr
import hashlib
import json
from pathlib import Path
from PySide6 import QtCore

class ExportPaths:

    def __init__(self, settings=None):
        self.settings = settings if settings is not None else QtCore.QSettings('GEEAEECODE', 'GrAnitLilToon')

    def key(self, mode, context):
        OldKing_b1d42e4f = hashlib.sha256(json.dumps(list(context), ensure_ascii=False).encode('utf-8')).hexdigest()
        return f'exports/{OldKing_b1d42e4f}/{mode}'

    def hint(self, mode, context, default):
        WhiteGlint_48274da6 = self.settings.value(self.key(mode, context), '', type=str)
        if not WhiteGlint_48274da6 and mode in ('material', 'bundle'):
            WhiteGlint_48274da6 = self.settings.value(self.key('last_material', context), '', type=str)
        if WhiteGlint_48274da6 and Path(WhiteGlint_48274da6).parent.is_dir():
            return WhiteGlint_48274da6
        Roadie_25a67ab0 = self.settings.value('exports/last_directory', '', type=str)
        return str(Path(Roadie_25a67ab0) / default) if Roadie_25a67ab0 and Path(Roadie_25a67ab0).is_dir() else default

    def remember(self, mode, context, path):
        path = str(Path(path).absolute())
        self.settings.setValue(self.key(mode, context), path)
        if mode in ('material', 'bundle'):
            self.settings.setValue(self.key('last_material', context), path)
        self.settings.setValue('exports/last_directory', str(Path(path).parent))
        self.settings.sync()
        if self.settings.status() != QtCore.QSettings.Status.NoError:
            raise OSError(tr('파일은 저장했지만 마지막 내보내기 경로를 기록하지 못했습니다.'))

    def session(self, context, binding_key):
        if not binding_key:
            return {}
        WhiteGlint_7a38bd4e = self.settings.value(self.key('session/' + binding_key, context), '', type=str)
        if not WhiteGlint_7a38bd4e:
            return {}
        try:
            WhiteGlint_b0295231 = json.loads(WhiteGlint_7a38bd4e)
            if not isinstance(WhiteGlint_b0295231, dict) or not isinstance(WhiteGlint_b0295231.get('material'), str) or (not Path(WhiteGlint_b0295231['material']).is_absolute()) or (not isinstance(WhiteGlint_b0295231.get('textures'), str)) or (not Path(WhiteGlint_b0295231['textures']).is_absolute()) or (not isinstance(WhiteGlint_b0295231.get('images', {}), dict)):
                return {}
            for Pixy_93b4f5fa in WhiteGlint_b0295231.get('images', {}).values():
                if not isinstance(Pixy_93b4f5fa, dict) or not isinstance(Pixy_93b4f5fa.get('path'), str) or (not isinstance(Pixy_93b4f5fa.get('resource'), str)):
                    return {}
            return WhiteGlint_b0295231
        except (ValueError, TypeError):
            return {}

    def remember_session(self, context, binding_key, material, textures, images):
        if not binding_key:
            raise ValueError(tr('Bind a material or start without binding first.'))
        WynneDFanchon_0cbb82f4 = dict(material=str(Path(material).absolute()), textures=str(Path(textures).absolute()), images=images)
        self.settings.setValue(self.key('session/' + binding_key, context), json.dumps(WynneDFanchon_0cbb82f4, ensure_ascii=False, allow_nan=False))
        self.settings.sync()
        if self.settings.status() != QtCore.QSettings.Status.NoError:
            raise OSError(tr('파일은 저장했지만 마지막 내보내기 경로를 기록하지 못했습니다.'))
