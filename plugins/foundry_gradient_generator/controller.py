from copy import deepcopy
import hashlib
import json
import math
import time
from PySide6 import QtCore
from .definitions import load_shader, from_painter, validate_parameter
from .gradient import Gradient
from .jobs import GenerationJob
from .models import ProjectState, GranitShaderInstance, PainterBinding, TextureSetBinding

def gradient_signature(gradient):
    if gradient is None:
        return ''
    return hashlib.sha256(json.dumps(gradient.to_dict(), sort_keys=True).encode()).hexdigest()

class ShaderController(QtCore.QObject):
    GRADIENT_DELAY_MS = 250
    changed = QtCore.Signal()
    selectionChanged = QtCore.Signal(str)
    message = QtCore.Signal(str)

    def __init__(self, bridge, parent=None, source_root=None):
        super().__init__(parent)
        self.bridge = bridge
        self.state = ProjectState()
        self.texture_sets = {}
        self._active_texture_set = ''
        self.project = ''
        self.loaded = False
        self._closed = False
        self._pending = set()
        self._gradient_due = {}
        self._parameters_pending = set()
        self._active = None
        self._epoch = 0
        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self._timer.setInterval(self.GRADIENT_DELAY_MS)
        self._timer.timeout.connect(lambda: self.flush(force=False))
        self.job = GenerationJob(bridge.assets, self, source_root=source_root)
        self.job.accept_result = self._accept_result
        self.job.finished.connect(self._ramp_ready)
        self.job.failed.connect(self._ramp_failed)
        self.job.discarded.connect(self._ramp_discarded)

    @property
    def current(self):
        return self.state.instances.get(self.state.selected)

    def require_ready(self):
        if not self.loaded or not self.bridge.ready() or self.bridge.project_key() != self.project:
            raise RuntimeError('편집 가능한 Painter 프로젝트를 먼저 여세요.')

    def save(self):
        self.require_ready()
        self.state.extra['resource_context'] = self.bridge.assets.project_key()
        self.bridge.save_metadata(self.state.to_dict())

    def load_project(self, _event=None):
        if self._closed or not self.bridge.ready():
            return
        key = self.bridge.project_key()
        if self.loaded and key == self.project:
            self.refresh()
            if self._adopt_existing():
                self.save()
                self.changed.emit()
                self.selectionChanged.emit(self.state.selected)
            self._resume_pending()
            self.sync_active_texture_set(force=True)
            return
        self.clear_project()
        try:
            data = self.bridge.load_metadata()
            self.state = ProjectState.from_dict(data) if data is not None else ProjectState()
            if set(self.state.instances) != set(self.state.painter_bindings):
                raise ValueError('일부 플러그인 인스턴스의 Painter 연결 기록이 없습니다. 저장 데이터를 덮어쓰지 않았습니다.')
            definition = load_shader()
            self.state.shaders.setdefault(definition.key, definition)
            self.project, self.loaded = (key, True)
            self.refresh()
            self._adopt_existing()
            self.save()
            self._resume_pending()
            self.sync_active_texture_set(force=True)
            self.message.emit('프로젝트 셰이더 목록 로드됨')
        except Exception as exc:
            self.loaded = False
            self.message.emit(str(exc))
            self.changed.emit()

    def _adopt_existing(self):
        definition = load_shader()
        labels = {b.native_label for b in self.state.painter_bindings.values()}
        labels.update(self.state.extra.get('ignored_native_labels', []))
        added = False
        for native in self.bridge.instances():
            if native['label'] in labels:
                continue
            if native['shader'] != definition.source_file.rsplit('.', 1)[0] and (not native['shader'].startswith('Granit_Ramp_')):
                continue
            imported_definition = deepcopy(definition)
            imported_definition.key = 'granit.native@' + hashlib.sha256(native['url'].encode()).hexdigest()[:16]
            imported_definition.parameters = {}
            imported_definition.extra['resource_url'] = native['url']
            self.state.shaders[imported_definition.key] = imported_definition
            instance = GranitShaderInstance.create(imported_definition, native['label'])
            instance.gradient = None
            self.state.instances[instance.key] = instance
            self.state.painter_bindings[instance.key] = PainterBinding(instance.key, native['label'], native['url'])
            self._read_parameters(instance)
            self.state.painter_bindings[instance.key].applied_revision = instance.revision
            self.message.emit(f'{instance.name} 감지됨 · 기존 램프 유지, 원본 그라디언트는 JSON으로 불러올 수 있습니다.')
            added = True
        return added

    def _resume_pending(self):
        for instance in self.state.instances.values():
            binding = self.state.painter_bindings.get(instance.key)
            if binding and binding.applied_revision < instance.revision:
                self._parameters_pending.add(instance.key)
                self._queue_gradient(instance.key)
        if self._parameters_pending:
            self.flush(force=False)

    def clear_project(self, _event=None):
        self._epoch += 1
        self._timer.stop()
        self.job.invalidate_project()
        self._pending.clear()
        self._gradient_due.clear()
        self._parameters_pending.clear()
        self._active = None
        self.state, self.texture_sets = (ProjectState(), {})
        self._active_texture_set = ''
        self.project, self.loaded = ('', False)
        self.changed.emit()
        self.selectionChanged.emit('')

    def refresh(self):
        self.require_ready()
        self.texture_sets = deepcopy(self.bridge.snapshot()['texturesets'])
        self.changed.emit()

    def sync_active_texture_set(self, _event=None, *, force=False):
        if self._closed or not self.loaded or (not self.bridge.ready()):
            return
        try:
            name = self.bridge.active_texture_set(validate=False)
        except RuntimeError:
            name = ''
        if not force and name == self._active_texture_set:
            return
        try:
            self.require_ready()
            self.texture_sets = deepcopy(self.bridge.snapshot()['texturesets'])
            self._active_texture_set = name
            label = self.texture_sets.get(name, {}).get('shader')
            key = next((key for key, b in self.state.painter_bindings.items() if b.native_label == label), '')
            self.select(key)
            self.changed.emit()
        except Exception as exc:
            self.message.emit(str(exc))

    def _read_parameters(self, instance):
        binding = self.state.painter_bindings[instance.key]
        native = self.bridge.find_native(binding.native_label)
        if native is None:
            raise RuntimeError('Painter 셰이더 인스턴스가 없습니다.')
        shader = self.state.shaders[instance.shader_key]
        for identifier, item in self.bridge.parameters(native['id']).items():
            definition = from_painter(identifier, item['description'], item['value'])
            previous = shader.parameters.get(identifier)
            if not definition.extra['default_known'] and previous and ('default' in previous.properties):
                definition.default = deepcopy(previous.properties['default'])
                definition.extra['default_known'] = True
            shader.parameters[identifier] = definition
            instance.parameters.values[identifier] = deepcopy(item['value'])
        binding.ramp_url = instance.parameters.values.get(shader.ramp_parameter, '')

    def add(self, source_key=None, *, apply_to_active=False):
        self.require_ready()
        texture_set = self.bridge.active_texture_set() if apply_to_active else None
        shader = load_shader()
        if source_key:
            source = self.state.instances[source_key]
            shader = self.state.shaders[source.shader_key]
            instance = source.duplicate(self.unique_name(source.name + ' 복사'))
        else:
            instance = GranitShaderInstance.create(shader, self.unique_name('셰이더'))
        self.state.shaders[shader.key] = shader
        binding = PainterBinding(instance.key, 'Granit ' + instance.key)
        if source_key:
            source_binding = self.state.painter_bindings[source_key]
            binding.resource_url = source_binding.resource_url
            binding.ramp_url = source_binding.ramp_url
        self.state.instances[instance.key] = instance
        self.state.painter_bindings[instance.key] = binding
        self.state.selected = instance.key
        self.save()
        self.changed.emit()
        self.selectionChanged.emit(instance.key)
        try:
            binding.resource_url, _name = self.bridge.ensure_resource(shader, binding.resource_url)
            self.save()
            self.message.emit(f'{instance.name} 추가됨 · 리소스 준비 완료' + ('' if texture_set is not None else ', 목록에서 선택하면 적용됩니다.'))
        except Exception as exc:
            self.message.emit(f'{instance.name} 목록에 보관됨 · 리소스 임포트 실패: {exc} · 적용 시 재시도합니다.')
            return instance.key
        if texture_set is not None:
            try:
                self.apply(texture_set, instance.key)
            except Exception as exc:
                self.message.emit(f'{instance.name} 목록에 보관됨 · {texture_set} 자동 적용 실패: {exc}')
        return instance.key

    def unique_name(self, prefix):
        names = {s.name for s in self.state.instances.values()}
        i = 1
        while f'{prefix}{i}' in names:
            i += 1
        return f'{prefix}{i}'

    def select(self, key):
        if key and key not in self.state.instances:
            return
        self.state.selected = key
        if self.loaded:
            self.save()
        self.selectionChanged.emit(key)

    def choose(self, key, texture_set=None):
        self.require_ready()
        name = texture_set if texture_set is not None else self.bridge.active_texture_set()
        if key:
            self.apply(name, key)
        else:
            current = self.bridge.snapshot()['texturesets'].get(name)
            if current is None:
                raise RuntimeError('텍스처셋이 더 이상 존재하지 않습니다.')
            target = self.state.texture_bindings.get(name)
            binding = self.state.painter_bindings.get(target.instance_key) if target else None
            if binding and current['shader'] == binding.native_label:
                self.revert(name)
            elif any((b.native_label == current['shader'] for b in self.state.painter_bindings.values())):
                raise RuntimeError('이 텍스처셋에는 GrAnit 적용 전 셰이더 기록이 없어 복원할 수 없습니다.')
        self.sync_active_texture_set(force=True)

    def rename(self, key, name):
        self.require_ready()
        name = name.strip()
        if not name or len(name) > 128:
            raise ValueError('셰이더 이름은 1~128자로 입력하세요.')
        self.state.instances[key].name = name
        self.save()
        self.changed.emit()

    def edit_parameter(self, key, identifier, value):
        self.require_ready()
        instance = self.state.instances[key]
        definition = self.state.shaders[instance.shader_key].parameters[identifier]
        value = validate_parameter(definition, value)
        if instance.parameters.values.get(identifier) == value:
            return
        instance.parameters.values[identifier] = value
        instance.revision += 1
        values = None if key in self._parameters_pending else {identifier: value}
        self._parameters_pending.add(key)
        try:
            self._apply_parameters(instance, values)
        except Exception as exc:
            self.message.emit(f'{instance.name}: {exc}')
        self.save()

    def edit_gradient(self, key, gradient):
        self.require_ready()
        instance = self.state.instances[key]
        if instance.gradient == gradient:
            return
        instance.gradient = Gradient.from_dict(gradient.to_dict())
        self._schedule(instance)

    def _schedule(self, instance):
        instance.revision += 1
        self._queue_gradient(instance.key)

    def _queue_gradient(self, key):
        self._pending.add(key)
        self._gradient_due[key] = time.monotonic() + self.GRADIENT_DELAY_MS / 1000
        self._arm_timer()

    def _arm_timer(self):
        self._timer.stop()
        if not self._pending or self._closed or (not self.loaded) or self.job.busy:
            return
        remaining = min((self._gradient_due.get(key, 0) for key in self._pending)) - time.monotonic()
        self._timer.start(max(1, math.ceil(remaining * 1000)))

    def _mark_applied(self, instance):
        binding = self.state.painter_bindings[instance.key]
        signature = gradient_signature(instance.gradient)
        if instance.key not in self._parameters_pending and (not signature or signature == binding.extra.get('ramp_signature')):
            binding.applied_revision = instance.revision

    def _apply_parameters(self, instance, values=None):
        binding = self.state.painter_bindings[instance.key]
        if self.bridge.find_native(binding.native_label) is None:
            self._parameters_pending.discard(instance.key)
            return
        if values is None:
            shader = self.state.shaders[instance.shader_key]
            values = deepcopy(instance.parameters.values)
            if binding.ramp_url:
                values[shader.ramp_parameter] = binding.ramp_url
            else:
                values.pop(shader.ramp_parameter, None)
        self.bridge.set_parameters(binding.native_label, binding.resource_url, values)
        self._parameters_pending.discard(instance.key)
        self._mark_applied(instance)

    def flush(self, _event=None, *, force=True):
        self._timer.stop()
        if not self.loaded or self._closed:
            return
        if not self.bridge.ready():
            if self._pending or self._parameters_pending:
                self._timer.start(self.GRADIENT_DELAY_MS)
            return
        try:
            self.save()
        except Exception as exc:
            self.message.emit(str(exc))
            return
        for key in list(self._parameters_pending):
            if key not in self.state.instances:
                self._parameters_pending.discard(key)
                continue
            try:
                self._apply_parameters(self.state.instances[key])
                self.save()
            except Exception as exc:
                self.message.emit(f'{self.state.instances[key].name}: {exc}')
        if self.job.busy:
            return
        for key in list(self._pending):
            if not force and self._gradient_due.get(key, 0) > time.monotonic():
                continue
            self._pending.discard(key)
            self._gradient_due.pop(key, None)
            if key not in self.state.instances:
                continue
            instance = self.state.instances[key]
            binding = self.state.painter_bindings[key]
            try:
                if self.bridge.find_native(binding.native_label) is None:
                    continue
                signature = gradient_signature(instance.gradient)
                if signature and signature != binding.extra.get('ramp_signature'):
                    self._active = (self._epoch, self.project, key, signature)
                    self.job.start('GranitRamp_' + key, instance.gradient)
                    return
                self._mark_applied(instance)
                self.save()
            except Exception as exc:
                self.message.emit(f'{instance.name}: {exc}')
        self._arm_timer()

    def _accept_result(self):
        if self._active is None or self._closed:
            return False
        epoch, project, key, signature = self._active
        instance = self.state.instances.get(key)
        return self.loaded and epoch == self._epoch and (project == self.project) and (instance is not None) and (gradient_signature(instance.gradient) == signature)

    def _ramp_ready(self, result):
        try:
            if not self._accept_result():
                return
            _epoch, _project, key, signature = self._active
            instance = self.state.instances[key]
            shader = self.state.shaders[instance.shader_key]
            binding = self.state.painter_bindings[key]
            self.bridge.set_parameters(binding.native_label, binding.resource_url, {shader.ramp_parameter: result.url})
            binding.ramp_url = result.url
            binding.extra['ramp_signature'] = signature
            instance.parameters.values[shader.ramp_parameter] = result.url
            self._mark_applied(instance)
            self.save()
            self.message.emit(f'{instance.name} 램프 적용됨')
        except Exception as exc:
            self.message.emit(str(exc))
        finally:
            self._active = None
            self._arm_timer()

    def _ramp_failed(self, error):
        if self._active and self.loaded and (not self.bridge.ready()):
            key = self._active[2]
            if key in self.state.instances:
                self._queue_gradient(key)
        self._active = None
        if self.loaded:
            self.message.emit(error)
        self._arm_timer()

    def _ramp_discarded(self):
        self._active = None
        self._arm_timer()

    def apply(self, texture_set, key):
        self.require_ready()
        instance = self.state.instances[key]
        binding = self.state.painter_bindings[key]
        shader = self.state.shaders[instance.shader_key]
        native = self.bridge.find_native(binding.native_label)
        if native is not None and native['url'] != binding.resource_url:
            raise RuntimeError('Painter의 셰이더 연결이 변경되어 적용하지 않았습니다.')
        current = self.bridge.snapshot()['texturesets'][texture_set]['shader']
        previous_binding = self.state.texture_bindings.get(texture_set)
        previous_native = self.state.painter_bindings.get(previous_binding.instance_key) if previous_binding else None
        if current == binding.native_label:
            return
        if previous_binding and previous_native and (current == previous_native.native_label):
            previous = deepcopy(previous_binding.previous_shader)
        else:
            previous = self.bridge.capture(texture_set)
        target = TextureSetBinding(texture_set, key, previous)
        self.state.texture_bindings[texture_set] = target
        values = deepcopy(instance.parameters.values)
        ramp_url = binding.ramp_url
        if native is None and instance.gradient is not None:
            ramp_url = ''
        if ramp_url:
            values[shader.ramp_parameter] = ramp_url
        else:
            values.pop(shader.ramp_parameter, None)
        try:
            self.save()
            binding.resource_url = self.bridge.apply_instance(texture_set, binding.native_label, shader, binding.resource_url, values)
        except Exception:
            if previous_binding:
                self.state.texture_bindings[texture_set] = previous_binding
            else:
                self.state.texture_bindings.pop(texture_set, None)
            self.save()
            raise
        self._read_parameters(instance)
        instance.parameters.values.update(values)
        binding.ramp_url = ramp_url
        if native is None and instance.gradient is not None:
            binding.extra.pop('ramp_signature', None)
            instance.parameters.values.pop(shader.ramp_parameter, None)
        binding.applied_revision = -1
        self._parameters_pending.discard(key)
        self.save()
        self._queue_gradient(key)
        self.refresh()
        if self.state.selected == key:
            self.selectionChanged.emit(key)
        self.message.emit(f'{texture_set} → {instance.name}')

    def revert(self, texture_set):
        self.require_ready()
        target = self.state.texture_bindings[texture_set]
        binding = self.state.painter_bindings[target.instance_key]
        current = self.bridge.snapshot()['texturesets'][texture_set]['shader']
        if current != binding.native_label:
            raise RuntimeError('Painter에서 연결이 변경되어 이전 Revert를 적용하지 않았습니다. 새로고침하세요.')
        self.bridge.restore(texture_set, target.previous_shader)
        del self.state.texture_bindings[texture_set]
        self.save()
        self.refresh()
        self.message.emit(f'{texture_set} 이전 셰이더로 복원됨')

    def remove(self, key):
        self.require_ready()
        label = self.state.painter_bindings[key].native_label
        self.texture_sets = deepcopy(self.bridge.snapshot()['texturesets'])
        linked = [name for name, item in self.texture_sets.items() if item['shader'] == label]
        if linked:
            self.changed.emit()
            raise RuntimeError('사용 중인 셰이더는 삭제할 수 없습니다: ' + ', '.join(linked) + ' · 모든 연결을 바꾸거나 되돌린 뒤 삭제하세요.')
        name = self.state.instances[key].name
        self.state.extra.setdefault('ignored_native_labels', []).append(label)
        del self.state.instances[key]
        del self.state.painter_bindings[key]
        for texture_set, target in list(self.state.texture_bindings.items()):
            if target.instance_key == key:
                del self.state.texture_bindings[texture_set]
        self._pending.discard(key)
        self._gradient_due.pop(key, None)
        self._parameters_pending.discard(key)
        self.state.selected = ''
        self.save()
        self.sync_active_texture_set(force=True)
        self.message.emit(f'{name} 목록에서 삭제됨 · 미사용 Painter 인스턴스/에셋은 보존됩니다.')

    def shutdown(self):
        if self._closed:
            return
        if self.loaded and self.bridge.ready():
            try:
                self.save()
            except Exception as exc:
                self.message.emit(str(exc))
        self._closed = True
        self._timer.stop()
        self.job.close()
