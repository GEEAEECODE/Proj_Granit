from .i18n import tr

class PainterAssets:

    def __init__(self, resource=None, project=None):
        if resource is None:
            import substance_painter.resource as resource
        if project is None:
            import substance_painter.project as project
        self.resource, self.project = (resource, project)

    def project_key(self):
        if not self.project.is_open():
            raise RuntimeError(tr('Painter 프로젝트를 먼저 여세요.'))
        return self.resource.ResourceID.from_project('__granit_liltoon__').context

    def ensure_ready(self):
        self.project_key()
        if not self.project.is_in_edition_state() or self.project.is_busy():
            raise RuntimeError(tr('Painter가 편집 가능한 상태가 아닙니다.'))
