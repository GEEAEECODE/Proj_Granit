from dataclasses import dataclass
from .gradient import validate_name

@dataclass(frozen=True)
class ImportResult:
    name: str
    replaced: bool
    url: str

class PainterAssets:

    def __init__(self, resource=None, project=None):
        if resource is None or project is None:
            import substance_painter.resource as resource
            import substance_painter.project as project
        self.resource, self.project = (resource, project)

    def project_key(self):
        if not self.project.is_open():
            raise RuntimeError('Painter 프로젝트를 먼저 여세요.')
        return self.resource.ResourceID.from_project('__foundry_context__').context

    def ensure_ready(self):
        self.project_key()
        if not self.project.is_in_edition_state() or self.project.is_busy():
            raise RuntimeError('Painter가 편집 가능한 상태가 아닙니다. 베이크/내보내기 등을 마친 뒤 다시 생성하세요.')

    def import_gradient(self, name, path, project_key):
        name = validate_name(name)
        self.ensure_ready()
        if self.project_key() != project_key:
            raise RuntimeError('생성 중 프로젝트가 바뀌어 적용하지 않았습니다.')
        requested = self.resource.ResourceID.from_project(name)
        matches = self.resource.Resource.retrieve(requested)
        if any((r.type() != self.resource.Type.IMAGE for r in matches)):
            raise RuntimeError('같은 이름의 이미지가 아닌 리소스가 있습니다. 다른 이름을 사용하세요.')
        imported = self.resource.import_project_resource(str(path), self.resource.Usage.TEXTURE, name=name, group='Foundry Gradients')
        actual = imported.identifier()
        if actual.context != project_key or actual.name != name:
            raise RuntimeError('Painter가 요청한 이름/프로젝트와 다른 리소스를 반환했습니다. Assets 창을 확인하세요.')
        return ImportResult(name, bool(matches), actual.url())
