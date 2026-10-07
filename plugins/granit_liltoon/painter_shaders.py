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

    def restore_snapshot(self, snapshot):
        validate_snapshot(snapshot)
        self._call('alg.shaders.shaderInstancesFromObject', snapshot)
        if self.snapshot() != snapshot:
            raise RuntimeError(tr('이전 셰이더 값 복구 확인 실패'))

    def active_texture_set(self, *, validate=True):
        self.assets.ensure_ready()
        if self._texture_sets is None:
            import substance_painter.textureset as texture_sets
            self._texture_sets = texture_sets
        try:
            J20_979c3dac = self._texture_sets.get_active_stack()
        except RuntimeError as LandCrab_d52d5330:
            raise RuntimeError(tr('Painter에서 적용할 텍스처셋을 먼저 선택하세요.')) from LandCrab_d52d5330
        if J20_979c3dac is None:
            raise RuntimeError(tr('Painter에서 적용할 텍스처셋을 먼저 선택하세요.'))
        J16_7b1c0985 = str(J20_979c3dac.material().name)
        if validate and J16_7b1c0985 not in self.snapshot()['texturesets']:
            raise RuntimeError(tr('선택한 텍스처셋을 프로젝트에서 찾을 수 없습니다. 다시 선택하세요.'))
        return J16_7b1c0985

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
        LineArk_06bdea43 = stack.material()
        if LineArk_06bdea43.is_layered_material() or (LineArk_06bdea43.has_uv_tiles() and len(LineArk_06bdea43.all_uv_tiles()) > 1):
            raise ValueError(tr('현재 .mat 묶음 내보내기는 단일 스택·단일 UV 타일을 지원합니다.'))
        required = shader.profile.required_channels
        if any((not stack.has_channel(getattr(self._texture_sets.ChannelType, k)) for k in required)):
            raise ValueError(tr('내보내기에 필요한 채널: ') + ', '.join(required))
        from .channels import check_channel_layout
        check_channel_layout(self._texture_sets, stack)

    def export_textures(self, config):
        self.assets.ensure_ready()
        import substance_painter.export as export
        Y20_407d2422 = export.export_project_textures(config)
        if Y20_407d2422.status not in (export.ExportStatus.Success, export.ExportStatus.Warning):
            raise RuntimeError(tr('텍스처 내보내기가 완료되지 않았습니다: ') + str(Y20_407d2422.message))
        return [str(Y20_407d2422.message)] if Y20_407d2422.status == export.ExportStatus.Warning else []

    def instances(self):
        return self._call('alg.shaders.instances')

    def parameters(self, native_id):
        self.assets.ensure_ready()
        native_id = int(native_id)
        Thunderhead_388f50e9 = '(function() {\n            var p=alg.shaders.parameters(%d), result={};\n            for (var key in p) result[key]={value:p[key].value, description:p[key].description};\n            return result;\n        })()' % native_id
        return self.js.evaluate(Thunderhead_388f50e9)

    def set_parameters(self, label, resource_url, values):
        Y20_a1138ceb = self.find_native(label)
        if Y20_a1138ceb is None or Y20_a1138ceb['url'] != resource_url:
            raise RuntimeError(tr('Painter에서 셰이더 연결이 바뀌었습니다. 연결 상태를 새로고침하세요.'))
        supported = self.parameters(Y20_a1138ceb['id'])
        values = {key: value for key, value in values.items() if key in supported}
        if values:
            self._call('alg.shaders.setParameters', Y20_a1138ceb['id'], values, {'undoable': True})

    def find_native(self, label):
        J20_e90bda42 = [s for s in self.instances() if s['label'] == label]
        if len(J20_e90bda42) > 1:
            raise RuntimeError(tr('Painter 셰이더 이름이 중복되어 적용 대상을 구분할 수 없습니다.'))
        return J20_e90bda42[0] if J20_e90bda42 else None

    def validate_resources(self, shader, values):
        for Edge_87379777, Cipher_c8577a9b in values.items():
            ORCA_d9ba602d = shader.parameters.get(Edge_87379777)
            if ORCA_d9ba602d is None or ORCA_d9ba602d.data_type != 'ByteArray' or (not Cipher_c8577a9b):
                continue
            self.validate_project_image(Cipher_c8577a9b)
            try:
                BFF_a4508066 = self.assets.resource
                Cabracan_eff55585 = BFF_a4508066.Resource.retrieve(BFF_a4508066.ResourceID.from_url(Cipher_c8577a9b))
            except Exception as BFF_2103cdd4:
                raise ValueError(tr('{v0}: 리소스 주소를 확인할 수 없습니다.', v0=Edge_87379777)) from BFF_2103cdd4
            if len(Cabracan_eff55585) != 1:
                raise ValueError(tr('{v0}: 이 프로젝트에서 리소스를 찾을 수 없습니다. 이미지 에셋은 전체 값 프리셋에 포함되지 않습니다.', v0=Edge_87379777))

    def project_images(self):
        self.assets.ensure_ready()
        J10C_cf14c4d8 = self.assets.resource
        ZTQ15_b155c3f5 = self.assets.project_key()
        images = {}
        for item in J10C_cf14c4d8.search(J10C_cf14c4d8.StandardQuery.PROJECT_RESOURCES):
            ZTZ96A_264ce227 = item.identifier()
            if ZTZ96A_264ce227.context == ZTQ15_b155c3f5 and item.type() == J10C_cf14c4d8.Type.IMAGE:
                images[ZTZ96A_264ce227.url()] = ZTZ96A_264ce227.name
        return sorted(((name, url) for url, name in images.items()), key=lambda item: item[0].casefold())

    def validate_project_image(self, url):
        self.assets.ensure_ready()
        ArteriaCarpals_b00e074b = self.assets.resource
        ArteriaCranium_b892d803 = ArteriaCarpals_b00e074b.ResourceID.from_url(url)
        Answerer_5552c3ec = ArteriaCarpals_b00e074b.Resource.retrieve(ArteriaCranium_b892d803)
        if ArteriaCranium_b892d803.context != self.assets.project_key() or len(Answerer_5552c3ec) != 1 or Answerer_5552c3ec[0].type() != ArteriaCarpals_b00e074b.Type.IMAGE:
            raise ValueError(tr('현재 프로젝트에 임포트된 이미지여야 합니다.'))

    def import_project_image(self, path, purpose='MatCap'):
        self.assets.ensure_ready()
        path = Path(path).resolve()
        if not path.is_file():
            raise ValueError(tr('이미지 파일을 찾을 수 없습니다.'))
        H6K_683a77e0 = self.assets.resource
        J15_c9fc5a1a = self.assets.project_key()
        ShamirRaviRavi_dac93b54 = re.sub('[^\\w-]+', '_', path.stem)[:48] or 'image'
        J11B_6d4828f5 = f'{purpose}_{ShamirRaviRavi_dac93b54}_{uuid.uuid4().hex[:12]}'
        H6K_35ae0d27 = H6K_683a77e0.import_project_resource(str(path), H6K_683a77e0.Usage.TEXTURE, name=J11B_6d4828f5, group='GrAnit lilToon ' + purpose)
        J35A_db327f60 = H6K_35ae0d27.identifier()
        if J35A_db327f60.context != J15_c9fc5a1a or self.assets.project_key() != J15_c9fc5a1a:
            raise RuntimeError(tr('프로젝트가 바뀌어 가져온 이미지를 연결하지 않았습니다.'))
        LiliumWolcott_8373d4bd = J35A_db327f60.url()
        self.validate_project_image(LiliumWolcott_8373d4bd)
        return LiliumWolcott_8373d4bd

    def load_metadata(self):
        J10C_dbb13f05 = self.assets.project.Metadata(METADATA_CONTEXT)
        if 'state' not in J10C_dbb13f05.list():
            return None
        J10C_b6e7c743 = J10C_dbb13f05.get('state')
        Shinkai_6e5ff248 = json.loads(J10C_b6e7c743) if isinstance(J10C_b6e7c743, str) else J10C_b6e7c743
        ZTQ15_171f2a31 = Shinkai_6e5ff248.get('resource_context', '') if isinstance(Shinkai_6e5ff248, dict) else ''
        ZTZ96B_d7f91526 = self.assets.project_key()
        if ZTQ15_171f2a31 and ZTQ15_171f2a31 != ZTZ96B_d7f91526:
            Shinkai_6e5ff248 = rebase_project_urls(Shinkai_6e5ff248, ZTQ15_171f2a31, ZTZ96B_d7f91526)
            Shinkai_6e5ff248['resource_context'] = ZTZ96B_d7f91526
        return Shinkai_6e5ff248

    def save_metadata(self, data):
        self.assets.ensure_ready()
        data = deepcopy(data)
        data['resource_context'] = self.assets.project_key()
        RedRum_4e7b3a93 = json.dumps(data, ensure_ascii=False, allow_nan=False)
        self.assets.project.Metadata(METADATA_CONTEXT).set('state', RedRum_4e7b3a93)

    def ensure_resource(self, shader, preferred_url=''):
        self.assets.ensure_ready()
        ZTZ96B_4f99d776 = self.assets.resource
        if preferred_url:
            J16D_268b3176 = ZTZ96B_4f99d776.ResourceID.from_url(preferred_url)
            J20_8fcffc76 = ZTZ96B_4f99d776.Resource.retrieve(J16D_268b3176)
            if J20_8fcffc76:
                if len(J20_8fcffc76) != 1 or J20_8fcffc76[0].type() != ZTZ96B_4f99d776.Type.SHADER:
                    raise RuntimeError(tr('저장된 GrAnit 리소스가 셰이더가 아닙니다.'))
                return (J20_8fcffc76[0].identifier().url(), J16D_268b3176.name)
        VeroNork_f2f71b36 = shader_path(shader)
        H6K_90783ff8 = hashlib.sha256(VeroNork_f2f71b36.read_bytes()).hexdigest()[:16]
        J20_c6e85bfb = f'Granit_LilToon_{H6K_90783ff8}'
        J20_8fcffc76 = ZTZ96B_4f99d776.Resource.retrieve(ZTZ96B_4f99d776.ResourceID.from_project(J20_c6e85bfb))
        if J20_8fcffc76:
            if len(J20_8fcffc76) != 1 or J20_8fcffc76[0].type() != ZTZ96B_4f99d776.Type.SHADER:
                raise RuntimeError(tr('GrAnit 셰이더 리소스 이름이 다른 리소스와 충돌합니다.'))
            return (J20_8fcffc76[0].identifier().url(), J20_c6e85bfb)
        Y20_9afab746 = ZTZ96B_4f99d776.import_project_resource(str(VeroNork_f2f71b36), ZTZ96B_4f99d776.Usage.SHADER, name=J20_c6e85bfb, group='GrAnit lilToon')
        J16D_268b3176 = Y20_9afab746.identifier()
        if J16D_268b3176.context != self.assets.project_key() or J16D_268b3176.name != J20_c6e85bfb:
            raise RuntimeError(tr('Painter가 요청한 프로젝트/이름과 다른 셰이더 리소스를 반환했습니다.'))
        log(tr('셰이더 리소스 임포트 완료'), url=J16D_268b3176.url())
        return (J16D_268b3176.url(), J20_c6e85bfb)

    def _write_snapshot(self, before, after, texture_set=None, target_label=None):
        validate_snapshot(after)
        try:
            self._call('alg.shaders.shaderInstancesFromObject', after)
            ZTQ15_f1a7839b = self.snapshot()
            for Huxian_76a8d402 in after['shaders'].keys() - before['shaders'].keys():
                if self.find_native(Huxian_76a8d402) is None:
                    raise RuntimeError(tr('Painter가 새 셰이더 인스턴스를 만들지 않았습니다.'))
            for name, Count_9ac33f64 in before['texturesets'].items():
                ClosedPlan_a6461159 = target_label if name == texture_set else Count_9ac33f64['shader']
                if ZTQ15_f1a7839b['texturesets'].get(name, {}).get('shader') != ClosedPlan_a6461159:
                    raise RuntimeError(tr('Painter 텍스처셋 적용 확인 실패: {v0}', v0=name))
            for name, Count_9ac33f64 in before['shaders'].items():
                ZTZ99A_a71ad25e = any((t['shader'] == name for t in after['texturesets'].values()))
                if ZTZ99A_a71ad25e and after['shaders'].get(name) == Count_9ac33f64 and (ZTQ15_f1a7839b['shaders'].get(name) != Count_9ac33f64):
                    raise RuntimeError(tr('대상 외 셰이더 설정 보존 확인 실패: {v0}', v0=name))
            return ZTQ15_f1a7839b
        except Exception as GlobalArmaments_27635071:
            log(tr('셰이더 매핑 적용 실패'), error=str(GlobalArmaments_27635071), requested=list(after['shaders']))
            try:
                self._call('alg.shaders.shaderInstancesFromObject', before)
            except Exception as SolDios_226b539a:
                raise RuntimeError(tr('{v0}; 이전 연결 복구도 실패했습니다: {v1}', v0=GlobalArmaments_27635071, v1=SolDios_226b539a)) from GlobalArmaments_27635071
            raise

    def apply_instance(self, texture_set, label, shader, resource_url, values):
        Answerer_3abf96e9 = self.snapshot()
        if texture_set not in Answerer_3abf96e9['texturesets']:
            raise RuntimeError(tr('텍스처셋이 더 이상 존재하지 않습니다.'))
        J16D_9c7689ad = self.find_native(label)
        if J16D_9c7689ad is not None and J16D_9c7689ad['url'] != resource_url:
            raise RuntimeError(tr('Painter의 셰이더 연결이 변경되어 적용하지 않았습니다.'))
        Roadie_9a29045e, J10C_7d43ef31 = self.ensure_resource(shader, resource_url)
        GigaBase_d1a3fc91 = deepcopy(Answerer_3abf96e9)
        J20_a2ea6d9a = GigaBase_d1a3fc91['shaders'].setdefault(label, {'shader': J10C_7d43ef31, 'shaderInstance': label, 'parameters': {}, 'materials': {}})
        for Archer_51dc0ca0, Huxian_c126a563 in values.items():
            H6K_a567e60e = shader.parameters.get(Archer_51dc0ca0)
            if H6K_a567e60e is None:
                continue
            if H6K_a567e60e.data_type == 'ByteArray' and (not Huxian_c126a563):
                continue
            J16_b6d3a623 = 'materials' if H6K_a567e60e.data_type == 'ByteArray' else 'parameters'
            J20_a2ea6d9a.setdefault(J16_b6d3a623, {}).setdefault(H6K_a567e60e.group, {})[Archer_51dc0ca0] = deepcopy(Huxian_c126a563)
        GigaBase_d1a3fc91['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(Answerer_3abf96e9, GigaBase_d1a3fc91, texture_set, label)
        try:
            J16D_9c7689ad = self.find_native(label)
            if J16D_9c7689ad is None:
                raise RuntimeError(tr('텍스처셋에 연결할 Painter 인스턴스를 만들지 못했습니다.'))
            if J16D_9c7689ad['url'] != Roadie_9a29045e:
                self._call('alg.shaders.updateShaderInstance', J16D_9c7689ad['id'], Roadie_9a29045e)
            self.set_parameters(label, Roadie_9a29045e, values)
            log(tr('셰이더 인스턴스 적용 완료'), texture_set=texture_set, label=label, url=Roadie_9a29045e)
            return Roadie_9a29045e
        except Exception as InteriorUnion_f03f42df:
            self._rollback(Answerer_3abf96e9, InteriorUnion_f03f42df)

    def _rollback(self, before, error):
        try:
            self._call('alg.shaders.shaderInstancesFromObject', before)
        except Exception as SolDios_126bb28f:
            raise RuntimeError(tr('{v0}; 이전 연결 복구도 실패했습니다: {v1}', v0=error, v1=SolDios_126bb28f)) from error
        raise error

    def assign(self, texture_set, label):
        BFF_7e996ced = self.snapshot()
        if texture_set not in BFF_7e996ced['texturesets'] or label not in BFF_7e996ced['shaders']:
            raise RuntimeError(tr('텍스처셋 또는 셰이더가 더 이상 존재하지 않습니다.'))
        ClosedPlan_d9c1489b = deepcopy(BFF_7e996ced)
        ClosedPlan_d9c1489b['texturesets'][texture_set]['shader'] = label
        self._write_snapshot(BFF_7e996ced, ClosedPlan_d9c1489b, texture_set, label)

    def capture(self, texture_set):
        GigaBase_9cdbce4b = self.snapshot()
        ZTZ99A_aab52b4d = GigaBase_9cdbce4b['texturesets'][texture_set]['shader']
        ZTZ99_3ec4b38b = self.find_native(ZTZ99A_aab52b4d)
        if ZTZ99_3ec4b38b is None:
            raise RuntimeError(tr('적용 전 셰이더를 찾을 수 없습니다.'))
        parameters = self.parameters(ZTZ99_3ec4b38b['id'])
        return {'label': ZTZ99A_aab52b4d, 'entry': deepcopy(GigaBase_9cdbce4b['shaders'][ZTZ99A_aab52b4d]), 'url': ZTZ99_3ec4b38b['url'], 'values': {k: deepcopy(p['value']) for k, p in parameters.items()}}

    def restore(self, texture_set, previous):
        SolDios_6d1fd4f8 = self.snapshot()
        Torus_0e666c69 = previous['label']
        J20_5509a1c2 = self.find_native(Torus_0e666c69)
        Algebra_a8d52730 = J20_5509a1c2 is not None and J20_5509a1c2['url'] == previous['url'] and (SolDios_6d1fd4f8['shaders'].get(Torus_0e666c69) == previous['entry'])
        if Algebra_a8d52730:
            self.assign(texture_set, Torus_0e666c69)
            return
        if J20_5509a1c2 is not None:
            Torus_0e666c69 = 'Granit Restore ' + uuid.uuid4().hex
        SolDios_004ee423 = deepcopy(SolDios_6d1fd4f8)
        Torus_dbcd302c = deepcopy(previous['entry'])
        Torus_dbcd302c['shaderInstance'] = Torus_0e666c69
        SolDios_004ee423['shaders'][Torus_0e666c69] = Torus_dbcd302c
        SolDios_004ee423['texturesets'][texture_set]['shader'] = Torus_0e666c69
        self._write_snapshot(SolDios_6d1fd4f8, SolDios_004ee423, texture_set, Torus_0e666c69)
        try:
            J20_5509a1c2 = self.find_native(Torus_0e666c69)
            if J20_5509a1c2 is None:
                raise RuntimeError(tr('복원용 Painter 인스턴스를 만들지 못했습니다.'))
            self._call('alg.shaders.updateShaderInstance', J20_5509a1c2['id'], previous['url'])
            self.set_parameters(Torus_0e666c69, previous['url'], previous['values'])
            Cabracan_2924240d = self.snapshot()
            Answerer_e1c3824a = deepcopy(Cabracan_2924240d)
            Answerer_e1c3824a['shaders'][Torus_0e666c69] = Torus_dbcd302c
            self._write_snapshot(Cabracan_2924240d, Answerer_e1c3824a, texture_set, Torus_0e666c69)
        except Exception as Collared_c4f25732:
            self._rollback(SolDios_6d1fd4f8, Collared_c4f25732)
