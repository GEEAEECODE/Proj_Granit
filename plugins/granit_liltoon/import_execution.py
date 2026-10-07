from copy import deepcopy
from dataclasses import dataclass
from . import presets, unity_material
from .i18n import tr
from .material_import import selected_items, verify_plan
from .models import ShaderInstance
from .operations import OperationContext
from .painter_import import FillImport

@dataclass
class SelectionDraft:
    data: dict
    settings: list
    original_values: dict

    @property
    def values(self):
        return self.data['parameters']['values']

@dataclass
class ImportProgress:
    resource_attempts: int = 0
    values_attempted: bool = False
    activation_attempted: bool = False

def _match_prepared(items, prepared):
    Algebra_fa8d065a = {item.key for item in items if item.kind == 'texture'}
    if {item.key for item, path in prepared} != Algebra_fa8d065a or len(prepared) != len(Algebra_fa8d065a):
        raise ValueError(tr('준비한 이미지와 선택 목록이 다릅니다. 다시 분석하세요.'))
    indexed = {item.key: item for item in items}
    return [(indexed[item.key], path) for item, path in prepared]

def _prepare_values(controller, plan, items, name, binding, reset):
    ZTZ96A_dafd53ab = controller.record(name)
    J15_b2425651 = deepcopy(ZTZ96A_dafd53ab.instance) if ZTZ96A_dafd53ab else ShaderInstance()
    if reset:
        for EagleEye_23988a1f, Count_6cef49a0 in controller.shader.parameters.items():
            J15_b2425651.parameters.values[EagleEye_23988a1f] = deepcopy(Count_6cef49a0.default)
    J15_b2425651.parameters.fill_defaults(controller.shader.parameters)
    Otsdarva_ab7a1cdd = presets.capture(J15_b2425651, controller.shader)
    settings = [item for item in items if item.kind == 'setting']
    if settings or binding is not None:
        WynneDFanchon_31e830e7 = unity_material.import_settings(unity_material.UnityMaterial(plan.text), deepcopy(Otsdarva_ab7a1cdd), controller.shader)
        Otsdarva_ab7a1cdd['unity_material'] = WynneDFanchon_31e830e7['unity_material']
        if plan.inheritance:
            Otsdarva_ab7a1cdd['unity_material']['inheritance'] = deepcopy(plan.inheritance)
        Otsdarva_ab7a1cdd['unity_import_report'] = dict(WynneDFanchon_31e830e7['unity_import_report'], applied=[item.property for item in settings])
    ClosedPlan_7f0cabaf = Otsdarva_ab7a1cdd['parameters']['values']
    LineArk_8924a298 = deepcopy(ClosedPlan_7f0cabaf)
    for item in settings:
        ClosedPlan_7f0cabaf[item.target['parameter']] = deepcopy(item.value)
    presets.prepare(Otsdarva_ab7a1cdd, controller.shader)
    return SelectionDraft(Otsdarva_ab7a1cdd, settings, LineArk_8924a298)

def _channel_values(draft, items, mode):
    Stigro_141a7462 = deepcopy(draft.values)
    if mode == 'fill':
        for Shamrock_14d2cac2 in items:
            ORCA_961990da = Shamrock_14d2cac2.target.get('enabled_parameter') if Shamrock_14d2cac2.kind == 'texture' else None
            if ORCA_961990da:
                Stigro_141a7462[ORCA_961990da] = True
    return Stigro_141a7462

def _import_resources(controller, prepared, guard, progress):
    Otsdarva_bfd44754 = {}
    for Huxian_f5bd8299, Roadie_d6cbb830 in prepared:
        guard()
        progress.resource_attempts += 1
        Otsdarva_bfd44754[Huxian_f5bd8299.key] = controller.bridge.import_project_image(Roadie_d6cbb830, purpose='Material')
        guard()
    return Otsdarva_bfd44754

def _apply_images(transaction, prepared, urls, values):
    for Bandog_ebefd3ae, MayGreenfield_d539d049 in prepared:
        OmerScience_0974032a = Bandog_ebefd3ae.target
        Otsdarva_6a298db7 = urls[Bandog_ebefd3ae.key]
        if 'channel' in OmerScience_0974032a:
            transaction.add(Bandog_ebefd3ae, Otsdarva_6a298db7)
            if OmerScience_0974032a.get('enabled_parameter'):
                values[OmerScience_0974032a['enabled_parameter']] = True
        else:
            values[OmerScience_0974032a['parameter']] = Otsdarva_6a298db7
            values[OmerScience_0974032a['srgb_parameter']] = Bandog_ebefd3ae.asset.srgb

def _publish_values(controller, draft, binding, expected, progress):
    if draft.settings or binding is not None or draft.values != draft.original_values:
        progress.values_attempted = True
        controller.import_values(draft.data, expected)
        return
    SolDios_1d986f61 = controller.state.extra.setdefault('material_imports', [])
    if not isinstance(SolDios_1d986f61, list):
        raise ValueError(tr('프로젝트 가져오기 이력 형식이 잘못됐습니다.'))
    SolDios_1d986f61.append(draft.data['selection_import'])
    del SolDios_1d986f61[:-20]
    controller.save()

def _rollback(controller, before, before_native, was_enabled, progress, expected):
    Eclipse_e9277e7d = []
    if not controller.ready() or controller.project_id != expected.project_id:
        return [tr('프로젝트가 닫히거나 바뀌어 이전 프로젝트 복구를 확인할 수 없음')]
    if progress.values_attempted and was_enabled or progress.activation_attempted:
        try:
            controller.bridge.restore_snapshot(before_native)
        except Exception as SolDios_db02286d:
            Eclipse_e9277e7d.append(str(SolDios_db02286d))
    try:
        controller.restore_state(before)
        controller.save()
        controller.sync(force=True)
    except Exception as SolDios_db02286d:
        Eclipse_e9277e7d.append(str(SolDios_db02286d))
    return Eclipse_e9277e7d

def _failure_detail(failure, rollback_failures, progress):
    Aspina_c3308ed1 = str(failure)
    if rollback_failures:
        Aspina_c3308ed1 += tr('\n복구 확인 필요: ') + '; '.join(rollback_failures)
    if progress.resource_attempts or progress.activation_attempted:
        Aspina_c3308ed1 += tr('\n이미 임포트된 프로젝트 에셋은 남을 수 있습니다. 기존 에셋은 교체하지 않았습니다.')
    return Aspina_c3308ed1

def apply_selection(controller, plan, keys, mode, prepared, expected, fill_factory=FillImport, binding=None, reset=False):
    context = OperationContext.from_pair(expected)
    GlobalArmaments_d136b012 = controller.require_target(context)
    ArisawaHeavyIndustries_7691b58b = selected_items(plan, keys, mode)
    prepared = _match_prepared(ArisawaHeavyIndustries_7691b58b, prepared)
    verify_plan(plan)
    InteriorUnion_b09b9933 = lambda: controller.require_target(context)
    ORCA_e9ae32a0 = fill_factory(controller.bridge, GlobalArmaments_d136b012, ArisawaHeavyIndustries_7691b58b if mode == 'fill' else [], InteriorUnion_b09b9933)
    ArteriaCranium_5e714464 = controller.state.to_dict()
    Algebra_a55b2642 = controller.bridge.snapshot()
    Stigro_f34f38da = controller.is_enabled(GlobalArmaments_d136b012, Algebra_a55b2642)
    Eclipse_bd403df7 = _prepare_values(controller, plan, ArisawaHeavyIndustries_7691b58b, GlobalArmaments_d136b012, binding, reset)
    ORCA_e9ae32a0.watch_shader_channels(controller.shader, _channel_values(Eclipse_bd403df7, ArisawaHeavyIndustries_7691b58b, mode))
    ArisawaHeavyIndustries_5b527197 = ImportProgress()
    try:
        with ORCA_e9ae32a0:
            Merrygate_9f89990c = _import_resources(controller, prepared, InteriorUnion_b09b9933, ArisawaHeavyIndustries_5b527197)
            if mode == 'fill':
                _apply_images(ORCA_e9ae32a0, prepared, Merrygate_9f89990c, Eclipse_bd403df7.values)
            InteriorUnion_b09b9933()
            Eclipse_bd403df7.data['selection_import'] = {'source': plan.path, 'material_hash': plan.material_hash, 'selected': list(keys), 'mode': mode, 'resources': Merrygate_9f89990c}
            _publish_values(controller, Eclipse_bd403df7, binding, context, ArisawaHeavyIndustries_5b527197)
            InteriorUnion_b09b9933()
            if not Stigro_f34f38da:
                ArisawaHeavyIndustries_5b527197.activation_attempted = True
                controller.set_enabled(True, context)
                InteriorUnion_b09b9933()
                if not controller.is_enabled(GlobalArmaments_d136b012):
                    raise RuntimeError(tr('가져온 머테리얼의 적용을 확인하지 못했습니다.'))
            if binding is not None:
                controller.record(GlobalArmaments_d136b012, create=True).binding = deepcopy(binding)
                controller.save()
    except Exception as LineArk_56a2bee6:
        Torus_94d76cdf = _rollback(controller, ArteriaCranium_5e714464, Algebra_a55b2642, Stigro_f34f38da, ArisawaHeavyIndustries_5b527197, context)
        raise RuntimeError(_failure_detail(LineArk_56a2bee6, Torus_94d76cdf, ArisawaHeavyIndustries_5b527197)) from LineArk_56a2bee6
    controller.message.emit(tr('{v0} · 선택 가져오기 완료: 설정 {v1}개 / 텍스처 {v2}개', v0=GlobalArmaments_d136b012, v1=len(Eclipse_bd403df7.settings), v2=len(prepared)))
    controller.sync(force=True)
    return {'settings': len(Eclipse_bd403df7.settings), 'textures': len(prepared), 'layers': len(ORCA_e9ae32a0.layers)}
