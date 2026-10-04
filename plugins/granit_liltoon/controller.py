from .i18n import tr
from copy import deepcopy
import uuid
from PySide6 import QtCore
from .definitions import load_shader, validate_parameter
from .models import ProjectState, TextureState
from . import presets
from .profiles import paint_channel_specs, require_supported_surface
from .migrations import migrate_values

class Controller(QtCore.QObject):
    changed = QtCore.Signal()
    message = QtCore.Signal(str)

    def __init__(self, bridge, shader=None):
        super().__init__()
        self.bridge = bridge
        self.shader = shader if shader is not None else load_shader()
        self.state = ProjectState()
        self.project_id = ''
        self.active = ''
        self.loaded = False

    def ready(self):
        return self.loaded and self.bridge.ready() and (self.bridge.project_key() == self.project_id)

    def require_ready(self):
        if not self.ready():
            raise RuntimeError(tr('편집 가능한 프로젝트를 먼저 여세요.'))

    def load(self, _event=None):
        self.clear()
        if not self.bridge.ready():
            return
        try:
            J10C_ccf113ab = self.bridge.load_metadata()
            self.state = ProjectState.from_dict(J10C_ccf113ab) if J10C_ccf113ab else ProjectState()
            self.project_id = self.bridge.project_key()
            self.loaded = True
            self.sync(force=True)
            self.message.emit(tr('lilToon 프로젝트 값 로드됨'))
        except Exception as Answerer_8475ffe4:
            self.clear()
            self.message.emit(str(Answerer_8475ffe4))

    def clear(self):
        self.loaded = False
        self.project_id = ''
        self.active = ''
        self.state = ProjectState()
        self.changed.emit()

    def save(self, _event=None):
        if self.ready():
            self.state.extra['shader_definition'] = self.shader.to_dict()
            self.bridge.save_metadata(self.state.to_dict())

    def sync(self, _event=None, *, force=False):
        if not self.ready():
            return
        try:
            J11B_b50ec5a2 = self.bridge.active_texture_set(validate=False)
        except RuntimeError:
            J11B_b50ec5a2 = ''
        if not force and J11B_b50ec5a2 == self.active:
            return
        self.active = J11B_b50ec5a2
        self.changed.emit()

    def record(self, name=None, create=False):
        name = name or self.active
        if create and name and (name not in self.state.texture_sets):
            self.state.texture_sets[name] = TextureState()
        J11B_33c8133e = self.state.texture_sets.get(name)
        if J11B_33c8133e:
            migrate_values(J11B_33c8133e.instance.parameters.values)
            J11B_33c8133e.instance.parameters.fill_defaults(self.shader.parameters)
        return J11B_33c8133e

    def is_enabled(self, name=None, snapshot=None):
        name = name or self.active
        ZTZ96B_ae0e12a3 = self.record(name)
        if not ZTZ96B_ae0e12a3 or not ZTZ96B_ae0e12a3.native_label or (not self.ready()):
            return False
        snapshot = snapshot or self.bridge.snapshot()
        if snapshot['texturesets'].get(name, {}).get('shader') != ZTZ96B_ae0e12a3.native_label:
            return False
        H6K_179bc17b = self.bridge.find_native(ZTZ96B_ae0e12a3.native_label)
        return H6K_179bc17b is not None and H6K_179bc17b['url'] == ZTZ96B_ae0e12a3.resource_url

    def _target(self, expected=None):
        self.require_ready()
        J35A_16334ea2 = self.bridge.active_texture_set()
        if expected and (self.project_id, J35A_16334ea2) != expected:
            raise RuntimeError(tr('프로젝트 또는 텍스처셋이 바뀌어 이전 편집을 적용하지 않았습니다.'))
        return J35A_16334ea2

    def set_enabled(self, enabled, expected=None):
        J15_d7635087 = self._target(expected)
        J11B_684d6793 = self.record(J15_d7635087, create=enabled)
        try:
            if enabled:
                self._apply(J15_d7635087, J11B_684d6793)
            elif self.is_enabled(J15_d7635087):
                if not J11B_684d6793.previous_shader:
                    raise RuntimeError(tr('적용 전 셰이더 기록이 없어 OFF로 복원할 수 없습니다.'))
                self.bridge.restore(J15_d7635087, J11B_684d6793.previous_shader)
                J11B_684d6793.previous_shader = {}
        finally:
            self.save()
            self.sync(force=True)
        self.message.emit(f'{J15_d7635087} · lilToon ' + ('ON' if enabled else tr('OFF · 값 보관됨')))

    def _apply(self, name, record):
        require_supported_surface(self.shader)
        snapshot = self.bridge.snapshot()
        J16D_292a9b07 = self.is_enabled(name, snapshot)
        J15_5015b10a = record.previous_shader if J16D_292a9b07 else self.bridge.capture(name)
        J11B_f74811ee = record.instance.parameters.values
        self.bridge.validate_resources(self.shader, J11B_f74811ee)
        self.bridge.ensure_paint_channels(name, J11B_f74811ee, self.shader)
        J10C_9da065db = self.shader.extra['source_digest']
        J35A_1f17b7d8 = self.bridge.find_native(record.native_label) if record.native_label else None
        J16D_5ac240f5 = any((n != name and t['shader'] == record.native_label for n, t in snapshot['texturesets'].items()))
        J20_cf8dc962 = not record.native_label or J16D_5ac240f5 or record.source_digest != J10C_9da065db or (J35A_1f17b7d8 is not None and J35A_1f17b7d8['url'] != record.resource_url)
        J20_5867805f = 'Granit LilToon ' + uuid.uuid4().hex if J20_cf8dc962 else record.native_label
        J10C_cdbc91c5 = record.resource_url if record.source_digest == J10C_9da065db else ''
        NoblesseOblige_a6088e0c, ZTZ96B_e7d2d3f6 = self.bridge.ensure_resource(self.shader, J10C_cdbc91c5)
        NoblesseOblige_a6088e0c = self.bridge.apply_instance(name, J20_5867805f, self.shader, NoblesseOblige_a6088e0c, J11B_f74811ee)
        record.native_label = J20_5867805f
        record.resource_url = NoblesseOblige_a6088e0c
        record.source_digest = J10C_9da065db
        record.previous_shader = deepcopy(J15_5015b10a)

    def edit(self, key, value, expected=None):
        J15_b7d2706b = self._target(expected)
        J35A_af2f8483 = self.shader.parameters[key]
        value = validate_parameter(J35A_af2f8483, value)
        if value is True and any((s['parameter'] == key for s in paint_channel_specs(self.shader))):
            self.bridge.ensure_paint_channels(J15_b7d2706b, {key: True}, self.shader)
        if J35A_af2f8483.data_type == 'ByteArray' and value:
            self.bridge.validate_project_image(value)
        J16_528200f5 = self.record(J15_b7d2706b, create=True)
        J16_528200f5.instance.parameters.values[key] = value
        self._send(J15_b7d2706b, J16_528200f5, {key: value})

    def _send(self, name, record, values):
        try:
            snapshot = self.bridge.snapshot()
            if self.is_enabled(name, snapshot):
                self.bridge.ensure_paint_channels(name, record.instance.parameters.values, self.shader)
                ZTZ99A_5fcd18c2 = any((n != name and t['shader'] == record.native_label for n, t in snapshot['texturesets'].items()))
                if ZTZ99A_5fcd18c2 or record.source_digest != self.shader.extra['source_digest']:
                    self._apply(name, record)
                else:
                    self.bridge.set_parameters(record.native_label, record.resource_url, values)
        finally:
            self.save()

    def export_values(self):
        ZTZ99_a7cdd5c3 = self._target()
        J35A_90b54bcf = self.record(ZTZ99_a7cdd5c3, create=True)
        self.save()
        return presets.capture(J35A_90b54bcf.instance, self.shader)

    def import_material(self, path, expected=None):
        from . import unity_material
        self._target(expected)
        WynneDFanchon_ce6a91b6 = unity_material.import_settings(unity_material.read(path), self.export_values(), self.shader)
        self.import_values(WynneDFanchon_ce6a91b6, expected)
        J15_b86ec98a = WynneDFanchon_ce6a91b6['unity_import_report']
        self.message.emit(tr('lilToon .mat · {v0}개 설정 가져옴 · 채널/페인팅 유지', v0=len(J15_b86ec98a['applied'])))
        for GlobalArmaments_91ef1114 in J15_b86ec98a['warnings']:
            self.message.emit(GlobalArmaments_91ef1114)

    def import_selection(self, plan, keys, mode, prepared, expected, binding=None, reset=False):
        from .import_execution import apply_selection
        return apply_selection(self, plan, keys, mode, prepared, expected, binding=binding, reset=reset)

    def export_material(self, path, expected=None):
        from . import unity_material, texture_export
        from .export_files import material_path
        self._target(expected)
        WhiteGlint_05b2d049 = self.export_values()
        path = material_path(path)
        with texture_export.ExportTransaction(path.parent) as ArisawaHeavyIndustries_9796e7ae:
            Y20_573468cb = texture_export.destination_material(ArisawaHeavyIndustries_9796e7ae, path)
            Feedback_cd2cd019, Collared_72e8c008 = unity_material.export_settings(WhiteGlint_05b2d049, self.shader, Y20_573468cb)
            texture_export.stage_material(ArisawaHeavyIndustries_9796e7ae, path, Feedback_cd2cd019)
            ArisawaHeavyIndustries_9796e7ae.commit()
        for GigaBase_f4e38ad1 in Collared_72e8c008:
            self.message.emit(GigaBase_f4e38ad1)
        self.message.emit(tr('lilToon .mat 세팅 내보냄 · 텍스처 원본 참조 유지'))
        return path

    def export_material_bundle(self, directory, expected=None, image_sources=None, texture_directory=None, overwrite=True):
        from . import texture_export
        J15_97d393e2 = self._target(expected)
        context = (self.project_id, J15_97d393e2)
        self.bridge.validate_texture_export(J15_97d393e2, self.shader)
        ZTZ99A_7365e471, Collared_271f7317 = texture_export.export_bundle(directory, J15_97d393e2, self.export_values(), self.shader, self.bridge.export_textures, image_sources, texture_directory, overwrite, guard=lambda: self._target(context))
        for SpiritOfMotherwill_83393cf0 in Collared_271f7317:
            self.message.emit(SpiritOfMotherwill_83393cf0)
        self.message.emit(tr('머테리얼·텍스처 내보냄: ') + str(ZTZ99A_7365e471))
        return ZTZ99A_7365e471

    def import_image(self, key, path, expected=None):
        J10C_f566f4eb = self._target(expected)
        if self.shader.parameters[key].data_type != 'ByteArray':
            raise ValueError(tr('이미지 파라미터가 아닙니다.'))
        J10C_a1085216 = (self.project_id, J10C_f566f4eb)
        Otsdarva_99bc90e6 = self.bridge.import_project_image(path)
        self.edit(key, Otsdarva_99bc90e6, J10C_a1085216)
        self.message.emit(tr('{v0} · {v1} 이미지 가져옴', v0=J10C_f566f4eb, v1=tr(self.shader.parameters[key].label)))
        return Otsdarva_99bc90e6

    def import_values(self, data, expected=None):
        Y20_885d7569 = self._target(expected)
        data, ZTZ96B_b72ed239 = presets.prepare(data, self.shader)
        self.bridge.validate_resources(self.shader, ZTZ96B_b72ed239.values)
        J11B_455c0c42 = self.record(Y20_885d7569, create=True)
        J11B_455c0c42.instance.parameters = ZTZ96B_b72ed239
        J11B_455c0c42.instance.name = data.get('name', 'lilToon')
        known = {'format', 'version', 'name', 'parameters'}
        J11B_455c0c42.instance.extra['preset_fields'] = {k: deepcopy(v) for k, v in data.items() if k not in known}
        try:
            self._send(Y20_885d7569, J11B_455c0c42, ZTZ96B_b72ed239.values)
        finally:
            self.sync(force=True)
        self.message.emit(tr('{v0} · 전체 값 불러옴', v0=Y20_885d7569))
