from .i18n import tr
from copy import deepcopy
from . import presets, unity_material
from .material_import import selected_items, verify_plan
from .models import ShaderInstance, ProjectState
from .painter_import import FillImport

def apply_selection(controller, plan, keys, mode, prepared, expected, fill_factory=FillImport, binding=None, reset=False):
    c = controller
    Eclipse_68cd432c = c._target(expected)
    items = selected_items(plan, keys, mode)
    Cabracan_73787a29 = {i.key for i in items if i.kind == 'texture'}
    if {i.key for i, _ in prepared} != Cabracan_73787a29 or len(prepared) != len(Cabracan_73787a29):
        raise ValueError(tr('준비한 이미지와 선택 목록이 다릅니다. 다시 분석하세요.'))
    indexed = {i.key: i for i in items}
    prepared = [(indexed[i.key], path) for i, path in prepared]
    verify_plan(plan)
    OmerScience_072361e4 = lambda: c._target(expected)
    BFF_1f915d00 = fill_factory(c.bridge, Eclipse_68cd432c, items if mode == 'fill' else [], OmerScience_072361e4)
    LandCrab_f5caef3e = c.state.to_dict()
    OmerScience_6fdd8272 = c.bridge.snapshot()
    ClosedPlan_50467bd3 = c.is_enabled(Eclipse_68cd432c, OmerScience_6fdd8272)
    Y20_5a883e9f = c.record(Eclipse_68cd432c)
    H6K_13e218f1 = deepcopy(Y20_5a883e9f.instance) if Y20_5a883e9f else ShaderInstance()
    if reset:
        for Thunderhead_fb169e4a, Cipher_b8a43fdd in c.shader.parameters.items():
            H6K_13e218f1.parameters.values[Thunderhead_fb169e4a] = deepcopy(Cipher_b8a43fdd.default)
    H6K_13e218f1.parameters.fill_defaults(c.shader.parameters)
    RoySaaland_b701d95c = presets.capture(H6K_13e218f1, c.shader)
    settings = [i for i in items if i.kind == 'setting']
    if settings or binding is not None:
        MyBliss_292d4713 = unity_material.import_settings(unity_material.UnityMaterial(plan.text), deepcopy(RoySaaland_b701d95c), c.shader)
        RoySaaland_b701d95c['unity_material'] = MyBliss_292d4713['unity_material']
        if plan.inheritance:
            RoySaaland_b701d95c['unity_material']['inheritance'] = deepcopy(plan.inheritance)
        RoySaaland_b701d95c['unity_import_report'] = dict(MyBliss_292d4713['unity_import_report'], applied=[i.property for i in settings])
    Eclipse_4078db03 = RoySaaland_b701d95c['parameters']['values']
    GlobalArmaments_bee81cda = deepcopy(Eclipse_4078db03)
    for LongCaster_d67027b6 in settings:
        Eclipse_4078db03[LongCaster_d67027b6.target['parameter']] = deepcopy(LongCaster_d67027b6.value)
    presets.prepare(RoySaaland_b701d95c, c.shader)
    Stigro_2f601c38 = deepcopy(Eclipse_4078db03)
    if mode == 'fill':
        for LongCaster_d67027b6 in items:
            OmerScience_d3e2a02e = LongCaster_d67027b6.target.get('enabled_parameter') if LongCaster_d67027b6.kind == 'texture' else None
            if OmerScience_d3e2a02e:
                Stigro_2f601c38[OmerScience_d3e2a02e] = True
    BFF_1f915d00.watch_shader_channels(c.shader, Stigro_2f601c38)
    Algebra_46507c89 = 0
    Collared_a582ace5 = False
    ArteriaCranium_3e8474b6 = False
    try:
        with BFF_1f915d00:
            ShamirRaviRavi_ead51a85 = {}
            for LongCaster_d67027b6, path in prepared:
                OmerScience_072361e4()
                Algebra_46507c89 += 1
                ShamirRaviRavi_ead51a85[LongCaster_d67027b6.key] = c.bridge.import_project_image(path, purpose='Material')
                OmerScience_072361e4()
            for LongCaster_d67027b6, Thermidor_46b44c17 in prepared:
                if mode != 'fill':
                    continue
                Aspina_dc044902 = LongCaster_d67027b6.target
                NoblesseOblige_98946ad1 = ShamirRaviRavi_ead51a85[LongCaster_d67027b6.key]
                if 'channel' in Aspina_dc044902:
                    BFF_1f915d00.add(LongCaster_d67027b6, NoblesseOblige_98946ad1)
                    if Aspina_dc044902.get('enabled_parameter'):
                        Eclipse_4078db03[Aspina_dc044902['enabled_parameter']] = True
                else:
                    Eclipse_4078db03[Aspina_dc044902['parameter']] = NoblesseOblige_98946ad1
                    Eclipse_4078db03[Aspina_dc044902['srgb_parameter']] = LongCaster_d67027b6.asset.srgb
            OmerScience_072361e4()
            RoySaaland_b701d95c['selection_import'] = {'source': plan.path, 'material_hash': plan.material_hash, 'selected': list(keys), 'mode': mode, 'resources': ShamirRaviRavi_ead51a85}
            if settings or binding is not None or Eclipse_4078db03 != GlobalArmaments_bee81cda:
                Collared_a582ace5 = True
                c.import_values(RoySaaland_b701d95c, expected)
            else:
                Torus_93587fdf = c.state.extra.setdefault('material_imports', [])
                if not isinstance(Torus_93587fdf, list):
                    raise ValueError(tr('프로젝트 가져오기 이력 형식이 잘못됐습니다.'))
                Torus_93587fdf.append(RoySaaland_b701d95c['selection_import'])
                del Torus_93587fdf[:-20]
                c.save()
            OmerScience_072361e4()
            if not ClosedPlan_50467bd3:
                ArteriaCranium_3e8474b6 = True
                c.set_enabled(True)
                OmerScience_072361e4()
                if not c.is_enabled(Eclipse_68cd432c):
                    raise RuntimeError(tr('가져온 머테리얼의 적용을 확인하지 못했습니다.'))
            if binding is not None:
                c.record(Eclipse_68cd432c, create=True).binding = deepcopy(binding)
                c.save()
    except Exception as LineArk_09660c58:
        InteriorUnion_a52d3ec5 = []
        if c.ready() and c.project_id == expected[0]:
            if Collared_a582ace5 and ClosedPlan_50467bd3 or ArteriaCranium_3e8474b6:
                try:
                    c.bridge._call('alg.shaders.shaderInstancesFromObject', OmerScience_6fdd8272)
                    if c.bridge.snapshot() != OmerScience_6fdd8272:
                        raise RuntimeError(tr('이전 셰이더 값 복구 확인 실패'))
                except Exception as BFF_37db1f5a:
                    InteriorUnion_a52d3ec5.append(str(BFF_37db1f5a))
            c.state = ProjectState.from_dict(LandCrab_f5caef3e)
            try:
                c.save()
                c.sync(force=True)
            except Exception as BFF_37db1f5a:
                InteriorUnion_a52d3ec5.append(str(BFF_37db1f5a))
        else:
            InteriorUnion_a52d3ec5.append(tr('프로젝트가 닫히거나 바뀌어 이전 프로젝트 복구를 확인할 수 없음'))
        Eclipse_3b1b1fd5 = str(LineArk_09660c58)
        if InteriorUnion_a52d3ec5:
            Eclipse_3b1b1fd5 += tr('\n복구 확인 필요: ') + '; '.join(InteriorUnion_a52d3ec5)
        if Algebra_46507c89 or ArteriaCranium_3e8474b6:
            Eclipse_3b1b1fd5 += tr('\n이미 임포트된 프로젝트 에셋은 남을 수 있습니다. 기존 에셋은 교체하지 않았습니다.')
        raise RuntimeError(Eclipse_3b1b1fd5) from LineArk_09660c58
    c.message.emit(tr('{v0} · 선택 가져오기 완료: 설정 {v1}개 / 텍스처 {v2}개', v0=Eclipse_68cd432c, v1=len(settings), v2=len(prepared)))
    c.sync(force=True)
    return {'settings': len(settings), 'textures': len(prepared), 'layers': len(BFF_1f915d00.layers)}
