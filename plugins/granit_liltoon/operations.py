from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple
from .i18n import tr

class OperationContext(NamedTuple):
    project_id: str
    texture_set: str

    @classmethod
    def from_pair(cls, value):
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError(tr('프로젝트 또는 텍스처셋이 바뀌어 이전 편집을 적용하지 않았습니다.'))
        if any((not isinstance(part, str) or not part for part in value)):
            raise ValueError(tr('프로젝트 또는 텍스처셋이 바뀌어 이전 편집을 적용하지 않았습니다.'))
        return cls(*value)

@dataclass(frozen=True)
class BundleExportRequest:
    material: str
    textures: str
    images: dict
    overwrite: bool

    @classmethod
    def from_options(cls, options):
        return cls(material=options['material'], textures=options['textures'], images=deepcopy(options.get('images', {})), overwrite=options['overwrite'])

@dataclass(frozen=True)
class BundleExportResult:
    material: Path
    binding_key: str

class ExportBindingError(RuntimeError):
    files_committed = True

    def __init__(self, material, cause):
        self.material = Path(material)
        super().__init__(tr('Files were exported to {v0}, but binding the output failed: {v1}', v0=self.material, v1=cause))
