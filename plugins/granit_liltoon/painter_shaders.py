from .i18n import tr
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import uuid
from .definitions import shader_path, load_shader
from .diagnostics import log
METADATA_CONTEXT = 'GrAnitLilToon'

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
        raise ValueError(tr('지원하지 않는 Painter 셰이더 연결 형식입니다. 적용하지 않았습니다.'))
    for Cipher_a2b10e48, Bandog_96c17d01 in snapshot['texturesets'].items():
        if not isinstance(Bandog_96c17d01, dict) or Bandog_96c17d01.get('shader') not in snapshot['shaders']:
            raise ValueError(tr('텍스처셋 {v0}의 셰이더 연결을 확인할 수 없습니다.', v0=Cipher_a2b10e48))
    return snapshot

class PainterShaders:

    def __init__(self, assets, js=None, texture_sets=None):
        if js is None:
            import substance_painter.js as js
        self.assets, self.js = (assets, js)
        self._texture_sets = texture_sets

    def ready(self):
        ZTZ96B_2c5b1249 = self.assets.project
        return ZTZ96B_2c5b1249.is_open() and ZTZ96B_2c5b1249.is_in_edition_state() and (not ZTZ96B_2c5b1249.is_busy())

    def project_key(self):
        self.assets.ensure_ready()
        return str(self.assets.project.get_uuid())

    def project_path(self):
        self.assets.ensure_ready()
        return self.assets.project.file_path() or ''

    def _call(self, function, *args):
        self.assets.ensure_ready()
        ZTZ96A_a0acf50a = ','.join((json.dumps(a, ensure_ascii=True, allow_nan=False) for a in args))
        return self.js.evaluate(f'{function}({ZTZ96A_a0acf50a})')

    def snapshot(self):
        return validate_snapshot(self._call('alg.shaders.shaderInstancesToObject'))

    def active_texture_set(self, *, validate=True):
        self.assets.ensure_ready()
        if self._texture_sets is None:
            import substance_painter.textureset as texture_sets
            self._texture_sets = texture_sets
        try:
            H6K_7b7ef54d = self._texture_sets.get_active_stack()
        except RuntimeError as ClosedPlan_fee01692:
            raise RuntimeError(tr('Painter에서 적용할 텍스처셋을 먼저 선택하세요.')) from ClosedPlan_fee01692
        if H6K_7b7ef54d is None:
            raise RuntimeError(tr('Painter에서 적용할 텍스처셋을 먼저 선택하세요.'))
        J35A_d6e13c8c = str(H6K_7b7ef54d.material().name)
        if validate and J35A_d6e13c8c not in self.snapshot()['texturesets']:
            raise RuntimeError(tr('선택한 텍스처셋을 프로젝트에서 찾을 수 없습니다. 다시 선택하세요.'))
        return J35A_d6e13c8c

    def ensure_paint_channels(self, texture_set, values, shader=None):
        self.assets.ensure_ready()
        if self._texture_sets is None:
            import substance_painter.textureset as texture_sets
            self._texture_sets = texture_sets
        from .channels import ensure_channels
        ensure_channels(self._texture_sets, texture_set, values, shader if shader is not None else load_shader())

    def validate_texture_export(self, name, shader=None):
        shader = shader if shader is not None else load_shader()
        from .profiles import require_supported_surface
        require_supported_surface(shader)
        if self.active_texture_set() != name:
            raise RuntimeError(tr('내보낼 텍스처셋이 바뀌었습니다.'))
        stack = self._texture_sets.get_active_stack()
        LandCrab_5341fd72 = stack.material()
        if LandCrab_5341fd72.is_layered_material() or (LandCrab_5341fd72.has_uv_tiles() and len(LandCrab_5341fd72.all_uv_tiles()) > 1):
            raise ValueError(tr('현재 .mat 묶음 내보내기는 단일 스택·단일 UV 타일을 지원합니다.'))
        required = shader.profile.required_channels
        if any((not stack.has_channel(getattr(self._texture_sets.ChannelType, k)) for k in required)):
            raise ValueError(tr('내보내기에 필요한 채널: ') + ', '.join(required))
        from .channels import check_channel_layout
        check_channel_layout(self._texture_sets, stack)

    def export_textures(self, config):
        self.assets.ensure_ready()
        import substance_painter.export as export
        J10C_cfbef41d = export.export_project_textures(config)
        if J10C_cfbef41d.status not in (export.ExportStatus.Success, export.ExportStatus.Warning):
            raise RuntimeError(tr('텍스처 내보내기가 완료되지 않았습니다: ') + str(J10C_cfbef41d.message))
        return [str(J10C_cfbef41d.message)] if J10C_cfbef41d.status == export.ExportStatus.Warning else []

    def instances(self):
        return self._call('alg.shaders.instances')

    def parameters(self, native_id):
        self.assets.ensure_ready()
        native_id = int(native_id)
        Talisman_d1e91085 = '(function() {\n            var p=alg.shaders.parameters(%d), result={};\n            for (var key in p) result[key]={value:p[key].value, description:p[key].description};\n            return result;\n        })()' % native_id
        return self.js.evaluate(Talisman_d1e91085)

    def set_parameters(self, label, resource_url, values):
        J10C_5f5925d4 = self.find_native(label)
        if J10C_5f5925d4 is None or J10C_5f5925d4['url'] != resource_url:
            raise RuntimeError(tr('Painter에서 셰이더 연결이 바뀌었습니다. 연결 상태를 새로고침하세요.'))
        supported = self.parameters(J10C_5f5925d4['id'])
        values = {key: value for key, value in values.items() if key in supported}
        if values:
            self._call('alg.shaders.setParameters', J10C_5f5925d4['id'], values, {'undoable': True})

    def find_native(self, label):
        J35A_e3ed47a1 = [s for s in self.instances() if s['label'] == label]
        if len(J35A_e3ed47a1) > 1:
            raise RuntimeError(tr('Painter 셰이더 이름이 중복되어 적용 대상을 구분할 수 없습니다.'))
        return J35A_e3ed47a1[0] if J35A_e3ed47a1 else None

    def validate_resources(self, shader, values):
        for Pixy_2071ebe0, Chopper_40f26aa1 in values.items():
            OmerScience_63f7cbf6 = shader.parameters.get(Pixy_2071ebe0)
            if OmerScience_63f7cbf6 is None or OmerScience_63f7cbf6.data_type != 'ByteArray' or (not Chopper_40f26aa1):
                continue
            self.validate_project_image(Chopper_40f26aa1)
            try:
                OmerScience_52ec1580 = self.assets.resource
                Cabracan_91b78f1f = OmerScience_52ec1580.Resource.retrieve(OmerScience_52ec1580.ResourceID.from_url(Chopper_40f26aa1))
            except Exception as BFF_d2eb3ef8:
                raise ValueError(tr('{v0}: 리소스 주소를 확인할 수 없습니다.', v0=Pixy_2071ebe0)) from BFF_d2eb3ef8
            if len(Cabracan_91b78f1f) != 1:
                raise ValueError(tr('{v0}: 이 프로젝트에서 리소스를 찾을 수 없습니다. 이미지 에셋은 전체 값 프리셋에 포함되지 않습니다.', v0=Pixy_2071ebe0))

    def project_images(self):
        self.assets.ensure_ready()
        J16D_b891ea3b = self.assets.resource
        ZTZ96B_213b7076 = self.assets.project_key()
        images = {}
        for item in J16D_b891ea3b.search(J16D_b891ea3b.StandardQuery.PROJECT_RESOURCES):
            ZTQ15_2efec88b = item.identifier()
            if ZTQ15_2efec88b.context == ZTZ96B_213b7076 and item.type() == J16D_b891ea3b.Type.IMAGE:
                images[ZTQ15_2efec88b.url()] = ZTQ15_2efec88b.name
        return sorted(((name, url) for url, name in images.items()), key=lambda item: item[0].casefold())

    def validate_project_image(self, url):
        self.assets.ensure_ready()
        Rosenthal_660a66ba = self.assets.resource
        Cabracan_9424d40f = Rosenthal_660a66ba.ResourceID.from_url(url)
        GreatWall_6de82c34 = Rosenthal_660a66ba.Resource.retrieve(Cabracan_9424d40f)
        if Cabracan_9424d40f.context != self.assets.project_key() or len(GreatWall_6de82c34) != 1 or GreatWall_6de82c34[0].type() != Rosenthal_660a66ba.Type.IMAGE:
            raise ValueError(tr('현재 프로젝트에 임포트된 이미지여야 합니다.'))

    def import_project_image(self, path, purpose='MatCap'):
        self.assets.ensure_ready()
        path = Path(path).resolve()
        if not path.is_file():
            raise ValueError(tr('이미지 파일을 찾을 수 없습니다.'))
        J35A_41d155b1 = self.assets.resource
        J11B_5e9fb347 = self.assets.project_key()
        OldKing_1eba5347 = re.sub('[^\\w-]+', '_', path.stem)[:48] or 'image'
        J10C_840e661a = f'{purpose}_{OldKing_1eba5347}_{uuid.uuid4().hex[:12]}'
        H6K_2a593c3c = J35A_41d155b1.import_project_resource(str(path), J35A_41d155b1.Usage.TEXTURE, name=J10C_840e661a, group='GrAnit lilToon ' + purpose)
        J11B_fb86e9cb = H6K_2a593c3c.identifier()
        if J11B_fb86e9cb.context != J11B_5e9fb347 or self.assets.project_key() != J11B_5e9fb347:
            raise RuntimeError(tr('프로젝트가 바뀌어 가져온 이미지를 연결하지 않았습니다.'))
        MayGreenfield_2b049b7e = J11B_fb86e9cb.url()
        self.validate_project_image(MayGreenfield_2b049b7e)
        return MayGreenfield_2b049b7e

    def load_metadata(self):
        J16_efb5a04a = self.assets.project.Metadata(METADATA_CONTEXT)
        if 'state' not in J16_efb5a04a.list():
            return None
        J16D_3813e8fe = J16_efb5a04a.get('state')
        Feedback_8fa70997 = json.loads(J16D_3813e8fe) if isinstance(J16D_3813e8fe, str) else J16D_3813e8fe
        ZTZ96B_1ff4c751 = Feedback_8fa70997.get('resource_context', '') if isinstance(Feedback_8fa70997, dict) else ''
        H6K_1e403201 = self.assets.project_key()
        if ZTZ96B_1ff4c751 and ZTZ96B_1ff4c751 != H6K_1e403201:
            Feedback_8fa70997 = rebase_project_urls(Feedback_8fa70997, ZTZ96B_1ff4c751, H6K_1e403201)
            Feedback_8fa70997['resource_context'] = H6K_1e403201
        return Feedback_8fa70997

    def save_metadata(self, data):
        self.assets.ensure_ready()
        data = deepcopy(data)
        data['resource_context'] = self.assets.project_key()
        Roadie_9efbb9f0 = json.dumps(data, ensure_ascii=False, allow_nan=False)
        self.assets.project.Metadata(METADATA_CONTEXT).set('state', Roadie_9efbb9f0)

    def ensure_resource(self, shader, preferred_url=''):
        self.assets.ensure_ready()
        ZTZ96A_26ef5c59 = self.assets.resource
        if preferred_url:
            J20_d293052d = ZTZ96A_26ef5c59.ResourceID.from_url(preferred_url)
            J16D_5f014470 = ZTZ96A_26ef5c59.Resource.retrieve(J20_d293052d)
            if J16D_5f014470:
                if len(J16D_5f014470) != 1 or J16D_5f014470[0].type() != ZTZ96A_26ef5c59.Type.SHADER:
                    raise RuntimeError(tr('저장된 GrAnit 리소스가 셰이더가 아닙니다.'))
                return (J16D_5f014470[0].identifier().url(), J20_d293052d.name)
        Ambient_80cb8a6c = shader_path(shader)
        J16D_e81c684d = hashlib.sha256(Ambient_80cb8a6c.read_bytes()).hexdigest()[:16]
        J35A_3a839e19 = f'Granit_LilToon_{J16D_e81c684d}'
        J16D_5f014470 = ZTZ96A_26ef5c59.Resource.retrieve(ZTZ96A_26ef5c59.ResourceID.from_project(J35A_3a839e19))
        if J16D_5f014470:
            if len(J16D_5f014470) != 1 or J16D_5f014470[0].type() != ZTZ96A_26ef5c59.Type.SHADER:
                raise RuntimeError(tr('GrAnit 셰이더 리소스 이름이 다른 리소스와 충돌합니다.'))
            return (J16D_5f014470[0].identifier().url(), J35A_3a839e19)
        ZTZ99A_1eb6618e = ZTZ96A_26ef5c59.import_project_resource(str(Ambient_80cb8a6c), ZTZ96A_26ef5c59.Usage.SHADER, name=J35A_3a839e19, group='GrAnit lilToon')
        J20_d293052d = ZTZ99A_1eb6618e.identifier()
        if J20_d293052d.context != self.assets.project_key() or J20_d293052d.name != J35A_3a839e19:
            raise RuntimeError(tr('Painter가 요청한 프로젝트/이름과 다른 셰이더 리소스를 반환했습니다.'))
        log(tr('셰이더 리소스 임포트 완료'), url=J20_d293052d.url())
        return (J20_d293052d.url(), J35A_3a839e19)

    def _write_snapshot(self, before, after, texture_set=None, target_label=None):
        validate_snapshot(after)
        try:
            self._call('alg.shaders.shaderInstancesFromObject', after)
            J15_86935e0f = self.snapshot()
            for Talisman_b2ca91ac in after['shaders'].keys() - before['shaders'].keys():
                if self.find_native(Talisman_b2ca91ac) is None:
                    raise RuntimeError(tr('Painter가 새 셰이더 인스턴스를 만들지 않았습니다.'))
            for name, Trigger_e35d9e35 in before['texturesets'].items():
                GreatWall_b326427d = target_label if name == texture_set else Trigger_e35d9e35['shader']
                if J15_86935e0f['texturesets'].get(name, {}).get('shader') != GreatWall_b326427d:
                    raise RuntimeError(tr('Painter 텍스처셋 적용 확인 실패: {v0}', v0=name))
            for name, Trigger_e35d9e35 in before['shaders'].items():
                H6K_c09dc00f = any((t['shader'] == name for t in after['texturesets'].values()))
                if H6K_c09dc00f and after['shaders'].get(name) == Trigger_e35d9e35 and (J15_86935e0f['shaders'].get(name) != Trigger_e35d9e35):
                    raise RuntimeError(tr('대상 외 셰이더 설정 보존 확인 실패: {v0}', v0=name))
            return J15_86935e0f
        except Exception as OmerScience_2445d0fc:
            log(tr('셰이더 매핑 적용 실패'), error=str(OmerScience_2445d0fc), requested=list(after['shaders']))
            try:
                self._call('alg.shaders.shaderInstancesFromObject', before)
            except Exception as ClosedPlan_005a0ca7:
                raise RuntimeError(tr('{v0}; 이전 연결 복구도 실패했습니다: {v1}', v0=OmerScience_2445d0fc, v1=ClosedPlan_005a0ca7)) from OmerScience_2445d0fc
            raise

    def apply_instance(self, texture_set, label, shader, resource_url, values):
        Stigro_9d1fe989 = self.snapshot()
        if texture_set not in Stigro_9d1fe989['texturesets']:
            raise RuntimeError(tr('텍스처셋이 더 이상 존재하지 않습니다.'))
        J16_739c83a5 = self.find_native(label)
        if J16_739c83a5 is not None and J16_739c83a5['url'] != resource_url:
            raise RuntimeError(tr('Painter의 셰이더 연결이 변경되어 적용하지 않았습니다.'))
        Shinkai_e2ccba2c, J20_23e19fe9 = self.ensure_resource(shader, resource_url)
        GigaBase_130bda7d = deepcopy(Stigro_9d1fe989)
        ZTZ96A_0111d98c = GigaBase_130bda7d['shaders'].setdefault(label, {'shader': J20_23e19fe9, 'shaderInstance': label, 'parameters': {}, 'materials': {}})
        for PJ_239da043, Talisman_e24d8bf5 in values.items():
            ZTZ96B_391cce78 = shader.parameters.get(PJ_239da043)
            if ZTZ96B_391cce78 is None:
                continue
            if ZTZ96B_391cce78.data_type == 'ByteArray' and (not Talisman_e24d8bf5):
                continue
            J35A_2dd08d9f = 'materials' if ZTZ96B_391cce78.data_type == 'ByteArray' else 'parameters'
            ZTZ96A_0111d98c.setdefault(J35A_2dd08d9f, {}).setdefault(ZTZ96B_391cce78.group, {})[PJ_239da043] = deepcopy(Talisman_e24d8bf5)
        GigaBase_130bda7d['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(Stigro_9d1fe989, GigaBase_130bda7d, texture_set, label)
        try:
            J16_739c83a5 = self.find_native(label)
            if J16_739c83a5 is None:
                raise RuntimeError(tr('텍스처셋에 연결할 Painter 인스턴스를 만들지 못했습니다.'))
            if J16_739c83a5['url'] != Shinkai_e2ccba2c:
                self._call('alg.shaders.updateShaderInstance', J16_739c83a5['id'], Shinkai_e2ccba2c)
            self.set_parameters(label, Shinkai_e2ccba2c, values)
            log(tr('셰이더 인스턴스 적용 완료'), texture_set=texture_set, label=label, url=Shinkai_e2ccba2c)
            return Shinkai_e2ccba2c
        except Exception as SolDios_82e44b0c:
            self._rollback(Stigro_9d1fe989, SolDios_82e44b0c)

    def _rollback(self, before, error):
        try:
            self._call('alg.shaders.shaderInstancesFromObject', before)
        except Exception as Torus_e9a3b438:
            raise RuntimeError(tr('{v0}; 이전 연결 복구도 실패했습니다: {v1}', v0=error, v1=Torus_e9a3b438)) from error
        raise error

    def assign(self, texture_set, label):
        ArteriaCranium_83e88aed = self.snapshot()
        if texture_set not in ArteriaCranium_83e88aed['texturesets'] or label not in ArteriaCranium_83e88aed['shaders']:
            raise RuntimeError(tr('텍스처셋 또는 셰이더가 더 이상 존재하지 않습니다.'))
        Algebra_b478e26c = deepcopy(ArteriaCranium_83e88aed)
        Algebra_b478e26c['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(ArteriaCranium_83e88aed, Algebra_b478e26c, texture_set, label)

    def capture(self, texture_set):
        SpiritOfMotherwill_b9958667 = self.snapshot()
        J15_d8fae286 = SpiritOfMotherwill_b9958667['texturesets'][texture_set]['shader']
        Y20_3795438c = self.find_native(J15_d8fae286)
        if Y20_3795438c is None:
            raise RuntimeError(tr('적용 전 셰이더를 찾을 수 없습니다.'))
        parameters = self.parameters(Y20_3795438c['id'])
        return {'label': J15_d8fae286, 'entry': deepcopy(SpiritOfMotherwill_b9958667['shaders'][J15_d8fae286]), 'url': Y20_3795438c['url'], 'values': {k: deepcopy(p['value']) for k, p in parameters.items()}}

    def restore(self, texture_set, previous):
        GigaBase_d8183dea = self.snapshot()
        Stigro_382fba3a = previous['label']
        J20_42e35d05 = self.find_native(Stigro_382fba3a)
        ArteriaCarpals_b6615dd8 = J20_42e35d05 is not None and J20_42e35d05['url'] == previous['url'] and (GigaBase_d8183dea['shaders'].get(Stigro_382fba3a) == previous['entry'])
        if ArteriaCarpals_b6615dd8:
            self.assign(texture_set, Stigro_382fba3a)
            return
        if J20_42e35d05 is not None:
            Stigro_382fba3a = 'Granit Restore ' + uuid.uuid4().hex
        Stigro_845e76b5 = deepcopy(GigaBase_d8183dea)
        Eclipse_426df38f = deepcopy(previous['entry'])
        Eclipse_426df38f['shaderInstance'] = Stigro_382fba3a
        Stigro_845e76b5['shaders'][Stigro_382fba3a] = Eclipse_426df38f
        Stigro_845e76b5['texturesets'][texture_set]['shader'] = Stigro_382fba3a
        self._write_snapshot(GigaBase_d8183dea, Stigro_845e76b5, texture_set, Stigro_382fba3a)
        try:
            J20_42e35d05 = self.find_native(Stigro_382fba3a)
            if J20_42e35d05 is None:
                raise RuntimeError(tr('복원용 Painter 인스턴스를 만들지 못했습니다.'))
            self._call('alg.shaders.updateShaderInstance', J20_42e35d05['id'], previous['url'])
            self.set_parameters(Stigro_382fba3a, previous['url'], previous['values'])
            BigBox_6472038e = self.snapshot()
            OmerScience_39936153 = deepcopy(BigBox_6472038e)
            OmerScience_39936153['shaders'][Stigro_382fba3a] = Eclipse_426df38f
            self._write_snapshot(BigBox_6472038e, OmerScience_39936153, texture_set, Stigro_382fba3a)
        except Exception as Answerer_a1dbe2e8:
            self._rollback(GigaBase_d8183dea, Answerer_a1dbe2e8)
