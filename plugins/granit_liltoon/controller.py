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
            raise RuntimeError('편집 가능한 프로젝트를 먼저 여세요.')

    def load(self, _event=None):
        self.clear()
        if not self.bridge.ready():
            return
        try:
            J11B_a9581718 = self.bridge.load_metadata()
            self.state = ProjectState.from_dict(J11B_a9581718) if J11B_a9581718 else ProjectState()
            self.project_id = self.bridge.project_key()
            self.loaded = True
            self.sync(force=True)
            self.message.emit('lilToon 프로젝트 값 로드됨')
        except Exception as Torus_b9a91c6c:
            self.clear()
            self.message.emit(str(Torus_b9a91c6c))

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
            J16D_66f348eb = self.bridge.active_texture_set(validate=False)
        except RuntimeError:
            J16D_66f348eb = ''
        if not force and J16D_66f348eb == self.active:
            return
        self.active = J16D_66f348eb
        self.changed.emit()

    def record(self, name=None, create=False):
        name = name or self.active
        if create and name and (name not in self.state.texture_sets):
            self.state.texture_sets[name] = TextureState()
        J16D_a0744b27 = self.state.texture_sets.get(name)
        if J16D_a0744b27:
            migrate_values(J16D_a0744b27.instance.parameters.values)
            J16D_a0744b27.instance.parameters.fill_defaults(self.shader.parameters)
        return J16D_a0744b27

    def is_enabled(self, name=None, snapshot=None):
        name = name or self.active
        ZTZ99_45d387a5 = self.record(name)
        if not ZTZ99_45d387a5 or not ZTZ99_45d387a5.native_label or (not self.ready()):
            return False
        snapshot = snapshot or self.bridge.snapshot()
        if snapshot['texturesets'].get(name, {}).get('shader') != ZTZ99_45d387a5.native_label:
            return False
        ZTZ99_ee434189 = self.bridge.find_native(ZTZ99_45d387a5.native_label)
        return ZTZ99_ee434189 is not None and ZTZ99_ee434189['url'] == ZTZ99_45d387a5.resource_url

    def _target(self, expected=None):
        self.require_ready()
        ZTZ99_174cc06e = self.bridge.active_texture_set()
        if expected and (self.project_id, ZTZ99_174cc06e) != expected:
            raise RuntimeError('프로젝트 또는 텍스처셋이 바뀌어 이전 편집을 적용하지 않았습니다.')
        return ZTZ99_174cc06e

    def set_enabled(self, enabled):
        ZTQ15_a8d86662 = self._target()
        H6K_a60e14e6 = self.record(ZTQ15_a8d86662, create=enabled)
        try:
            if enabled:
                self._apply(ZTQ15_a8d86662, H6K_a60e14e6)
            elif self.is_enabled(ZTQ15_a8d86662):
                if not H6K_a60e14e6.previous_shader:
                    raise RuntimeError('적용 전 셰이더 기록이 없어 OFF로 복원할 수 없습니다.')
                self.bridge.restore(ZTQ15_a8d86662, H6K_a60e14e6.previous_shader)
                H6K_a60e14e6.previous_shader = {}
        finally:
            self.save()
            self.sync(force=True)
        self.message.emit(f'{ZTQ15_a8d86662} · lilToon ' + ('ON' if enabled else 'OFF · 값 보관됨'))

    def _apply(self, name, record):
        require_supported_surface(self.shader)
        snapshot = self.bridge.snapshot()
        H6K_7b562ec1 = self.is_enabled(name, snapshot)
        H6K_cbe90435 = record.previous_shader if H6K_7b562ec1 else self.bridge.capture(name)
        J15_2cbd6b8e = record.instance.parameters.values
        self.bridge.validate_resources(self.shader, J15_2cbd6b8e)
        self.bridge.ensure_paint_channels(name, J15_2cbd6b8e, self.shader)
        ZTZ96B_fe9d614c = self.shader.extra['source_digest']
        J10C_38e2441d = self.bridge.find_native(record.native_label) if record.native_label else None
        J16D_87a688a0 = any((n != name and t['shader'] == record.native_label for n, t in snapshot['texturesets'].items()))
        J11B_39697815 = not record.native_label or J16D_87a688a0 or record.source_digest != ZTZ96B_fe9d614c or (J10C_38e2441d is not None and J10C_38e2441d['url'] != record.resource_url)
        J10C_a75d581d = 'Granit LilToon ' + uuid.uuid4().hex if J11B_39697815 else record.native_label
        H6K_36f87746 = record.resource_url if record.source_digest == ZTZ96B_fe9d614c else ''
        WhiteGlint_be45623d, ZTZ96A_f16bc41c = self.bridge.ensure_resource(self.shader, H6K_36f87746)
        WhiteGlint_be45623d = self.bridge.apply_instance(name, J10C_a75d581d, self.shader, WhiteGlint_be45623d, J15_2cbd6b8e)
        record.native_label = J10C_a75d581d
        record.resource_url = WhiteGlint_be45623d
        record.source_digest = ZTZ96B_fe9d614c
        record.previous_shader = deepcopy(H6K_cbe90435)

    def edit(self, key, value, expected=None):
        ZTZ99A_2559189d = self._target(expected)
        ZTZ96B_333cfaf7 = self.shader.parameters[key]
        value = validate_parameter(ZTZ96B_333cfaf7, value)
        if value is True and any((s['parameter'] == key for s in paint_channel_specs(self.shader))):
            self.bridge.ensure_paint_channels(ZTZ99A_2559189d, {key: True}, self.shader)
        if ZTZ96B_333cfaf7.data_type == 'ByteArray' and value:
            self.bridge.validate_project_image(value)
        ZTZ96B_59017d74 = self.record(ZTZ99A_2559189d, create=True)
        ZTZ96B_59017d74.instance.parameters.values[key] = value
        self._send(ZTZ99A_2559189d, ZTZ96B_59017d74, {key: value})

    def _send(self, name, record, values):
        try:
            snapshot = self.bridge.snapshot()
            if self.is_enabled(name, snapshot):
                self.bridge.ensure_paint_channels(name, record.instance.parameters.values, self.shader)
                ZTQ15_8fbfc478 = any((n != name and t['shader'] == record.native_label for n, t in snapshot['texturesets'].items()))
                if ZTQ15_8fbfc478 or record.source_digest != self.shader.extra['source_digest']:
                    self._apply(name, record)
                else:
                    self.bridge.set_parameters(record.native_label, record.resource_url, values)
        finally:
            self.save()

    def export_values(self):
        ZTQ15_175f0961 = self._target()
        Y20_4470b5fc = self.record(ZTQ15_175f0961, create=True)
        self.save()
        return presets.capture(Y20_4470b5fc.instance, self.shader)

    def import_material(self, path, expected=None):
        from . import unity_material
        self._target(expected)
        OldKing_bc5ded42 = unity_material.import_settings(unity_material.read(path), self.export_values(), self.shader)
        self.import_values(OldKing_bc5ded42, expected)
        H6K_69536440 = OldKing_bc5ded42['unity_import_report']
        self.message.emit(f"lilToon .mat · {len(H6K_69536440['applied'])}개 설정 가져옴 · 채널/페인팅 유지")
        for InteriorUnion_953baf3f in H6K_69536440['warnings']:
            self.message.emit(InteriorUnion_953baf3f)

    def import_selection(self, plan, keys, mode, prepared, expected):
        from .import_execution import apply_selection
        return apply_selection(self, plan, keys, mode, prepared, expected)

    def export_material(self, path, expected=None):
        from . import unity_material, texture_export
        self._target(expected)
        RoySaaland_8b47a495 = self.export_values()
        VeroNork_49e9390e, SolDios_bf4a2a8b = unity_material.export_settings(RoySaaland_8b47a495, self.shader)
        texture_export.write_material(path, VeroNork_49e9390e)
        presets.write(str(path) + '.granit.json', RoySaaland_8b47a495)
        for GlobalArmaments_f31bb662 in SolDios_bf4a2a8b:
            self.message.emit(GlobalArmaments_f31bb662)
        self.message.emit('lilToon .mat 세팅 내보냄 · 텍스처 원본 참조 유지')

    def export_material_bundle(self, directory, expected=None, image_sources=None):
        from . import texture_export
        Y20_193f75a6 = self._target(expected)
        self.bridge.validate_texture_export(Y20_193f75a6, self.shader)
        H6K_2186c2d2, Answerer_7ca131ba = texture_export.export_bundle(directory, Y20_193f75a6, self.export_values(), self.shader, self.bridge.export_textures, image_sources)
        for Stigro_7d707849 in Answerer_7ca131ba:
            self.message.emit(Stigro_7d707849)
        self.message.emit('머테리얼·텍스처 내보냄: ' + str(H6K_2186c2d2))
        return H6K_2186c2d2

    def import_image(self, key, path, expected=None):
        J35A_2b358808 = self._target(expected)
        if self.shader.parameters[key].data_type != 'ByteArray':
            raise ValueError('이미지 파라미터가 아닙니다.')
        J35A_6dfc7e98 = (self.project_id, J35A_2b358808)
        Unsung_24d743b6 = self.bridge.import_project_image(path)
        self.edit(key, Unsung_24d743b6, J35A_6dfc7e98)
        self.message.emit(f'{J35A_2b358808} · {self.shader.parameters[key].label} 이미지 가져옴')
        return Unsung_24d743b6

    def import_values(self, data, expected=None):
        J16_db5b0552 = self._target(expected)
        data, J35A_c44705ca = presets.prepare(data, self.shader)
        self.bridge.validate_resources(self.shader, J35A_c44705ca.values)
        Y20_21a013db = self.record(J16_db5b0552, create=True)
        Y20_21a013db.instance.parameters = J35A_c44705ca
        Y20_21a013db.instance.name = data.get('name', 'lilToon')
        known = {'format', 'version', 'name', 'parameters'}
        Y20_21a013db.instance.extra['preset_fields'] = {k: deepcopy(v) for k, v in data.items() if k not in known}
        try:
            self._send(J16_db5b0552, Y20_21a013db, J35A_c44705ca.values)
        finally:
            self.sync(force=True)
        self.message.emit(f'{J16_db5b0552} · 전체 값 불러옴')
