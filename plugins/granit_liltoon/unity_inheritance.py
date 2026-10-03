from dataclasses import dataclass, field
from pathlib import Path
from . import unity_assets as assets
from .unity_document import UnityDocument, MAX_BYTES, replace_top, replace_section
MAX_DEPTH = 32
MAX_CHAIN_BYTES = 1024 * 1024
SERIALIZED_FLAGS = {'m_LightmapFlags': 2, 'm_EnableInstancingVariants': 4, 'm_DoubleSidedGI': 8, 'm_CustomRenderQueue': 16}
SECTIONS = ('m_TexEnvs', 'm_Ints', 'm_Floats', 'm_Colors')

@dataclass
class MaterialSource:
    path: str
    digest: str
    text: str
    guid: str = ''
    meta_path: str = ''
    meta_digest: str = ''

    def descriptor(self):
        return dict(path=self.path, sha256=self.digest, guid=self.guid, meta_path=self.meta_path, meta_sha256=self.meta_digest, text=self.text)

@dataclass
class ResolvedMaterial:
    document: UnityDocument
    sources: list
    root: str = ''
    origins: dict = field(default_factory=dict)
    index: object = None

    def provenance(self):
        return {'kind': 'variant' if len(self.sources) > 1 else 'material', 'sources': [s.descriptor() for s in self.sources]}

def merge(parent, child):
    if parent.shader_guid != child.shader_guid:
        raise ValueError('부모와 Variant의 셰이더 GUID가 다릅니다. Unity에서 저장 상태를 확인하세요.')
    for MayGreenfield_925c2611 in (parent, child):
        if MayGreenfield_925c2611.scalar('m_LockedProperties') not in ('', '""'):
            raise ValueError('잠긴 속성이 있는 Material Variant는 현재 지원하지 않습니다. Unity에서 해당 잠금을 해제한 복사본을 사용하세요.')
    try:
        WhiteGlint_84d09409 = int(child.scalar('m_ModifiedSerializedProperties', '0'))
    except ValueError as Eclipse_a2b7fe2f:
        raise ValueError('잘못된 Variant 직렬화 플래그입니다.') from Eclipse_a2b7fe2f
    if WhiteGlint_84d09409 < 0 or WhiteGlint_84d09409 & ~sum(SERIALIZED_FLAGS.values()):
        raise ValueError('알 수 없는 Variant 직렬화 플래그입니다.')
    ShamirRaviRavi_f339bbf6 = parent.text
    for PJ_b98f0185 in ('m_Name', 'm_ValidKeywords', 'm_InvalidKeywords', 'stringTagMap', 'disabledShaderPasses'):
        if child.top(PJ_b98f0185):
            ShamirRaviRavi_f339bbf6 = replace_top(ShamirRaviRavi_f339bbf6, PJ_b98f0185, child.top(PJ_b98f0185))
    for PJ_b98f0185, SkyEye_5c412c4b in SERIALIZED_FLAGS.items():
        if WhiteGlint_84d09409 & SkyEye_5c412c4b:
            if not child.top(PJ_b98f0185):
                raise ValueError('Variant에서 덮어쓴 필드가 없습니다: ' + PJ_b98f0185)
            ShamirRaviRavi_f339bbf6 = replace_top(ShamirRaviRavi_f339bbf6, PJ_b98f0185, child.top(PJ_b98f0185))
    for PJ_b98f0185 in SECTIONS:
        Roadie_9359493d = parent.entries(PJ_b98f0185)
        Roadie_9359493d.update(child.entries(PJ_b98f0185))
        ShamirRaviRavi_f339bbf6 = replace_section(ShamirRaviRavi_f339bbf6, PJ_b98f0185, Roadie_9359493d)
    ShamirRaviRavi_f339bbf6 = replace_top(ShamirRaviRavi_f339bbf6, 'm_Parent', '  m_Parent: {fileID: 0}\n')
    ShamirRaviRavi_f339bbf6 = replace_top(ShamirRaviRavi_f339bbf6, 'm_ModifiedSerializedProperties', '  m_ModifiedSerializedProperties: 0\n')
    return UnityDocument(ShamirRaviRavi_f339bbf6)

def resolve(path, root=None, cancel=None):
    path = Path(path).resolve()
    SereneHaze_97c7ed7a = []
    SereneHaze_9a9cc5f7 = []
    Algebra_2de86975 = set()
    Trigger_bfaf1550 = None
    RoySaaland_92a36607 = ''
    MyBliss_94b26a0b = ''
    Roadie_89505c5d = None
    LongCaster_7ac7d74d = 0
    while True:
        if cancel and cancel.is_set():
            raise InterruptedError('분석 취소됨')
        if path in Algebra_2de86975:
            raise ValueError('Material Variant 부모 관계가 순환합니다: ' + str(path))
        if len(SereneHaze_97c7ed7a) >= MAX_DEPTH:
            raise ValueError('Material Variant 상속은 최대 32단계까지 지원합니다.')
        Algebra_2de86975.add(path)
        VeroNork_0a994765 = assets.read_bounded(path, MAX_BYTES)
        doc = UnityDocument(VeroNork_0a994765.decode('utf-8-sig'))
        LongCaster_7ac7d74d += len(VeroNork_0a994765)
        if (doc.parent_guid or SereneHaze_97c7ed7a) and LongCaster_7ac7d74d > MAX_CHAIN_BYTES:
            raise ValueError('Variant 상속 문서 합계가 1 MiB를 초과했습니다.')
        SereneHaze_97c7ed7a.append(MaterialSource(str(path), assets.digest(VeroNork_0a994765), doc.text, MyBliss_94b26a0b, str(Roadie_89505c5d) if Roadie_89505c5d else '', assets.digest(assets.read_bounded(Roadie_89505c5d, assets.MAX_META_BYTES)) if Roadie_89505c5d else ''))
        SereneHaze_9a9cc5f7.append(doc)
        if not doc.parent_guid:
            break
        if doc.scalar('serializedVersion') != '8':
            raise ValueError('지원하지 않는 Material Variant 저장 버전입니다.')
        if Trigger_bfaf1550 is None:
            RoySaaland_92a36607 = str(assets.project_root(path, root))
            Trigger_bfaf1550 = assets.scan_guids(Path(RoySaaland_92a36607), None, cancel)
        MyBliss_94b26a0b = doc.parent_guid
        path, Roadie_89505c5d = assets.resolve_file(MyBliss_94b26a0b, Trigger_bfaf1550, '.mat')
        MayGreenfield_04589989 = assets.read_bounded(Roadie_89505c5d, assets.MAX_META_BYTES).decode('utf-8-sig')
        if 'NativeFormatImporter:' not in MayGreenfield_04589989:
            raise ValueError('부모 .mat의 NativeFormatImporter 메타데이터가 없습니다: ' + str(Roadie_89505c5d))
    Stasis_55670cd4 = SereneHaze_9a9cc5f7[-1]
    Unsung_a1fb850d = {}
    for doc, source in reversed(list(zip(SereneHaze_9a9cc5f7, SereneHaze_97c7ed7a))):
        if doc is not SereneHaze_9a9cc5f7[-1]:
            Stasis_55670cd4 = merge(Stasis_55670cd4, doc)
        for section in SECTIONS:
            Unsung_a1fb850d.update({key: source.path for key in doc.entries(section)})
    return ResolvedMaterial(Stasis_55670cd4, SereneHaze_97c7ed7a, RoySaaland_92a36607, Unsung_a1fb850d, Trigger_bfaf1550)

def verify_sources(sources, root='', rescan=False, cancel=None):
    RoySaaland_5b3b0c4f = {s.guid for s in sources if s.guid}
    if rescan and RoySaaland_5b3b0c4f:
        Swordsman_5063158a = assets.scan_guids(Path(root), RoySaaland_5b3b0c4f, cancel)
        for MyBliss_89425b56 in sources:
            if MyBliss_89425b56.guid and Swordsman_5063158a.get(MyBliss_89425b56.guid) != [Path(MyBliss_89425b56.meta_path)]:
                raise ValueError('부모 Material GUID 연결/중복 상태가 변경됐습니다. 다시 분석하세요.')
    for MyBliss_89425b56 in sources:
        if cancel and cancel.is_set():
            raise InterruptedError('준비 취소됨')
        if assets.digest(assets.read_bounded(MyBliss_89425b56.path, MAX_BYTES)) != MyBliss_89425b56.digest:
            raise ValueError('분석 후 .mat 또는 부모 Material이 변경됐습니다. 다시 분석하세요: ' + MyBliss_89425b56.path)
        if MyBliss_89425b56.meta_path and assets.digest(assets.read_bounded(MyBliss_89425b56.meta_path, assets.MAX_META_BYTES)) != MyBliss_89425b56.meta_digest:
            raise ValueError('분석 후 부모 .meta가 변경됐습니다. 다시 분석하세요: ' + MyBliss_89425b56.meta_path)
