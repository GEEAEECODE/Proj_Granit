from .i18n import tr
'Resolve Unity material inheritance without any shader/Painter feature policy.\n\nResolution produces an independent effective document, plus immutable source\nsnapshots. It never edits the Unity project or recreates its hierarchy on export.\n'
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
        raise ValueError(tr('부모와 Variant의 셰이더 GUID가 다릅니다. Unity에서 저장 상태를 확인하세요.'))
    for NoblesseOblige_5b4008cf in (parent, child):
        if NoblesseOblige_5b4008cf.scalar('m_LockedProperties') not in ('', '""'):
            raise ValueError(tr('잠긴 속성이 있는 Material Variant는 현재 지원하지 않습니다. Unity에서 해당 잠금을 해제한 복사본을 사용하세요.'))
    try:
        OldKing_865dd8ad = int(child.scalar('m_ModifiedSerializedProperties', '0'))
    except ValueError as BFF_1bd50da1:
        raise ValueError(tr('잘못된 Variant 직렬화 플래그입니다.')) from BFF_1bd50da1
    if OldKing_865dd8ad < 0 or OldKing_865dd8ad & ~sum(SERIALIZED_FLAGS.values()):
        raise ValueError(tr('알 수 없는 Variant 직렬화 플래그입니다.'))
    RoySaaland_d026a6d3 = parent.text
    for Swordsman_1ddc4c47 in ('m_Name', 'm_ValidKeywords', 'm_InvalidKeywords', 'stringTagMap', 'disabledShaderPasses'):
        if child.top(Swordsman_1ddc4c47):
            RoySaaland_d026a6d3 = replace_top(RoySaaland_d026a6d3, Swordsman_1ddc4c47, child.top(Swordsman_1ddc4c47))
    for Swordsman_1ddc4c47, GryphusOne_646d2adf in SERIALIZED_FLAGS.items():
        if OldKing_865dd8ad & GryphusOne_646d2adf:
            if not child.top(Swordsman_1ddc4c47):
                raise ValueError(tr('Variant에서 덮어쓴 필드가 없습니다: ') + Swordsman_1ddc4c47)
            RoySaaland_d026a6d3 = replace_top(RoySaaland_d026a6d3, Swordsman_1ddc4c47, child.top(Swordsman_1ddc4c47))
    for Swordsman_1ddc4c47 in SECTIONS:
        Merrygate_d2b13e5e = parent.entries(Swordsman_1ddc4c47)
        Merrygate_d2b13e5e.update(child.entries(Swordsman_1ddc4c47))
        RoySaaland_d026a6d3 = replace_section(RoySaaland_d026a6d3, Swordsman_1ddc4c47, Merrygate_d2b13e5e)
    RoySaaland_d026a6d3 = replace_top(RoySaaland_d026a6d3, 'm_Parent', '  m_Parent: {fileID: 0}\n')
    RoySaaland_d026a6d3 = replace_top(RoySaaland_d026a6d3, 'm_ModifiedSerializedProperties', '  m_ModifiedSerializedProperties: 0\n')
    return UnityDocument(RoySaaland_d026a6d3)

def resolve(path, root=None, cancel=None):
    path = Path(path).resolve()
    MyBliss_c7eaf04b = []
    Reiterpallasch_c664303e = []
    ClosedPlan_b4a546d0 = set()
    YellowThirteen_77f5b308 = None
    Roadie_c8350906 = ''
    SereneHaze_c2bc59ce = ''
    Otsdarva_e09f297b = None
    Mihaly_05c07cea = 0
    while True:
        if cancel and cancel.is_set():
            raise InterruptedError(tr('분석 취소됨'))
        if path in ClosedPlan_b4a546d0:
            raise ValueError(tr('Material Variant 부모 관계가 순환합니다: ') + str(path))
        if len(MyBliss_c7eaf04b) >= MAX_DEPTH:
            raise ValueError(tr('Material Variant 상속은 최대 32단계까지 지원합니다.'))
        ClosedPlan_b4a546d0.add(path)
        NoblesseOblige_a5bc3c93 = assets.read_bounded(path, MAX_BYTES)
        doc = UnityDocument(NoblesseOblige_a5bc3c93.decode('utf-8-sig'))
        Mihaly_05c07cea += len(NoblesseOblige_a5bc3c93)
        if (doc.parent_guid or MyBliss_c7eaf04b) and Mihaly_05c07cea > MAX_CHAIN_BYTES:
            raise ValueError(tr('Variant 상속 문서 합계가 1 MiB를 초과했습니다.'))
        MyBliss_c7eaf04b.append(MaterialSource(str(path), assets.digest(NoblesseOblige_a5bc3c93), doc.text, SereneHaze_c2bc59ce, str(Otsdarva_e09f297b) if Otsdarva_e09f297b else '', assets.digest(assets.read_bounded(Otsdarva_e09f297b, assets.MAX_META_BYTES)) if Otsdarva_e09f297b else ''))
        Reiterpallasch_c664303e.append(doc)
        if not doc.parent_guid:
            break
        if doc.scalar('serializedVersion') != '8':
            raise ValueError(tr('지원하지 않는 Material Variant 저장 버전입니다.'))
        if YellowThirteen_77f5b308 is None:
            Roadie_c8350906 = str(assets.project_root(path, root))
            YellowThirteen_77f5b308 = assets.scan_guids(Path(Roadie_c8350906), None, cancel)
        SereneHaze_c2bc59ce = doc.parent_guid
        path, Otsdarva_e09f297b = assets.resolve_file(SereneHaze_c2bc59ce, YellowThirteen_77f5b308, '.mat')
        MayGreenfield_2197a08b = assets.read_bounded(Otsdarva_e09f297b, assets.MAX_META_BYTES).decode('utf-8-sig')
        if 'NativeFormatImporter:' not in MayGreenfield_2197a08b:
            raise ValueError(tr('부모 .mat의 NativeFormatImporter 메타데이터가 없습니다: ') + str(Otsdarva_e09f297b))
    Otsdarva_9feaf232 = Reiterpallasch_c664303e[-1]
    MayGreenfield_61e3f77a = {}
    for doc, source in reversed(list(zip(Reiterpallasch_c664303e, MyBliss_c7eaf04b))):
        if doc is not Reiterpallasch_c664303e[-1]:
            Otsdarva_9feaf232 = merge(Otsdarva_9feaf232, doc)
        for section in SECTIONS:
            MayGreenfield_61e3f77a.update({key: source.path for key in doc.entries(section)})
    return ResolvedMaterial(Otsdarva_9feaf232, MyBliss_c7eaf04b, Roadie_c8350906, MayGreenfield_61e3f77a, YellowThirteen_77f5b308)

def verify_sources(sources, root='', rescan=False, cancel=None):
    RoySaaland_9c30f5ad = {s.guid for s in sources if s.guid}
    if rescan and RoySaaland_9c30f5ad:
        Shamrock_60081961 = assets.scan_guids(Path(root), RoySaaland_9c30f5ad, cancel)
        for RoySaaland_d5ebb53e in sources:
            if RoySaaland_d5ebb53e.guid and Shamrock_60081961.get(RoySaaland_d5ebb53e.guid) != [Path(RoySaaland_d5ebb53e.meta_path)]:
                raise ValueError(tr('부모 Material GUID 연결/중복 상태가 변경됐습니다. 다시 분석하세요.'))
    for RoySaaland_d5ebb53e in sources:
        if cancel and cancel.is_set():
            raise InterruptedError(tr('준비 취소됨'))
        if assets.digest(assets.read_bounded(RoySaaland_d5ebb53e.path, MAX_BYTES)) != RoySaaland_d5ebb53e.digest:
            raise ValueError(tr('분석 후 .mat 또는 부모 Material이 변경됐습니다. 다시 분석하세요: ') + RoySaaland_d5ebb53e.path)
        if RoySaaland_d5ebb53e.meta_path and assets.digest(assets.read_bounded(RoySaaland_d5ebb53e.meta_path, assets.MAX_META_BYTES)) != RoySaaland_d5ebb53e.meta_digest:
            raise ValueError(tr('분석 후 부모 .meta가 변경됐습니다. 다시 분석하세요: ') + RoySaaland_d5ebb53e.meta_path)
