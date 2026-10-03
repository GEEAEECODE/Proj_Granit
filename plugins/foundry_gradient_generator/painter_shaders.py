from copy import deepcopy
import hashlib
import json
import uuid
from .definitions import shader_path
from .diagnostics import log
METADATA_CONTEXT = 'GrAnitShader'

def rebase_project_urls(data, old_context, new_context):
    old_prefix = 'resource://' + old_context + '/'
    new_prefix = 'resource://' + new_context + '/'

    def visit(value):
        if isinstance(value, str) and value.startswith(old_prefix):
            return new_prefix + value[len(old_prefix):]
        if isinstance(value, list):
            return [visit(v) for v in value]
        if isinstance(value, dict):
            return {k: deepcopy(v) if k in ('name', 'label') else visit(v) for k, v in value.items()}
        return deepcopy(value)
    return visit(data)

def validate_snapshot(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get('format', {}).get('version') != '1.0' or (not isinstance(snapshot.get('shaders'), dict)) or (not isinstance(snapshot.get('texturesets'), dict)):
        raise ValueError('지원하지 않는 Painter 셰이더 연결 형식입니다. 적용하지 않았습니다.')
    for name, item in snapshot['texturesets'].items():
        if not isinstance(item, dict) or item.get('shader') not in snapshot['shaders']:
            raise ValueError(f'텍스처셋 {name}의 셰이더 연결을 확인할 수 없습니다.')
    return snapshot

class PainterShaders:

    def __init__(self, assets, js=None, texture_sets=None):
        if js is None:
            import substance_painter.js as js
        self.assets, self.js = (assets, js)
        self._texture_sets = texture_sets

    def ready(self):
        project = self.assets.project
        return project.is_open() and project.is_in_edition_state() and (not project.is_busy())

    def project_key(self):
        self.assets.ensure_ready()
        return str(self.assets.project.get_uuid())

    def _call(self, function, *args):
        self.assets.ensure_ready()
        arguments = ','.join((json.dumps(a, ensure_ascii=True, allow_nan=False) for a in args))
        return self.js.evaluate(f'{function}({arguments})')

    def snapshot(self):
        return validate_snapshot(self._call('alg.shaders.shaderInstancesToObject'))

    def active_texture_set(self, *, validate=True):
        self.assets.ensure_ready()
        if self._texture_sets is None:
            import substance_painter.textureset as texture_sets
            self._texture_sets = texture_sets
        try:
            stack = self._texture_sets.get_active_stack()
        except RuntimeError as exc:
            raise RuntimeError('Painter에서 적용할 텍스처셋을 먼저 선택하세요.') from exc
        if stack is None:
            raise RuntimeError('Painter에서 적용할 텍스처셋을 먼저 선택하세요.')
        name = str(stack.material().name)
        if validate and name not in self.snapshot()['texturesets']:
            raise RuntimeError('선택한 텍스처셋을 프로젝트에서 찾을 수 없습니다. 다시 선택하세요.')
        return name

    def instances(self):
        return self._call('alg.shaders.instances')

    def parameters(self, native_id):
        self.assets.ensure_ready()
        native_id = int(native_id)
        script = '(function() {\n            var p=alg.shaders.parameters(%d), result={};\n            for (var key in p) result[key]={value:p[key].value, description:p[key].description};\n            return result;\n        })()' % native_id
        return self.js.evaluate(script)

    def set_parameters(self, label, resource_url, values):
        native = self.find_native(label)
        if native is None or native['url'] != resource_url:
            raise RuntimeError('Painter에서 셰이더 연결이 바뀌었습니다. 목록을 새로고침하세요.')
        supported = self.parameters(native['id'])
        values = {key: value for key, value in values.items() if key in supported}
        if values:
            self._call('alg.shaders.setParameters', native['id'], values, {'undoable': True})

    def find_native(self, label):
        matches = [s for s in self.instances() if s['label'] == label]
        if len(matches) > 1:
            raise RuntimeError('Painter 셰이더 이름이 중복되어 적용 대상을 구분할 수 없습니다.')
        return matches[0] if matches else None

    def load_metadata(self):
        metadata = self.assets.project.Metadata(METADATA_CONTEXT)
        if 'state' not in metadata.list():
            return None
        value = metadata.get('state')
        data = json.loads(value) if isinstance(value, str) else value
        old_context = data.get('resource_context', '') if isinstance(data, dict) else ''
        current = self.assets.project_key()
        if old_context and old_context != current:
            data = rebase_project_urls(data, old_context, current)
            data['resource_context'] = current
        return data

    def save_metadata(self, data):
        self.assets.ensure_ready()
        data = deepcopy(data)
        data['resource_context'] = self.assets.project_key()
        payload = json.dumps(data, ensure_ascii=False, allow_nan=False)
        self.assets.project.Metadata(METADATA_CONTEXT).set('state', payload)

    def ensure_resource(self, shader, preferred_url=''):
        self.assets.ensure_ready()
        resource = self.assets.resource
        if preferred_url:
            identifier = resource.ResourceID.from_url(preferred_url)
            matches = resource.Resource.retrieve(identifier)
            if matches:
                if len(matches) != 1 or matches[0].type() != resource.Type.SHADER:
                    raise RuntimeError('저장된 GrAnit 리소스가 셰이더가 아닙니다.')
                return (matches[0].identifier().url(), identifier.name)
        path = shader_path(shader)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        name = f'Granit_Ramp_{digest}'
        matches = resource.Resource.retrieve(resource.ResourceID.from_project(name))
        if matches:
            if len(matches) != 1 or matches[0].type() != resource.Type.SHADER:
                raise RuntimeError('GrAnit 셰이더 리소스 이름이 다른 리소스와 충돌합니다.')
            return (matches[0].identifier().url(), name)
        imported = resource.import_project_resource(str(path), resource.Usage.SHADER, name=name, group='GrAnit Shaders')
        identifier = imported.identifier()
        if identifier.context != self.assets.project_key() or identifier.name != name:
            raise RuntimeError('Painter가 요청한 프로젝트/이름과 다른 셰이더 리소스를 반환했습니다.')
        log('셰이더 리소스 임포트 완료', url=identifier.url())
        return (identifier.url(), name)

    def _write_snapshot(self, before, after, texture_set=None, target_label=None):
        validate_snapshot(after)
        try:
            self._call('alg.shaders.shaderInstancesFromObject', after)
            actual = self.snapshot()
            for label in after['shaders'].keys() - before['shaders'].keys():
                if self.find_native(label) is None:
                    raise RuntimeError('Painter가 새 셰이더 인스턴스를 만들지 않았습니다.')
            for name, item in before['texturesets'].items():
                expected = target_label if name == texture_set else item['shader']
                if actual['texturesets'].get(name, {}).get('shader') != expected:
                    raise RuntimeError(f'Painter 텍스처셋 적용 확인 실패: {name}')
            for name, item in before['shaders'].items():
                referenced = any((t['shader'] == name for t in after['texturesets'].values()))
                if referenced and after['shaders'].get(name) == item and (actual['shaders'].get(name) != item):
                    raise RuntimeError(f'대상 외 셰이더 설정 보존 확인 실패: {name}')
            return actual
        except Exception as exc:
            log('셰이더 매핑 적용 실패', error=str(exc), requested=list(after['shaders']))
            try:
                self._call('alg.shaders.shaderInstancesFromObject', before)
            except Exception as rollback:
                raise RuntimeError(f'{exc}; 이전 연결 복구도 실패했습니다: {rollback}') from exc
            raise

    def apply_instance(self, texture_set, label, shader, resource_url, values):
        before = self.snapshot()
        if texture_set not in before['texturesets']:
            raise RuntimeError('텍스처셋이 더 이상 존재하지 않습니다.')
        native = self.find_native(label)
        if native is not None and native['url'] != resource_url:
            raise RuntimeError('Painter의 셰이더 연결이 변경되어 적용하지 않았습니다.')
        url, name = self.ensure_resource(shader, resource_url)
        after = deepcopy(before)
        entry = after['shaders'].setdefault(label, {'shader': name, 'shaderInstance': label, 'parameters': {}, 'materials': {}})
        for identifier, value in values.items():
            definition = shader.parameters.get(identifier)
            if definition is None:
                continue
            if definition.data_type == 'ByteArray' and (not value):
                continue
            section = 'materials' if definition.data_type == 'ByteArray' else 'parameters'
            entry.setdefault(section, {}).setdefault(definition.group, {})[identifier] = deepcopy(value)
        after['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(before, after, texture_set, label)
        try:
            native = self.find_native(label)
            if native is None:
                raise RuntimeError('텍스처셋에 연결할 Painter 인스턴스를 만들지 못했습니다.')
            if native['url'] != url:
                self._call('alg.shaders.updateShaderInstance', native['id'], url)
            self.set_parameters(label, url, values)
            log('셰이더 인스턴스 적용 완료', texture_set=texture_set, label=label, url=url)
            return url
        except Exception as exc:
            self._rollback(before, exc)

    def _rollback(self, before, error):
        try:
            self._call('alg.shaders.shaderInstancesFromObject', before)
        except Exception as rollback:
            raise RuntimeError(f'{error}; 이전 연결 복구도 실패했습니다: {rollback}') from error
        raise error

    def assign(self, texture_set, label):
        before = self.snapshot()
        if texture_set not in before['texturesets'] or label not in before['shaders']:
            raise RuntimeError('텍스처셋 또는 셰이더가 더 이상 존재하지 않습니다.')
        after = deepcopy(before)
        after['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(before, after, texture_set, label)

    def capture(self, texture_set):
        snapshot = self.snapshot()
        label = snapshot['texturesets'][texture_set]['shader']
        native = self.find_native(label)
        if native is None:
            raise RuntimeError('적용 전 셰이더를 찾을 수 없습니다.')
        parameters = self.parameters(native['id'])
        return {'label': label, 'entry': deepcopy(snapshot['shaders'][label]), 'url': native['url'], 'values': {k: deepcopy(p['value']) for k, p in parameters.items()}}

    def restore(self, texture_set, previous):
        before = self.snapshot()
        label = previous['label']
        native = self.find_native(label)
        matches = native is not None and native['url'] == previous['url'] and (before['shaders'].get(label) == previous['entry'])
        if matches:
            self.assign(texture_set, label)
            return
        if native is not None:
            label = 'Granit Restore ' + uuid.uuid4().hex
        after = deepcopy(before)
        entry = deepcopy(previous['entry'])
        entry['shaderInstance'] = label
        after['shaders'][label] = entry
        after['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(before, after, texture_set, label)
        try:
            native = self.find_native(label)
            if native is None:
                raise RuntimeError('복원용 Painter 인스턴스를 만들지 못했습니다.')
            self._call('alg.shaders.updateShaderInstance', native['id'], previous['url'])
            self.set_parameters(label, previous['url'], previous['values'])
            before_assign = self.snapshot()
            after_assign = deepcopy(before_assign)
            after_assign['shaders'][label] = entry
            self._write_snapshot(before_assign, after_assign, texture_set, label)
        except Exception as exc:
            self._rollback(before, exc)
