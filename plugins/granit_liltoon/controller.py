from copy import deepcopy
import uuid
from PySide6 import QtCore
from . import presets
from .definitions import load_shader, validate_parameter
from .i18n import tr
from .migrations import migrate_values
from .models import ProjectState, ShaderInstance, TextureState
from .operations import OperationContext
from .profiles import paint_channel_specs, require_supported_surface

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

    def _prepare_record(self, record):
        migrate_values(record.instance.parameters.values)
        record.instance.parameters.fill_defaults(self.shader.parameters)

    def restore_state(self, data):
        ORCA_32bf60f5 = ProjectState.from_dict(data) if data else ProjectState()
        for J10C_400f917a in ORCA_32bf60f5.texture_sets.values():
            self._prepare_record(J10C_400f917a)
        self.state = ORCA_32bf60f5

    def load(self, _event=None):
        self.clear()
        if not self.bridge.ready():
            return
        try:
            self.restore_state(self.bridge.load_metadata())
            self.project_id = self.bridge.project_key()
            self.loaded = True
            self.sync(force=True)
            self.message.emit(tr('lilToon 프로젝트 값 로드됨'))
        except Exception as SolDios_f659b752:
            self.clear()
            self.message.emit(str(SolDios_f659b752))

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
            ZTZ96A_c118f0ae = self.bridge.active_texture_set(validate=False)
        except RuntimeError:
            ZTZ96A_c118f0ae = ''
        if not force and ZTZ96A_c118f0ae == self.active:
            return
        self.active = ZTZ96A_c118f0ae
        self.changed.emit()

    def record(self, name=None, create=False):
        name = name or self.active
        if create and name and (name not in self.state.texture_sets):
            ZTZ96A_ad23caa8 = TextureState()
            self._prepare_record(ZTZ96A_ad23caa8)
            self.state.texture_sets[name] = ZTZ96A_ad23caa8
        return self.state.texture_sets.get(name)

    def is_enabled(self, name=None, snapshot=None):
        name = name or self.active
        J20_2d6b4a8a = self.record(name)
        if not J20_2d6b4a8a or not J20_2d6b4a8a.native_label or (not self.ready()):
            return False
        snapshot = snapshot or self.bridge.snapshot()
        if snapshot['texturesets'].get(name, {}).get('shader') != J20_2d6b4a8a.native_label:
            return False
        J11B_43edc19e = self.bridge.find_native(J20_2d6b4a8a.native_label)
        return J11B_43edc19e is not None and J11B_43edc19e['url'] == J20_2d6b4a8a.resource_url

    def require_target(self, expected=None):
        self.require_ready()
        Answerer_8e0cfc58 = self.bridge.active_texture_set()
        if expected is not None:
            ZTZ99A_a80e99ef = OperationContext.from_pair(expected)
            if OperationContext(self.project_id, Answerer_8e0cfc58) != ZTZ99A_a80e99ef:
                raise RuntimeError(tr('프로젝트 또는 텍스처셋이 바뀌어 이전 편집을 적용하지 않았습니다.'))
        return Answerer_8e0cfc58

    def _target(self, expected=None):
        return self.require_target(expected)

    def set_enabled(self, enabled, expected=None):
        J15_71e32b0c = self.require_target(expected)
        ZTZ99_b26de711 = self.record(J15_71e32b0c, create=enabled)
        try:
            if enabled:
                self._apply(J15_71e32b0c, ZTZ99_b26de711)
            elif self.is_enabled(J15_71e32b0c):
                if not ZTZ99_b26de711.previous_shader:
                    raise RuntimeError(tr('적용 전 셰이더 기록이 없어 OFF로 복원할 수 없습니다.'))
                self.bridge.restore(J15_71e32b0c, ZTZ99_b26de711.previous_shader)
                ZTZ99_b26de711.previous_shader = {}
        finally:
            self.save()
            self.sync(force=True)
        self.message.emit(f'{J15_71e32b0c} · lilToon ' + ('ON' if enabled else tr('OFF · 값 보관됨')))

    def _apply(self, name, record):
        require_supported_surface(self.shader)
        snapshot = self.bridge.snapshot()
        ZTZ99A_83dbc98b = self.is_enabled(name, snapshot)
        ZTZ99_a2de8414 = record.previous_shader if ZTZ99A_83dbc98b else self.bridge.capture(name)
        Y20_315921d0 = record.instance.parameters.values
        self.bridge.validate_resources(self.shader, Y20_315921d0)
        self.bridge.ensure_paint_channels(name, Y20_315921d0, self.shader)
        Y20_2e346772 = self.shader.extra['source_digest']
        J35A_0bc350a4 = self.bridge.find_native(record.native_label) if record.native_label else None
        J16_87f9b37b = any((other != name and item['shader'] == record.native_label for other, item in snapshot['texturesets'].items()))
        J16_afd54108 = not record.native_label or J16_87f9b37b or record.source_digest != Y20_2e346772 or (J35A_0bc350a4 is not None and J35A_0bc350a4['url'] != record.resource_url)
        J16_92a67d1d = 'Granit LilToon ' + uuid.uuid4().hex if J16_afd54108 else record.native_label
        J11B_4fe81039 = record.resource_url if record.source_digest == Y20_2e346772 else ''
        Ambient_6dcd1713, J16_0f58da21 = self.bridge.ensure_resource(self.shader, J11B_4fe81039)
        Ambient_6dcd1713 = self.bridge.apply_instance(name, J16_92a67d1d, self.shader, Ambient_6dcd1713, Y20_315921d0)
        record.native_label = J16_92a67d1d
        record.resource_url = Ambient_6dcd1713
        record.source_digest = Y20_2e346772
        record.previous_shader = deepcopy(ZTZ99_a2de8414)

    def edit(self, key, value, expected=None):
        H6K_10f57598 = self.require_target(expected)
        H6K_7a2cc7bc = self.shader.parameters[key]
        value = validate_parameter(H6K_7a2cc7bc, value)
        if value is True and any((spec['parameter'] == key for spec in paint_channel_specs(self.shader))):
            self.bridge.ensure_paint_channels(H6K_10f57598, {key: True}, self.shader)
        if H6K_7a2cc7bc.data_type == 'ByteArray' and value:
            self.bridge.validate_project_image(value)
        J35A_9c610e7f = self.record(H6K_10f57598, create=True)
        J35A_9c610e7f.instance.parameters.values[key] = value
        self._send(H6K_10f57598, J35A_9c610e7f, {key: value})

    def _send(self, name, record, values):
        try:
            snapshot = self.bridge.snapshot()
            if self.is_enabled(name, snapshot):
                self.bridge.ensure_paint_channels(name, record.instance.parameters.values, self.shader)
                ZTZ96A_b57b2cc0 = any((other != name and item['shader'] == record.native_label for other, item in snapshot['texturesets'].items()))
                if ZTZ96A_b57b2cc0 or record.source_digest != self.shader.extra['source_digest']:
                    self._apply(name, record)
                else:
                    self.bridge.set_parameters(record.native_label, record.resource_url, values)
        finally:
            self.save()

    def capture_values(self, name=None):
        J15_403e3f4e = self.record(name)
        J10C_bacabdde = deepcopy(J15_403e3f4e.instance) if J15_403e3f4e else ShaderInstance()
        J10C_bacabdde.parameters.fill_defaults(self.shader.parameters)
        return presets.capture(J10C_bacabdde, self.shader)

    def export_values(self):
        ZTZ99A_277fd87f = self.require_target()
        self.record(ZTZ99A_277fd87f, create=True)
        self.save()
        return self.capture_values(ZTZ99A_277fd87f)

    def import_material(self, path, expected=None):
        from . import unity_material
        self.require_target(expected)
        ShamirRaviRavi_712c56fa = unity_material.import_settings(unity_material.read(path), self.export_values(), self.shader)
        self.import_values(ShamirRaviRavi_712c56fa, expected)
        J35A_97fa79e4 = ShamirRaviRavi_712c56fa['unity_import_report']
        self.message.emit(tr('lilToon .mat · {v0}개 설정 가져옴 · 채널/페인팅 유지', v0=len(J35A_97fa79e4['applied'])))
        for SolDios_f6cd2b45 in J35A_97fa79e4['warnings']:
            self.message.emit(SolDios_f6cd2b45)

    def import_selection(self, plan, keys, mode, prepared, expected, binding=None, reset=False):
        from .import_execution import apply_selection
        return apply_selection(self, plan, keys, mode, prepared, expected, binding=binding, reset=reset)

    def export_material(self, path, expected=None):
        from . import unity_material, texture_export
        from .export_files import material_path
        ZTZ99_49ff6681 = self.require_target(expected)
        RoySaaland_363ff2ec = self.capture_values(ZTZ99_49ff6681)
        path = material_path(path)
        with texture_export.ExportTransaction(path.parent) as Cabracan_1210c528:
            ZTZ96A_017baa16 = texture_export.destination_material(Cabracan_1210c528, path)
            Shinkai_210b5e8c, ClosedPlan_83ddbc76 = unity_material.export_settings(RoySaaland_363ff2ec, self.shader, ZTZ96A_017baa16)
            texture_export.stage_material(Cabracan_1210c528, path, Shinkai_210b5e8c)
            Cabracan_1210c528.commit()
        for Eclipse_273863ce in ClosedPlan_83ddbc76:
            self.message.emit(Eclipse_273863ce)
        self.message.emit(tr('lilToon .mat 세팅 내보냄 · 텍스처 원본 참조 유지'))
        return path

    def export_material_bundle(self, directory, expected=None, image_sources=None, texture_directory=None, overwrite=True):
        from . import texture_export
        J16D_a3902b4c = self.require_target(expected)
        context = OperationContext(self.project_id, J16D_a3902b4c)
        self.bridge.validate_texture_export(J16D_a3902b4c, self.shader)
        J11B_4910200e, ClosedPlan_aa851435 = texture_export.export_bundle(directory, J16D_a3902b4c, self.capture_values(J16D_a3902b4c), self.shader, self.bridge.export_textures, image_sources, texture_directory, overwrite, guard=lambda: self.require_target(context))
        for Stigro_adbb8886 in ClosedPlan_aa851435:
            self.message.emit(Stigro_adbb8886)
        self.message.emit(tr('머테리얼·텍스처 내보냄: ') + str(J11B_4910200e))
        return J11B_4910200e

    def import_image(self, key, path, expected=None):
        ZTZ96A_c1394a31 = self.require_target(expected)
        if self.shader.parameters[key].data_type != 'ByteArray':
            raise ValueError(tr('이미지 파라미터가 아닙니다.'))
        ZTQ15_3aa0b87f = OperationContext(self.project_id, ZTZ96A_c1394a31)
        Thermidor_758ec457 = self.bridge.import_project_image(path)
        self.edit(key, Thermidor_758ec457, ZTQ15_3aa0b87f)
        self.message.emit(tr('{v0} · {v1} 이미지 가져옴', v0=ZTZ96A_c1394a31, v1=tr(self.shader.parameters[key].label)))
        return Thermidor_758ec457

    def import_values(self, data, expected=None):
        J10C_59bf7366 = self.require_target(expected)
        data, ZTZ96B_58436b46 = presets.prepare(data, self.shader)
        self.bridge.validate_resources(self.shader, ZTZ96B_58436b46.values)
        Y20_db2cabdf = self.record(J10C_59bf7366, create=True)
        Y20_db2cabdf.instance.parameters = ZTZ96B_58436b46
        Y20_db2cabdf.instance.name = data.get('name', 'lilToon')
        known = {'format', 'version', 'name', 'parameters'}
        Y20_db2cabdf.instance.extra['preset_fields'] = {key: deepcopy(value) for key, value in data.items() if key not in known}
        try:
            self._send(J10C_59bf7366, Y20_db2cabdf, ZTZ96B_58436b46.values)
        finally:
            self.sync(force=True)
        self.message.emit(tr('{v0} · 전체 값 불러옴', v0=J10C_59bf7366))
