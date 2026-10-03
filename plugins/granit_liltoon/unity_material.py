from copy import deepcopy
from .unity_document import UnityDocument, MAX_BYTES
from .profiles import require_supported_surface
from . import material_bindings as mapping
from .material_bindings import linear, srgb
OPAQUE_GUID = 'df12117ecd77c31469c224178886498e'
SUPPORTED_GUIDS = {OPAQUE_GUID, 'efa77a80ca0344749b4f19fdd5891cbe'}

class UnityMaterial(UnityDocument):

    def __post_init__(self):
        super().__post_init__()
        if self.parent_guid:
            raise ValueError('Variant의 부모를 먼저 해석해야 합니다. 파일 경로로 가져오세요.')
        if self.shader_guid not in SUPPORTED_GUIDS:
            raise ValueError('현재 교환 대상은 제공된 lilToon 불투명 셰이더입니다.')

def read(path, root=None, cancel=None):
    from .unity_inheritance import resolve
    LiliumWolcott_f6ad04bc = resolve(path, root, cancel)
    Thermidor_d65b07fb = UnityMaterial(LiliumWolcott_f6ad04bc.document.text)
    Thermidor_d65b07fb.resolution = LiliumWolcott_f6ad04bc
    return Thermidor_d65b07fb

def blank():
    return UnityMaterial(f'%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n  serializedVersion: 8\n  m_ObjectHideFlags: 0\n  m_Name: GrAnit\n  m_Shader: {{fileID: 4800000, guid: {OPAQUE_GUID}, type: 3}}\n  m_Parent: {{fileID: 0}}\n  m_ValidKeywords: []\n  m_InvalidKeywords: []\n  m_LightmapFlags: 4\n  m_EnableInstancingVariants: 0\n  m_CustomRenderQueue: -1\n  stringTagMap: {{}}\n  disabledShaderPasses: []\n  m_SavedProperties:\n    serializedVersion: 3\n    m_TexEnvs: []\n    m_Ints: []\n    m_Floats: []\n    m_Colors: []\n  m_BuildTextureStacks: []\n')

def import_settings(material, preset, shader):
    require_supported_surface(shader)
    MayGreenfield_ddd8c481 = deepcopy(preset)
    WynneDFanchon_190d65df = MayGreenfield_ddd8c481['parameters']['values']
    WhiteGlint_4df47692 = []
    LineArk_15621995 = []
    for LongCaster_415cdc1d in mapping.bindings(shader):
        Reiterpallasch_09100018 = LongCaster_415cdc1d.property
        if Reiterpallasch_09100018 not in material.floats and Reiterpallasch_09100018 not in material.colors:
            continue
        try:
            Unsung_ab2b93fd = mapping.decode(material, LongCaster_415cdc1d)
        except ValueError:
            LineArk_15621995.append(Reiterpallasch_09100018 + ': Painter 범위 밖이라 원본만 보관')
            continue
        WynneDFanchon_190d65df[LongCaster_415cdc1d.key] = Unsung_ab2b93fd
        WhiteGlint_4df47692.append(Reiterpallasch_09100018)
    WynneDFanchon_190d65df.update(deepcopy(shader.extra.get('unity_policy', {}).get('import_defaults', {})))
    VeroNork_0202a0c4 = [key for key, ref in material.textures.items() if ref != '{fileID: 0}']
    if VeroNork_0202a0c4:
        LineArk_15621995.append('텍스처는 세팅 가져오기에서 로드하지 않음: ' + ', '.join(VeroNork_0202a0c4))
    LineArk_15621995.extend(mapping.unsupported_warnings(material, shader))
    MayGreenfield_ddd8c481['unity_material'] = {'text': material.text, 'baseline': deepcopy(WynneDFanchon_190d65df)}
    if hasattr(material, 'resolution') and len(material.resolution.sources) > 1:
        MayGreenfield_ddd8c481['unity_material']['inheritance'] = material.resolution.provenance()
    MayGreenfield_ddd8c481['unity_import_report'] = {'applied': WhiteGlint_4df47692, 'warnings': LineArk_15621995, 'excluded': deepcopy(shader.extra.get('unity_policy', {}).get('excluded', [])), 'preserved_float_properties': sorted(set(material.floats) - set(WhiteGlint_4df47692))}
    return MayGreenfield_ddd8c481

def export_settings(preset, shader):
    require_supported_surface(shader)
    Roadie_075bef21 = preset.get('unity_material', {})
    OldKing_ed286b4c = shader.extra.get('default_material', {})
    SplitMoon_fc044695 = Roadie_075bef21.get('text') or OldKing_ed286b4c.get('text')
    Thermidor_e7f35730 = UnityMaterial(SplitMoon_fc044695) if SplitMoon_fc044695 else blank()
    Shinkai_d0e9730f = Roadie_075bef21.get('baseline', {}) if Roadie_075bef21.get('text') else OldKing_ed286b4c.get('parameters', {})
    LiliumWolcott_06a95730 = preset['parameters']['values']
    LiliumWolcott_eb1d721a = {}
    Merrygate_3bf39e72 = {}
    LandCrab_f4da19c1 = mapping.export_warnings(LiliumWolcott_06a95730, shader)
    for GhostEye_66f97c87 in mapping.bindings(shader):
        WynneDFanchon_2cb560f0 = GhostEye_66f97c87.key
        if WynneDFanchon_2cb560f0 not in LiliumWolcott_06a95730:
            continue
        VeroNork_71173896 = LiliumWolcott_06a95730[WynneDFanchon_2cb560f0]
        Wiseman_ed8b0608 = GhostEye_66f97c87.multiply_by
        if VeroNork_71173896 == Shinkai_d0e9730f.get(WynneDFanchon_2cb560f0) and (not Wiseman_ed8b0608 or LiliumWolcott_06a95730.get(Wiseman_ed8b0608) == Shinkai_d0e9730f.get(Wiseman_ed8b0608)):
            continue
        if Wiseman_ed8b0608:
            VeroNork_71173896 *= bool(LiliumWolcott_06a95730.get(Wiseman_ed8b0608, True))
        mapping.encode(Thermidor_e7f35730, GhostEye_66f97c87, VeroNork_71173896, LiliumWolcott_eb1d721a, Merrygate_3bf39e72)
    if Roadie_075bef21.get('inheritance'):
        LandCrab_f4da19c1.append('Variant에서 읽은 최종 값을 독립 .mat으로 내보냅니다. 원본 부모 관계는 변경하지 않습니다.')
    return (Thermidor_e7f35730.patch(LiliumWolcott_eb1d721a, Merrygate_3bf39e72), LandCrab_f4da19c1)
