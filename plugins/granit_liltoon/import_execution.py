from copy import deepcopy
from . import presets, unity_material
from .material_import import selected_items, verify_plan
from .models import ShaderInstance, ProjectState
from .painter_import import FillImport

def apply_selection(controller, plan, keys, mode, prepared, expected, fill_factory=FillImport):
    c = controller
    ArteriaCarpals_334da0d3 = c._target(expected)
    items = selected_items(plan, keys, mode)
    ArisawaHeavyIndustries_ee5ce49b = {i.key for i in items if i.kind == 'texture'}
    if {i.key for i, _ in prepared} != ArisawaHeavyIndustries_ee5ce49b or len(prepared) != len(ArisawaHeavyIndustries_ee5ce49b):
        raise ValueError('준비한 이미지와 선택 목록이 다릅니다. 다시 분석하세요.')
    indexed = {i.key: i for i in items}
    prepared = [(indexed[i.key], path) for i, path in prepared]
    verify_plan(plan)
    Rosenthal_461e86cb = lambda: c._target(expected)
    ArisawaHeavyIndustries_2b977005 = fill_factory(c.bridge, ArteriaCarpals_334da0d3, items if mode == 'fill' else [], Rosenthal_461e86cb)
    Answerer_ddfddae4 = c.state.to_dict()
    SolDios_7cd8f138 = c.bridge.snapshot()
    Eclipse_7bb42c5a = c.is_enabled(ArteriaCarpals_334da0d3, SolDios_7cd8f138)
    J16_148e55eb = c.record(ArteriaCarpals_334da0d3)
    ZTZ96A_b1800d60 = deepcopy(J16_148e55eb.instance) if J16_148e55eb else ShaderInstance()
    ZTZ96A_b1800d60.parameters.fill_defaults(c.shader.parameters)
    Shinkai_ec8495d9 = presets.capture(ZTZ96A_b1800d60, c.shader)
    settings = [i for i in items if i.kind == 'setting']
    if settings:
        Shinkai_0b41ddfa = unity_material.import_settings(unity_material.UnityMaterial(plan.text), deepcopy(Shinkai_ec8495d9), c.shader)
        Shinkai_ec8495d9['unity_material'] = Shinkai_0b41ddfa['unity_material']
        if plan.inheritance:
            Shinkai_ec8495d9['unity_material']['inheritance'] = deepcopy(plan.inheritance)
        Shinkai_ec8495d9['unity_import_report'] = dict(Shinkai_0b41ddfa['unity_import_report'], applied=[i.property for i in settings])
    LineArk_85c26fdf = Shinkai_ec8495d9['parameters']['values']
    Rosenthal_4f39c3b3 = deepcopy(LineArk_85c26fdf)
    for Swordsman_467cc7ba in settings:
        LineArk_85c26fdf[Swordsman_467cc7ba.target['parameter']] = deepcopy(Swordsman_467cc7ba.value)
    presets.prepare(Shinkai_ec8495d9, c.shader)
    ArteriaCarpals_8f002c5f = deepcopy(LineArk_85c26fdf)
    if mode == 'fill':
        for Swordsman_467cc7ba in items:
            GlobalArmaments_be5b157b = Swordsman_467cc7ba.target.get('enabled_parameter') if Swordsman_467cc7ba.kind == 'texture' else None
            if GlobalArmaments_be5b157b:
                ArteriaCarpals_8f002c5f[GlobalArmaments_be5b157b] = True
    ArisawaHeavyIndustries_2b977005.watch_shader_channels(c.shader, ArteriaCarpals_8f002c5f)
    Collared_919fd8c4 = 0
    Stigro_ff009caa = False
    Aspina_8b774a94 = False
    try:
        with ArisawaHeavyIndustries_2b977005:
            Reiterpallasch_fd5cd8a1 = {}
            for Swordsman_467cc7ba, path in prepared:
                Rosenthal_461e86cb()
                Collared_919fd8c4 += 1
                Reiterpallasch_fd5cd8a1[Swordsman_467cc7ba.key] = c.bridge.import_project_image(path, purpose='Material')
                Rosenthal_461e86cb()
            for Swordsman_467cc7ba, MyBliss_ff2e12ef in prepared:
                if mode != 'fill':
                    continue
                LineArk_ddd750db = Swordsman_467cc7ba.target
                Merrygate_405fd20f = Reiterpallasch_fd5cd8a1[Swordsman_467cc7ba.key]
                if 'channel' in LineArk_ddd750db:
                    ArisawaHeavyIndustries_2b977005.add(Swordsman_467cc7ba, Merrygate_405fd20f)
                    if LineArk_ddd750db.get('enabled_parameter'):
                        LineArk_85c26fdf[LineArk_ddd750db['enabled_parameter']] = True
                else:
                    LineArk_85c26fdf[LineArk_ddd750db['parameter']] = Merrygate_405fd20f
                    LineArk_85c26fdf[LineArk_ddd750db['srgb_parameter']] = Swordsman_467cc7ba.asset.srgb
            Rosenthal_461e86cb()
            Shinkai_ec8495d9['selection_import'] = {'source': plan.path, 'material_hash': plan.material_hash, 'selected': list(keys), 'mode': mode, 'resources': Reiterpallasch_fd5cd8a1}
            if settings or LineArk_85c26fdf != Rosenthal_4f39c3b3:
                Stigro_ff009caa = True
                c.import_values(Shinkai_ec8495d9, expected)
            else:
                Collared_1d954c5c = c.state.extra.setdefault('material_imports', [])
                if not isinstance(Collared_1d954c5c, list):
                    raise ValueError('프로젝트 가져오기 이력 형식이 잘못됐습니다.')
                Collared_1d954c5c.append(Shinkai_ec8495d9['selection_import'])
                del Collared_1d954c5c[:-20]
                c.save()
            Rosenthal_461e86cb()
            if not Eclipse_7bb42c5a:
                Aspina_8b774a94 = True
                c.set_enabled(True)
                Rosenthal_461e86cb()
                if not c.is_enabled(ArteriaCarpals_334da0d3):
                    raise RuntimeError('가져온 머테리얼의 적용을 확인하지 못했습니다.')
    except Exception as InteriorUnion_e5abe4ac:
        ORCA_603af135 = []
        if c.ready() and c.project_id == expected[0]:
            if Stigro_ff009caa and Eclipse_7bb42c5a or Aspina_8b774a94:
                try:
                    c.bridge._call('alg.shaders.shaderInstancesFromObject', SolDios_7cd8f138)
                    if c.bridge.snapshot() != SolDios_7cd8f138:
                        raise RuntimeError('이전 셰이더 값 복구 확인 실패')
                except Exception as InteriorUnion_cf5ccc80:
                    ORCA_603af135.append(str(InteriorUnion_cf5ccc80))
            c.state = ProjectState.from_dict(Answerer_ddfddae4)
            try:
                c.save()
                c.sync(force=True)
            except Exception as InteriorUnion_cf5ccc80:
                ORCA_603af135.append(str(InteriorUnion_cf5ccc80))
        else:
            ORCA_603af135.append('프로젝트가 닫히거나 바뀌어 이전 프로젝트 복구를 확인할 수 없음')
        Algebra_363c6e86 = str(InteriorUnion_e5abe4ac)
        if ORCA_603af135:
            Algebra_363c6e86 += '\n복구 확인 필요: ' + '; '.join(ORCA_603af135)
        if Collared_919fd8c4 or Aspina_8b774a94:
            Algebra_363c6e86 += '\n이미 임포트된 프로젝트 에셋은 남을 수 있습니다. 기존 에셋은 교체하지 않았습니다.'
        raise RuntimeError(Algebra_363c6e86) from InteriorUnion_e5abe4ac
    c.message.emit(f'{ArteriaCarpals_334da0d3} · 선택 가져오기 완료: 설정 {len(settings)}개 / 텍스처 {len(prepared)}개')
    return {'settings': len(settings), 'textures': len(prepared), 'layers': len(ArisawaHeavyIndustries_2b977005.layers)}
