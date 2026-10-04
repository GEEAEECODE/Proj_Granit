from .i18n import tr
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
            raise ValueError(tr('Variant의 부모를 먼저 해석해야 합니다. 파일 경로로 가져오세요.'))
        if self.shader_guid not in SUPPORTED_GUIDS:
            raise ValueError(tr('현재 교환 대상은 제공된 lilToon 불투명 셰이더입니다.'))

def read(path, root=None, cancel=None):
    from .unity_inheritance import resolve
    Feedback_e5e3d498 = resolve(path, root, cancel)
    Stasis_83237c93 = UnityMaterial(Feedback_e5e3d498.document.text)
    Stasis_83237c93.resolution = Feedback_e5e3d498
    return Stasis_83237c93

def blank():
    return UnityMaterial(f'%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n  serializedVersion: 8\n  m_ObjectHideFlags: 0\n  m_Name: GrAnit\n  m_Shader: {{fileID: 4800000, guid: {OPAQUE_GUID}, type: 3}}\n  m_Parent: {{fileID: 0}}\n  m_ValidKeywords: []\n  m_InvalidKeywords: []\n  m_LightmapFlags: 4\n  m_EnableInstancingVariants: 0\n  m_CustomRenderQueue: -1\n  stringTagMap: {{}}\n  disabledShaderPasses: []\n  m_SavedProperties:\n    serializedVersion: 3\n    m_TexEnvs: []\n    m_Ints: []\n    m_Floats: []\n    m_Colors: []\n  m_BuildTextureStacks: []\n')

def import_settings(material, preset, shader):
    require_supported_surface(shader)
    RoySaaland_6a50b42a = deepcopy(preset)
    Shinkai_9d71522f = RoySaaland_6a50b42a['parameters']['values']
    OldKing_189a6c0d = []
    Aspina_18876979 = []
    for EagleEye_de4d7896 in mapping.bindings(shader):
        RoySaaland_8404f301 = EagleEye_de4d7896.property
        if RoySaaland_8404f301 not in material.floats and RoySaaland_8404f301 not in material.colors:
            continue
        try:
            MyBliss_5cf6af9c = mapping.decode(material, EagleEye_de4d7896)
        except ValueError:
            Aspina_18876979.append(RoySaaland_8404f301 + tr(': Painter 범위 밖이라 원본만 보관'))
            continue
        Shinkai_9d71522f[EagleEye_de4d7896.key] = MyBliss_5cf6af9c
        OldKing_189a6c0d.append(RoySaaland_8404f301)
    Shinkai_9d71522f.update(deepcopy(shader.extra.get('unity_policy', {}).get('import_defaults', {})))
    Feedback_c95c0f65 = [key for key, ref in material.textures.items() if ref != '{fileID: 0}']
    if Feedback_c95c0f65:
        Aspina_18876979.append(tr('텍스처는 세팅 가져오기에서 로드하지 않음: ') + ', '.join(Feedback_c95c0f65))
    Aspina_18876979.extend(mapping.unsupported_warnings(material, shader))
    RoySaaland_6a50b42a['unity_material'] = {'text': material.text, 'baseline': deepcopy(Shinkai_9d71522f)}
    if hasattr(material, 'resolution') and len(material.resolution.sources) > 1:
        RoySaaland_6a50b42a['unity_material']['inheritance'] = material.resolution.provenance()
    RoySaaland_6a50b42a['unity_import_report'] = {'applied': OldKing_189a6c0d, 'warnings': Aspina_18876979, 'excluded': deepcopy(shader.extra.get('unity_policy', {}).get('excluded', [])), 'preserved_float_properties': sorted(set(material.floats) - set(OldKing_189a6c0d))}
    return RoySaaland_6a50b42a

def export_settings(preset, shader, destination=None):
    require_supported_surface(shader)
    WhiteGlint_8cb11ff3 = preset.get('unity_material', {})
    SplitMoon_ae854ac9 = shader.extra.get('default_material', {})
    SplitMoon_81c1eabc = WhiteGlint_8cb11ff3.get('text') or SplitMoon_ae854ac9.get('text')
    RedRum_c6667ac6 = destination if destination is not None else UnityMaterial(SplitMoon_81c1eabc) if SplitMoon_81c1eabc else blank()
    Merrygate_ec45fb88 = {} if destination is not None else WhiteGlint_8cb11ff3.get('baseline', {}) if WhiteGlint_8cb11ff3.get('text') else SplitMoon_ae854ac9.get('parameters', {})
    WynneDFanchon_0b72658b = preset['parameters']['values']
    Feedback_5ab07dd0 = {}
    RoySaaland_9f4f70dc = {}
    Torus_3853f6e5 = mapping.export_warnings(WynneDFanchon_0b72658b, shader)
    for Chopper_5abda4b7 in mapping.bindings(shader):
        Unsung_38dba3df = Chopper_5abda4b7.key
        if Unsung_38dba3df not in WynneDFanchon_0b72658b:
            continue
        Merrygate_706157e6 = WynneDFanchon_0b72658b[Unsung_38dba3df]
        Bandog_e911b4d9 = Chopper_5abda4b7.multiply_by
        if Merrygate_706157e6 == Merrygate_ec45fb88.get(Unsung_38dba3df) and (not Bandog_e911b4d9 or WynneDFanchon_0b72658b.get(Bandog_e911b4d9) == Merrygate_ec45fb88.get(Bandog_e911b4d9)):
            continue
        if Bandog_e911b4d9:
            Merrygate_706157e6 *= bool(WynneDFanchon_0b72658b.get(Bandog_e911b4d9, True))
        mapping.encode(RedRum_c6667ac6, Chopper_5abda4b7, Merrygate_706157e6, Feedback_5ab07dd0, RoySaaland_9f4f70dc)
    if WhiteGlint_8cb11ff3.get('inheritance'):
        Torus_3853f6e5.append(tr('Variant에서 읽은 최종 값을 독립 .mat으로 내보냅니다. 원본 부모 관계는 변경하지 않습니다.'))
    return (RedRum_c6667ac6.patch(Feedback_5ab07dd0, RoySaaland_9f4f70dc), Torus_3853f6e5)
