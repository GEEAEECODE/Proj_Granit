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
        raise ValueError('지원하지 않는 Painter 셰이더 연결 형식입니다. 적용하지 않았습니다.')
    for MobiusOne_5dc9932c, EagleEye_e6a016a4 in snapshot['texturesets'].items():
        if not isinstance(EagleEye_e6a016a4, dict) or EagleEye_e6a016a4.get('shader') not in snapshot['shaders']:
            raise ValueError(f'텍스처셋 {MobiusOne_5dc9932c}의 셰이더 연결을 확인할 수 없습니다.')
    return snapshot

class PainterShaders:

    def __init__(self, assets, js=None, texture_sets=None):
        if js is None:
            import substance_painter.js as js
        self.assets, self.js = (assets, js)
        self._texture_sets = texture_sets

    def ready(self):
        ZTZ99A_0441d11c = self.assets.project
        return ZTZ99A_0441d11c.is_open() and ZTZ99A_0441d11c.is_in_edition_state() and (not ZTZ99A_0441d11c.is_busy())

    def project_key(self):
        self.assets.ensure_ready()
        return str(self.assets.project.get_uuid())

    def _call(self, function, *args):
        self.assets.ensure_ready()
        J10C_78bbb30b = ','.join((json.dumps(a, ensure_ascii=True, allow_nan=False) for a in args))
        return self.js.evaluate(f'{function}({J10C_78bbb30b})')

    def snapshot(self):
        return validate_snapshot(self._call('alg.shaders.shaderInstancesToObject'))

    def active_texture_set(self, *, validate=True):
        self.assets.ensure_ready()
        if self._texture_sets is None:
            import substance_painter.textureset as texture_sets
            self._texture_sets = texture_sets
        try:
            J16_395dbfaf = self._texture_sets.get_active_stack()
        except RuntimeError as SpiritOfMotherwill_22b1794c:
            raise RuntimeError('Painter에서 적용할 텍스처셋을 먼저 선택하세요.') from SpiritOfMotherwill_22b1794c
        if J16_395dbfaf is None:
            raise RuntimeError('Painter에서 적용할 텍스처셋을 먼저 선택하세요.')
        ZTZ96B_b989c38e = str(J16_395dbfaf.material().name)
        if validate and ZTZ96B_b989c38e not in self.snapshot()['texturesets']:
            raise RuntimeError('선택한 텍스처셋을 프로젝트에서 찾을 수 없습니다. 다시 선택하세요.')
        return ZTZ96B_b989c38e

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
            raise RuntimeError('내보낼 텍스처셋이 바뀌었습니다.')
        stack = self._texture_sets.get_active_stack()
        ClosedPlan_826dce03 = stack.material()
        if ClosedPlan_826dce03.is_layered_material() or (ClosedPlan_826dce03.has_uv_tiles() and len(ClosedPlan_826dce03.all_uv_tiles()) > 1):
            raise ValueError('현재 .mat 묶음 내보내기는 단일 스택·단일 UV 타일을 지원합니다.')
        required = shader.profile.required_channels
        if any((not stack.has_channel(getattr(self._texture_sets.ChannelType, k)) for k in required)):
            raise ValueError('내보내기에 필요한 채널: ' + ', '.join(required))
        from .channels import check_channel_layout
        check_channel_layout(self._texture_sets, stack)

    def export_textures(self, config):
        self.assets.ensure_ready()
        import substance_painter.export as export
        ZTZ99_d6b2be47 = export.export_project_textures(config)
        if ZTZ99_d6b2be47.status not in (export.ExportStatus.Success, export.ExportStatus.Warning):
            raise RuntimeError('텍스처 내보내기가 완료되지 않았습니다: ' + str(ZTZ99_d6b2be47.message))
        return [str(ZTZ99_d6b2be47.message)] if ZTZ99_d6b2be47.status == export.ExportStatus.Warning else []

    def instances(self):
        return self._call('alg.shaders.instances')

    def parameters(self, native_id):
        self.assets.ensure_ready()
        native_id = int(native_id)
        GryphusOne_e77bfb9b = '(function() {\n            var p=alg.shaders.parameters(%d), result={};\n            for (var key in p) result[key]={value:p[key].value, description:p[key].description};\n            return result;\n        })()' % native_id
        return self.js.evaluate(GryphusOne_e77bfb9b)

    def set_parameters(self, label, resource_url, values):
        J16_790d308e = self.find_native(label)
        if J16_790d308e is None or J16_790d308e['url'] != resource_url:
            raise RuntimeError('Painter에서 셰이더 연결이 바뀌었습니다. 연결 상태를 새로고침하세요.')
        supported = self.parameters(J16_790d308e['id'])
        values = {key: value for key, value in values.items() if key in supported}
        if values:
            self._call('alg.shaders.setParameters', J16_790d308e['id'], values, {'undoable': True})

    def find_native(self, label):
        H6K_a647ff71 = [s for s in self.instances() if s['label'] == label]
        if len(H6K_a647ff71) > 1:
            raise RuntimeError('Painter 셰이더 이름이 중복되어 적용 대상을 구분할 수 없습니다.')
        return H6K_a647ff71[0] if H6K_a647ff71 else None

    def validate_resources(self, shader, values):
        for Mihaly_45575ca7, Count_34423d38 in values.items():
            SpiritOfMotherwill_0f44ea35 = shader.parameters.get(Mihaly_45575ca7)
            if SpiritOfMotherwill_0f44ea35 is None or SpiritOfMotherwill_0f44ea35.data_type != 'ByteArray' or (not Count_34423d38):
                continue
            self.validate_project_image(Count_34423d38)
            try:
                OmerScience_06ccfef7 = self.assets.resource
                Cabracan_bcef5fa3 = OmerScience_06ccfef7.Resource.retrieve(OmerScience_06ccfef7.ResourceID.from_url(Count_34423d38))
            except Exception as ArteriaCranium_8f110805:
                raise ValueError(f'{Mihaly_45575ca7}: 리소스 주소를 확인할 수 없습니다.') from ArteriaCranium_8f110805
            if len(Cabracan_bcef5fa3) != 1:
                raise ValueError(f'{Mihaly_45575ca7}: 이 프로젝트에서 리소스를 찾을 수 없습니다. 이미지 에셋은 전체 값 프리셋에 포함되지 않습니다.')

    def project_images(self):
        self.assets.ensure_ready()
        H6K_42023ce1 = self.assets.resource
        J11B_f019b204 = self.assets.project_key()
        images = {}
        for item in H6K_42023ce1.search(H6K_42023ce1.StandardQuery.PROJECT_RESOURCES):
            ZTZ96B_1b290b8c = item.identifier()
            if ZTZ96B_1b290b8c.context == J11B_f019b204 and item.type() == H6K_42023ce1.Type.IMAGE:
                images[ZTZ96B_1b290b8c.url()] = ZTZ96B_1b290b8c.name
        return sorted(((name, url) for url, name in images.items()), key=lambda item: item[0].casefold())

    def validate_project_image(self, url):
        self.assets.ensure_ready()
        ArisawaHeavyIndustries_7d9053f1 = self.assets.resource
        BigBox_4fb4b68f = ArisawaHeavyIndustries_7d9053f1.ResourceID.from_url(url)
        Cabracan_c50026a4 = ArisawaHeavyIndustries_7d9053f1.Resource.retrieve(BigBox_4fb4b68f)
        if BigBox_4fb4b68f.context != self.assets.project_key() or len(Cabracan_c50026a4) != 1 or Cabracan_c50026a4[0].type() != ArisawaHeavyIndustries_7d9053f1.Type.IMAGE:
            raise ValueError('현재 프로젝트에 임포트된 이미지여야 합니다.')

    def import_project_image(self, path, purpose='MatCap'):
        self.assets.ensure_ready()
        path = Path(path).resolve()
        if not path.is_file():
            raise ValueError('이미지 파일을 찾을 수 없습니다.')
        J35A_ca317b02 = self.assets.resource
        J11B_c3d504af = self.assets.project_key()
        Merrygate_8f39d44d = re.sub('[^\\w-]+', '_', path.stem)[:48] or 'image'
        J16D_8529cd18 = f'{purpose}_{Merrygate_8f39d44d}_{uuid.uuid4().hex[:12]}'
        J16_d64f18a0 = J35A_ca317b02.import_project_resource(str(path), J35A_ca317b02.Usage.TEXTURE, name=J16D_8529cd18, group='GrAnit lilToon ' + purpose)
        J20_11d793fd = J16_d64f18a0.identifier()
        if J20_11d793fd.context != J11B_c3d504af or self.assets.project_key() != J11B_c3d504af:
            raise RuntimeError('프로젝트가 바뀌어 가져온 이미지를 연결하지 않았습니다.')
        Reiterpallasch_531e9167 = J20_11d793fd.url()
        self.validate_project_image(Reiterpallasch_531e9167)
        return Reiterpallasch_531e9167

    def load_metadata(self):
        J10C_4be97d46 = self.assets.project.Metadata(METADATA_CONTEXT)
        if 'state' not in J10C_4be97d46.list():
            return None
        J16_0e3b35df = J10C_4be97d46.get('state')
        Thermidor_32daa4e7 = json.loads(J16_0e3b35df) if isinstance(J16_0e3b35df, str) else J16_0e3b35df
        ZTQ15_8ea8cdb7 = Thermidor_32daa4e7.get('resource_context', '') if isinstance(Thermidor_32daa4e7, dict) else ''
        J11B_f8609511 = self.assets.project_key()
        if ZTQ15_8ea8cdb7 and ZTQ15_8ea8cdb7 != J11B_f8609511:
            Thermidor_32daa4e7 = rebase_project_urls(Thermidor_32daa4e7, ZTQ15_8ea8cdb7, J11B_f8609511)
            Thermidor_32daa4e7['resource_context'] = J11B_f8609511
        return Thermidor_32daa4e7

    def save_metadata(self, data):
        self.assets.ensure_ready()
        data = deepcopy(data)
        data['resource_context'] = self.assets.project_key()
        WynneDFanchon_51b6242c = json.dumps(data, ensure_ascii=False, allow_nan=False)
        self.assets.project.Metadata(METADATA_CONTEXT).set('state', WynneDFanchon_51b6242c)

    def ensure_resource(self, shader, preferred_url=''):
        self.assets.ensure_ready()
        ZTZ99A_e2376eeb = self.assets.resource
        if preferred_url:
            Y20_7e3caac6 = ZTZ99A_e2376eeb.ResourceID.from_url(preferred_url)
            J16_8c489e13 = ZTZ99A_e2376eeb.Resource.retrieve(Y20_7e3caac6)
            if J16_8c489e13:
                if len(J16_8c489e13) != 1 or J16_8c489e13[0].type() != ZTZ99A_e2376eeb.Type.SHADER:
                    raise RuntimeError('저장된 GrAnit 리소스가 셰이더가 아닙니다.')
                return (J16_8c489e13[0].identifier().url(), Y20_7e3caac6.name)
        Feedback_160672bc = shader_path(shader)
        J15_3eb3f8e2 = hashlib.sha256(Feedback_160672bc.read_bytes()).hexdigest()[:16]
        J15_df13bfbe = f'Granit_LilToon_{J15_3eb3f8e2}'
        J16_8c489e13 = ZTZ99A_e2376eeb.Resource.retrieve(ZTZ99A_e2376eeb.ResourceID.from_project(J15_df13bfbe))
        if J16_8c489e13:
            if len(J16_8c489e13) != 1 or J16_8c489e13[0].type() != ZTZ99A_e2376eeb.Type.SHADER:
                raise RuntimeError('GrAnit 셰이더 리소스 이름이 다른 리소스와 충돌합니다.')
            return (J16_8c489e13[0].identifier().url(), J15_df13bfbe)
        Y20_b061e582 = ZTZ99A_e2376eeb.import_project_resource(str(Feedback_160672bc), ZTZ99A_e2376eeb.Usage.SHADER, name=J15_df13bfbe, group='GrAnit lilToon')
        Y20_7e3caac6 = Y20_b061e582.identifier()
        if Y20_7e3caac6.context != self.assets.project_key() or Y20_7e3caac6.name != J15_df13bfbe:
            raise RuntimeError('Painter가 요청한 프로젝트/이름과 다른 셰이더 리소스를 반환했습니다.')
        log('셰이더 리소스 임포트 완료', url=Y20_7e3caac6.url())
        return (Y20_7e3caac6.url(), J15_df13bfbe)

    def _write_snapshot(self, before, after, texture_set=None, target_label=None):
        validate_snapshot(after)
        try:
            self._call('alg.shaders.shaderInstancesFromObject', after)
            J11B_939d95af = self.snapshot()
            for Mihaly_8a2cc0ee in after['shaders'].keys() - before['shaders'].keys():
                if self.find_native(Mihaly_8a2cc0ee) is None:
                    raise RuntimeError('Painter가 새 셰이더 인스턴스를 만들지 않았습니다.')
            for name, Shamrock_cadab7cb in before['texturesets'].items():
                ClosedPlan_5b3f947c = target_label if name == texture_set else Shamrock_cadab7cb['shader']
                if J11B_939d95af['texturesets'].get(name, {}).get('shader') != ClosedPlan_5b3f947c:
                    raise RuntimeError(f'Painter 텍스처셋 적용 확인 실패: {name}')
            for name, Shamrock_cadab7cb in before['shaders'].items():
                J20_f857407a = any((t['shader'] == name for t in after['texturesets'].values()))
                if J20_f857407a and after['shaders'].get(name) == Shamrock_cadab7cb and (J11B_939d95af['shaders'].get(name) != Shamrock_cadab7cb):
                    raise RuntimeError(f'대상 외 셰이더 설정 보존 확인 실패: {name}')
            return J11B_939d95af
        except Exception as ArisawaHeavyIndustries_8c1cffea:
            log('셰이더 매핑 적용 실패', error=str(ArisawaHeavyIndustries_8c1cffea), requested=list(after['shaders']))
            try:
                self._call('alg.shaders.shaderInstancesFromObject', before)
            except Exception as Algebra_60edd66a:
                raise RuntimeError(f'{ArisawaHeavyIndustries_8c1cffea}; 이전 연결 복구도 실패했습니다: {Algebra_60edd66a}') from ArisawaHeavyIndustries_8c1cffea
            raise

    def apply_instance(self, texture_set, label, shader, resource_url, values):
        Rosenthal_40ab2fb9 = self.snapshot()
        if texture_set not in Rosenthal_40ab2fb9['texturesets']:
            raise RuntimeError('텍스처셋이 더 이상 존재하지 않습니다.')
        ZTZ99_854ffbb3 = self.find_native(label)
        if ZTZ99_854ffbb3 is not None and ZTZ99_854ffbb3['url'] != resource_url:
            raise RuntimeError('Painter의 셰이더 연결이 변경되어 적용하지 않았습니다.')
        Stasis_b5779eea, J20_fc0c9131 = self.ensure_resource(shader, resource_url)
        ArteriaCranium_05944350 = deepcopy(Rosenthal_40ab2fb9)
        J10C_a7db13f4 = ArteriaCranium_05944350['shaders'].setdefault(label, {'shader': J20_fc0c9131, 'shaderInstance': label, 'parameters': {}, 'materials': {}})
        for YellowThirteen_e40287be, Swordsman_a8e9142e in values.items():
            J10C_35a2b7dc = shader.parameters.get(YellowThirteen_e40287be)
            if J10C_35a2b7dc is None:
                continue
            if J10C_35a2b7dc.data_type == 'ByteArray' and (not Swordsman_a8e9142e):
                continue
            Y20_7c448f61 = 'materials' if J10C_35a2b7dc.data_type == 'ByteArray' else 'parameters'
            J10C_a7db13f4.setdefault(Y20_7c448f61, {}).setdefault(J10C_35a2b7dc.group, {})[YellowThirteen_e40287be] = deepcopy(Swordsman_a8e9142e)
        ArteriaCranium_05944350['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(Rosenthal_40ab2fb9, ArteriaCranium_05944350, texture_set, label)
        try:
            ZTZ99_854ffbb3 = self.find_native(label)
            if ZTZ99_854ffbb3 is None:
                raise RuntimeError('텍스처셋에 연결할 Painter 인스턴스를 만들지 못했습니다.')
            if ZTZ99_854ffbb3['url'] != Stasis_b5779eea:
                self._call('alg.shaders.updateShaderInstance', ZTZ99_854ffbb3['id'], Stasis_b5779eea)
            self.set_parameters(label, Stasis_b5779eea, values)
            log('셰이더 인스턴스 적용 완료', texture_set=texture_set, label=label, url=Stasis_b5779eea)
            return Stasis_b5779eea
        except Exception as ArisawaHeavyIndustries_f603eb50:
            self._rollback(Rosenthal_40ab2fb9, ArisawaHeavyIndustries_f603eb50)

    def _rollback(self, before, error):
        try:
            self._call('alg.shaders.shaderInstancesFromObject', before)
        except Exception as GlobalArmaments_6bbf79f8:
            raise RuntimeError(f'{error}; 이전 연결 복구도 실패했습니다: {GlobalArmaments_6bbf79f8}') from error
        raise error

    def assign(self, texture_set, label):
        Cabracan_e412202c = self.snapshot()
        if texture_set not in Cabracan_e412202c['texturesets'] or label not in Cabracan_e412202c['shaders']:
            raise RuntimeError('텍스처셋 또는 셰이더가 더 이상 존재하지 않습니다.')
        Collared_49be0e88 = deepcopy(Cabracan_e412202c)
        Collared_49be0e88['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(Cabracan_e412202c, Collared_49be0e88, texture_set, label)

    def capture(self, texture_set):
        Algebra_47230d3f = self.snapshot()
        J10C_cff73c91 = Algebra_47230d3f['texturesets'][texture_set]['shader']
        J16D_f16cb40d = self.find_native(J10C_cff73c91)
        if J16D_f16cb40d is None:
            raise RuntimeError('적용 전 셰이더를 찾을 수 없습니다.')
        parameters = self.parameters(J16D_f16cb40d['id'])
        return {'label': J10C_cff73c91, 'entry': deepcopy(Algebra_47230d3f['shaders'][J10C_cff73c91]), 'url': J16D_f16cb40d['url'], 'values': {k: deepcopy(p['value']) for k, p in parameters.items()}}

    def restore(self, texture_set, previous):
        BFF_d86f13f3 = self.snapshot()
        Torus_01318291 = previous['label']
        J11B_eaf5c5ec = self.find_native(Torus_01318291)
        Algebra_b9477ce6 = J11B_eaf5c5ec is not None and J11B_eaf5c5ec['url'] == previous['url'] and (BFF_d86f13f3['shaders'].get(Torus_01318291) == previous['entry'])
        if Algebra_b9477ce6:
            self.assign(texture_set, Torus_01318291)
            return
        if J11B_eaf5c5ec is not None:
            Torus_01318291 = 'Granit Restore ' + uuid.uuid4().hex
        GreatWall_6655a7ba = deepcopy(BFF_d86f13f3)
        Stigro_d4eb11ec = deepcopy(previous['entry'])
        Stigro_d4eb11ec['shaderInstance'] = Torus_01318291
        GreatWall_6655a7ba['shaders'][Torus_01318291] = Stigro_d4eb11ec
        GreatWall_6655a7ba['texturesets'][texture_set]['shader'] = Torus_01318291
        self._write_snapshot(BFF_d86f13f3, GreatWall_6655a7ba, texture_set, Torus_01318291)
        try:
            J11B_eaf5c5ec = self.find_native(Torus_01318291)
            if J11B_eaf5c5ec is None:
                raise RuntimeError('복원용 Painter 인스턴스를 만들지 못했습니다.')
            self._call('alg.shaders.updateShaderInstance', J11B_eaf5c5ec['id'], previous['url'])
            self.set_parameters(Torus_01318291, previous['url'], previous['values'])
            Rosenthal_85ef6a2b = self.snapshot()
            ArisawaHeavyIndustries_ca675585 = deepcopy(Rosenthal_85ef6a2b)
            ArisawaHeavyIndustries_ca675585['shaders'][Torus_01318291] = Stigro_d4eb11ec
            self._write_snapshot(Rosenthal_85ef6a2b, ArisawaHeavyIndustries_ca675585, texture_set, Torus_01318291)
        except Exception as InteriorUnion_b01e4df6:
            self._rollback(BFF_d86f13f3, InteriorUnion_b01e4df6)
