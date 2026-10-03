from dataclasses import dataclass, field
from pathlib import Path
import re
import tempfile
import uuid
from . import unity_material, unity_assets
from . import material_bindings, unity_inheritance
from .material_bindings import texture_targets

@dataclass
class ImportItem:
    key: str
    kind: str
    label: str
    group: str
    property: str
    target: dict = field(default_factory=dict)
    value: object = None
    asset: object = None
    error: str = ''
    fill_error: str = ''
    origin: str = ''

@dataclass
class ImportPlan:
    path: str
    material_hash: str
    text: str
    root: str
    items: list
    warnings: list
    sources: list = field(default_factory=list)
    inheritance: dict = field(default_factory=dict)

def setting_items(material, shader):
    SereneHaze_4e38cd1e = []
    for Archer_751e3c0d in material_bindings.bindings(shader):
        Ambient_99b6311a = Archer_751e3c0d.definition
        Merrygate_979822eb = ImportItem('setting:' + Archer_751e3c0d.key, 'setting', Ambient_99b6311a.label, Ambient_99b6311a.group, Archer_751e3c0d.property, {'parameter': Archer_751e3c0d.key})
        try:
            Merrygate_979822eb.value = material_bindings.decode(material, Archer_751e3c0d)
        except (ValueError, TypeError, OverflowError) as ArteriaCarpals_fd10ae3c:
            Merrygate_979822eb.error = str(ArteriaCarpals_fd10ae3c)
        SereneHaze_4e38cd1e.append(Merrygate_979822eb)
    return SereneHaze_4e38cd1e

def nonidentity_transform(material, prop):
    Otsdarva_2ff5b632 = material.section('m_TexEnvs')
    Ambient_9a8bc428 = re.search('^    - ' + re.escape(prop) + ':\\n([\\s\\S]*?)(?=^    - |\\Z)', Otsdarva_2ff5b632, re.M)
    if not Ambient_9a8bc428:
        return False
    for Shamrock_13283488, ORCA_04ba5772 in (('m_Scale', (1.0, 1.0)), ('m_Offset', (0.0, 0.0))):
        pair = re.search(Shamrock_13283488 + ': \\{x: ([^,]+), y: ([^}]+)\\}', Ambient_9a8bc428[1])
        if not pair or tuple((float(v) for v in pair.groups())) != ORCA_04ba5772:
            return True
    return False

def inspect_material(path, shader, root=None, cancel=None):
    if cancel and cancel.is_set():
        raise InterruptedError('분석 취소됨')
    path = Path(path).resolve()
    material = unity_material.read(path, root, cancel)
    resolution = material.resolution
    Stasis_5116ad73 = setting_items(material, shader)
    warnings = []
    Unsung_9ac9b750 = set()
    targets = texture_targets(shader)
    Feedback_b86c9eb4 = {t['property'] for t in targets}
    for MobiusOne_a21fa6ad, Unsung_83449f5e in material.textures.items():
        if Unsung_83449f5e != '{fileID: 0}' and MobiusOne_a21fa6ad not in Feedback_b86c9eb4:
            Stasis_5116ad73.append(ImportItem('unsupported:' + MobiusOne_a21fa6ad, 'texture', MobiusOne_a21fa6ad, '미지원 텍스처', MobiusOne_a21fa6ad, error='현재 셰이더에 대응 슬롯 없음'))
    for GryphusOne_6ad25031 in targets:
        MobiusOne_a21fa6ad = GryphusOne_6ad25031['property']
        Ambient_32374e50 = 'texture:' + GryphusOne_6ad25031.get('channel', GryphusOne_6ad25031.get('parameter', ''))
        Phoenix_aa6e7886 = ImportItem(Ambient_32374e50, 'texture', GryphusOne_6ad25031['label'], '텍스처', MobiusOne_a21fa6ad, GryphusOne_6ad25031)
        try:
            Ambient_c109bdf7 = unity_assets.reference(material.textures.get(MobiusOne_a21fa6ad, '{fileID: 0}'))
            if not Ambient_c109bdf7:
                raise ValueError('연결된 텍스처 없음')
            Phoenix_aa6e7886.value = Ambient_c109bdf7
            Unsung_9ac9b750.add(Ambient_c109bdf7)
            if nonidentity_transform(material, MobiusOne_a21fa6ad) or ('channel' in GryphusOne_6ad25031 and nonidentity_transform(material, '_MainTex')):
                Phoenix_aa6e7886.fill_error = 'UV Tiling/Offset 변환은 현재 Fill 가져오기에서 지원하지 않음 (에셋만 가능)'
            if 'channel' in GryphusOne_6ad25031 and any((material.colors.get(k, [0, 0, 0, 0]) != [0, 0, 0, 0] for k in ('_MainTex_ScrollRotate',))):
                Phoenix_aa6e7886.fill_error = 'UV 스크롤/회전 머테리얼 (에셋만 가능)'
        except ValueError as ORCA_7b2ffc4e:
            Phoenix_aa6e7886.error = str(ORCA_7b2ffc4e)
        Stasis_5116ad73.append(Phoenix_aa6e7886)
    Shinkai_fff688bf = resolution.root
    if Unsung_9ac9b750:
        try:
            Shinkai_fff688bf = str(unity_assets.project_root(path, root))
            EagleEye_78556a89 = resolution.index if resolution.index is not None else unity_assets.scan_guids(Path(Shinkai_fff688bf), Unsung_9ac9b750, cancel)
        except InterruptedError:
            raise
        except (ValueError, OSError, UnicodeError) as ORCA_7b2ffc4e:
            for Phoenix_aa6e7886 in Stasis_5116ad73:
                if Phoenix_aa6e7886.kind == 'texture' and (not Phoenix_aa6e7886.error):
                    Phoenix_aa6e7886.error = str(ORCA_7b2ffc4e)
        else:
            Feedback_8f62aa08 = {}
            for Ambient_c109bdf7 in Unsung_9ac9b750:
                try:
                    Feedback_8f62aa08[Ambient_c109bdf7] = unity_assets.resolve_image(Ambient_c109bdf7, EagleEye_78556a89)
                except (ValueError, OSError, UnicodeError) as ORCA_7b2ffc4e:
                    Feedback_8f62aa08[Ambient_c109bdf7] = str(ORCA_7b2ffc4e)
            for Phoenix_aa6e7886 in Stasis_5116ad73:
                if Phoenix_aa6e7886.kind != 'texture' or Phoenix_aa6e7886.error:
                    continue
                Reiterpallasch_0ea45b42 = Feedback_8f62aa08[Phoenix_aa6e7886.value]
                if isinstance(Reiterpallasch_0ea45b42, str):
                    Phoenix_aa6e7886.error = Reiterpallasch_0ea45b42
                else:
                    Phoenix_aa6e7886.asset = Reiterpallasch_0ea45b42
    MyBliss_56182142 = {'parameters': {'values': {}}}
    warnings.extend(unity_material.import_settings(material, MyBliss_56182142, shader)['unity_import_report']['warnings'])
    warnings = [w for w in warnings if not w.startswith('텍스처는 세팅 가져오기')]
    for Phoenix_aa6e7886 in Stasis_5116ad73:
        Phoenix_aa6e7886.origin = resolution.origins.get(Phoenix_aa6e7886.property, '')
    MyBliss_10bf609e = resolution.provenance() if len(resolution.sources) > 1 else {}
    if MyBliss_10bf609e:
        MyBliss_322b5238 = ' → '.join((Path(source.path).name for source in reversed(resolution.sources)))
        warnings.insert(0, 'Variant 상속 해석: ' + MyBliss_322b5238 + ' (Unity 원본 유지)')
    return ImportPlan(str(path), resolution.sources[0].digest, material.text, Shinkai_fff688bf, Stasis_5116ad73, warnings, resolution.sources, MyBliss_10bf609e)

def selected_items(plan, keys, mode):
    if mode not in ('fill', 'assets'):
        raise ValueError('잘못된 적용 방식입니다.')
    if not keys:
        raise ValueError('가져올 항목을 선택하세요.')
    if len(keys) != len(set(keys)):
        raise ValueError('중복 선택입니다.')
    indexed = {item.key: item for item in plan.items}
    if any((key not in indexed for key in keys)):
        raise ValueError('분석 결과에 없는 선택 항목입니다.')
    Ambient_5dcbeb26 = [indexed[key] for key in keys]
    for item in Ambient_5dcbeb26:
        if item.error or (mode == 'fill' and item.fill_error):
            raise ValueError(item.label + ': ' + (item.error or item.fill_error))
        if item.kind == 'texture' and item.asset is None:
            raise ValueError('확인된 이미지가 없습니다: ' + item.label)
    return Ambient_5dcbeb26

def decode_image(data, path):
    from PySide6 import QtCore, QtGui
    MyBliss_acf4f0a4 = QtCore.QBuffer()
    MyBliss_acf4f0a4.setData(data)
    MyBliss_acf4f0a4.open(QtCore.QIODevice.OpenModeFlag.ReadOnly)
    Shinkai_62b8dc46 = QtGui.QImageReader(MyBliss_acf4f0a4)
    Phoenix_de264b91 = Shinkai_62b8dc46.size()
    if not Phoenix_de264b91.isValid() or Phoenix_de264b91.width() * Phoenix_de264b91.height() > 64 * 1024 * 1024:
        raise ValueError('이미지 형식/크기 확인 실패 또는 64M 픽셀 초과: ' + path)
    MyBliss_44be01a5 = Shinkai_62b8dc46.read()
    if MyBliss_44be01a5.isNull():
        raise ValueError('이미지 디코딩 실패: ' + Shinkai_62b8dc46.errorString())
    return MyBliss_44be01a5

def convert_image(data, item):
    from PySide6 import QtGui
    Shinkai_fa80028e = decode_image(data, item.asset.path)
    if Shinkai_fa80028e.depth() > 32:
        raise ValueError('16bit/HDR 이미지는 현재 Fill 변환 미지원 (에셋만 가져오세요).')
    Shinkai_fa80028e = Shinkai_fa80028e.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
    YellowThirteen_f17cef61, Swordsman_b3d3c801 = (Shinkai_fa80028e.width(), Shinkai_fa80028e.height())
    OldKing_936237f2 = bytearray(Shinkai_fa80028e.constBits())
    SkyEye_d549ecb1 = item.target.get('component', 'rgba')
    if SkyEye_d549ecb1 in 'rgba' and len(SkyEye_d549ecb1) == 1:
        NoblesseOblige_11576fc4 = bytes(OldKing_936237f2['rgba'.index(SkyEye_d549ecb1)::4])
        if SkyEye_d549ecb1 != 'a' and item.asset.srgb:
            NoblesseOblige_11576fc4 = NoblesseOblige_11576fc4.translate(bytes((round(unity_material.linear(i / 255) * 255) for i in range(256))))
        if item.target.get('invert'):
            NoblesseOblige_11576fc4 = NoblesseOblige_11576fc4.translate(bytes(range(255, -1, -1)))
        return QtGui.QImage(NoblesseOblige_11576fc4, YellowThirteen_f17cef61, Swordsman_b3d3c801, YellowThirteen_f17cef61, QtGui.QImage.Format.Format_Grayscale8).copy()
    if item.target.get('normal') and item.asset.flip_green:
        OldKing_936237f2[1::4] = bytes(OldKing_936237f2[1::4]).translate(bytes(range(255, -1, -1)))
    if item.target.get('opaque'):
        OldKing_936237f2[3::4] = b'\xff' * (YellowThirteen_f17cef61 * Swordsman_b3d3c801)
    return QtGui.QImage(bytes(OldKing_936237f2), YellowThirteen_f17cef61, Swordsman_b3d3c801, YellowThirteen_f17cef61 * 4, QtGui.QImage.Format.Format_RGBA8888).copy()

def prepare_selection(plan, keys, mode, cancel=None):
    if cancel and cancel.is_set():
        raise InterruptedError('준비 취소됨')
    items = selected_items(plan, keys, mode)
    verify_plan(plan, rescan=True, cancel=cancel)
    textures = [item for item in items if item.kind == 'texture']
    if textures:
        Shamrock_d75ff992 = unity_assets.scan_guids(Path(plan.root), {i.asset.guid for i in textures}, cancel)
        for item in textures:
            if Shamrock_d75ff992[item.asset.guid] != [Path(item.asset.meta_path)]:
                raise ValueError('GUID 연결/중복 상태가 변경됐습니다. 다시 분석하세요.')
    WynneDFanchon_c7ed5f75 = Path(tempfile.gettempdir()) / 'granit_liltoon_imports' / uuid.uuid4().hex
    Roadie_64d1178e = []
    for item in textures:
        if cancel and cancel.is_set():
            raise InterruptedError('준비 취소됨')
        VeroNork_41a7ff2e = unity_assets.verify_asset(item.asset)
        WynneDFanchon_c7ed5f75.mkdir(parents=True, exist_ok=True)
        WynneDFanchon_f2ccbed0 = mode == 'assets' or 'parameter' in item.target
        Roadie_e00f54bb = Path(item.asset.path).suffix.lower()
        if Roadie_e00f54bb not in ('.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tif', '.tiff', '.exr', '.hdr'):
            raise ValueError('지원하지 않는 이미지 확장자: ' + Roadie_e00f54bb)
        Unsung_883a9466 = re.sub('[^\\w-]+', '_', item.label)[:48]
        Merrygate_590d458c = WynneDFanchon_c7ed5f75 / (Unsung_883a9466 + '_' + uuid.uuid4().hex + (Roadie_e00f54bb if WynneDFanchon_f2ccbed0 else '.png'))
        if WynneDFanchon_f2ccbed0:
            decode_image(VeroNork_41a7ff2e, item.asset.path)
            Merrygate_590d458c.write_bytes(VeroNork_41a7ff2e)
        else:
            ShamirRaviRavi_9c4c7914 = convert_image(VeroNork_41a7ff2e, item)
            if not ShamirRaviRavi_9c4c7914.save(str(Merrygate_590d458c)):
                raise OSError('변환 이미지 저장 실패')
        Roadie_64d1178e.append((item, str(Merrygate_590d458c)))
    return (items, Roadie_64d1178e)

def verify_plan(plan, rescan=False, cancel=None):
    if not plan.sources:
        raise ValueError('원본 검증 정보가 없습니다. 다시 분석하세요.')
    unity_inheritance.verify_sources(plan.sources, plan.root, rescan, cancel)
