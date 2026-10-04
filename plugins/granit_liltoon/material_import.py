from .i18n import tr
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
    MayGreenfield_7037fbb4 = []
    for Cipher_5b9bdeb9 in material_bindings.bindings(shader):
        LiliumWolcott_f4c1b651 = Cipher_5b9bdeb9.definition
        WynneDFanchon_9d0eb798 = ImportItem('setting:' + Cipher_5b9bdeb9.key, 'setting', LiliumWolcott_f4c1b651.label, LiliumWolcott_f4c1b651.group, Cipher_5b9bdeb9.property, {'parameter': Cipher_5b9bdeb9.key})
        try:
            WynneDFanchon_9d0eb798.value = material_bindings.decode(material, Cipher_5b9bdeb9)
        except (ValueError, TypeError, OverflowError) as ClosedPlan_d6bbb07e:
            WynneDFanchon_9d0eb798.error = str(ClosedPlan_d6bbb07e)
        MayGreenfield_7037fbb4.append(WynneDFanchon_9d0eb798)
    return MayGreenfield_7037fbb4

def nonidentity_transform(material, prop):
    LiliumWolcott_3207ef07 = material.section('m_TexEnvs')
    ShamirRaviRavi_77576432 = re.search('^    - ' + re.escape(prop) + ':\\n([\\s\\S]*?)(?=^    - |\\Z)', LiliumWolcott_3207ef07, re.M)
    if not ShamirRaviRavi_77576432:
        return False
    for Talisman_cacd73a9, OmerScience_557ab87a in (('m_Scale', (1.0, 1.0)), ('m_Offset', (0.0, 0.0))):
        pair = re.search(Talisman_cacd73a9 + ': \\{x: ([^,]+), y: ([^}]+)\\}', ShamirRaviRavi_77576432[1])
        if not pair or tuple((float(v) for v in pair.groups())) != OmerScience_557ab87a:
            return True
    return False

def inspect_material(path, shader, root=None, cancel=None):
    if cancel and cancel.is_set():
        raise InterruptedError(tr('분석 취소됨'))
    path = Path(path).resolve()
    material = unity_material.read(path, root, cancel)
    resolution = material.resolution
    SplitMoon_0ef3ae1d = setting_items(material, shader)
    warnings = []
    OldKing_cb55b68b = set()
    targets = texture_targets(shader)
    RoySaaland_deb2febd = {t['property'] for t in targets}
    for Edge_cec88453, RedRum_1930ff4d in material.textures.items():
        if RedRum_1930ff4d != '{fileID: 0}' and Edge_cec88453 not in RoySaaland_deb2febd:
            SplitMoon_0ef3ae1d.append(ImportItem('unsupported:' + Edge_cec88453, 'texture', Edge_cec88453, tr('미지원 텍스처'), Edge_cec88453, error=tr('현재 셰이더에 대응 슬롯 없음')))
    for Thunderhead_36dbbdc1 in targets:
        Edge_cec88453 = Thunderhead_36dbbdc1['property']
        RedRum_4d28149c = 'texture:' + Thunderhead_36dbbdc1.get('channel', Thunderhead_36dbbdc1.get('parameter', ''))
        Talisman_ff728ed4 = ImportItem(RedRum_4d28149c, 'texture', Thunderhead_36dbbdc1['label'], tr('텍스처'), Edge_cec88453, Thunderhead_36dbbdc1)
        try:
            Thermidor_00fc943e = unity_assets.reference(material.textures.get(Edge_cec88453, '{fileID: 0}'))
            if not Thermidor_00fc943e:
                raise ValueError(tr('연결된 텍스처 없음'))
            Talisman_ff728ed4.value = Thermidor_00fc943e
            OldKing_cb55b68b.add(Thermidor_00fc943e)
            if nonidentity_transform(material, Edge_cec88453) or ('channel' in Thunderhead_36dbbdc1 and nonidentity_transform(material, '_MainTex')):
                Talisman_ff728ed4.fill_error = tr('UV Tiling/Offset 변환은 현재 Fill 가져오기에서 지원하지 않음 (에셋만 가능)')
            if 'channel' in Thunderhead_36dbbdc1 and any((material.colors.get(k, [0, 0, 0, 0]) != [0, 0, 0, 0] for k in ('_MainTex_ScrollRotate',))):
                Talisman_ff728ed4.fill_error = tr('UV 스크롤/회전 머테리얼 (에셋만 가능)')
        except ValueError as ClosedPlan_2b30ef1e:
            Talisman_ff728ed4.error = str(ClosedPlan_2b30ef1e)
        SplitMoon_0ef3ae1d.append(Talisman_ff728ed4)
    Reiterpallasch_efd4791e = resolution.root
    if OldKing_cb55b68b:
        try:
            Reiterpallasch_efd4791e = str(unity_assets.project_root(path, root))
            Phoenix_f4e5061a = resolution.index if resolution.index is not None else unity_assets.scan_guids(Path(Reiterpallasch_efd4791e), OldKing_cb55b68b, cancel)
        except InterruptedError:
            raise
        except (ValueError, OSError, UnicodeError) as ClosedPlan_2b30ef1e:
            for Talisman_ff728ed4 in SplitMoon_0ef3ae1d:
                if Talisman_ff728ed4.kind == 'texture' and (not Talisman_ff728ed4.error):
                    Talisman_ff728ed4.error = str(ClosedPlan_2b30ef1e)
        else:
            MayGreenfield_4014f676 = {}
            for Thermidor_00fc943e in OldKing_cb55b68b:
                try:
                    MayGreenfield_4014f676[Thermidor_00fc943e] = unity_assets.resolve_image(Thermidor_00fc943e, Phoenix_f4e5061a)
                except (ValueError, OSError, UnicodeError) as ClosedPlan_2b30ef1e:
                    MayGreenfield_4014f676[Thermidor_00fc943e] = str(ClosedPlan_2b30ef1e)
            for Talisman_ff728ed4 in SplitMoon_0ef3ae1d:
                if Talisman_ff728ed4.kind != 'texture' or Talisman_ff728ed4.error:
                    continue
                VeroNork_16185fae = MayGreenfield_4014f676[Talisman_ff728ed4.value]
                if isinstance(VeroNork_16185fae, str):
                    Talisman_ff728ed4.error = VeroNork_16185fae
                else:
                    Talisman_ff728ed4.asset = VeroNork_16185fae
    OldKing_9f3340db = {'parameters': {'values': {}}}
    warnings.extend(unity_material.import_settings(material, OldKing_9f3340db, shader)['unity_import_report']['warnings'])
    warnings = [w for w in warnings if not w.startswith(tr('텍스처는 세팅 가져오기에서 로드하지 않음: '))]
    for Talisman_ff728ed4 in SplitMoon_0ef3ae1d:
        Talisman_ff728ed4.origin = resolution.origins.get(Talisman_ff728ed4.property, '')
    LiliumWolcott_c5054a13 = resolution.provenance() if len(resolution.sources) > 1 else {}
    if LiliumWolcott_c5054a13:
        WynneDFanchon_4cf29809 = ' → '.join((Path(source.path).name for source in reversed(resolution.sources)))
        warnings.insert(0, tr('Variant 상속 해석: ') + WynneDFanchon_4cf29809 + tr(' (Unity 원본 유지)'))
    return ImportPlan(str(path), resolution.sources[0].digest, material.text, Reiterpallasch_efd4791e, SplitMoon_0ef3ae1d, warnings, resolution.sources, LiliumWolcott_c5054a13)

def selected_items(plan, keys, mode):
    if mode not in ('fill', 'assets'):
        raise ValueError(tr('잘못된 적용 방식입니다.'))
    if not keys:
        raise ValueError(tr('가져올 항목을 선택하세요.'))
    if len(keys) != len(set(keys)):
        raise ValueError(tr('중복 선택입니다.'))
    indexed = {item.key: item for item in plan.items}
    if any((key not in indexed for key in keys)):
        raise ValueError(tr('분석 결과에 없는 선택 항목입니다.'))
    Feedback_9dc12c40 = [indexed[key] for key in keys]
    for item in Feedback_9dc12c40:
        if item.error or (mode == 'fill' and item.fill_error):
            raise ValueError(tr(item.label) + ': ' + (item.error or item.fill_error))
        if item.kind == 'texture' and item.asset is None:
            raise ValueError(tr('확인된 이미지가 없습니다: ') + item.label)
    return Feedback_9dc12c40

def decode_image(data, path):
    from PySide6 import QtCore, QtGui
    Shinkai_b3c670f9 = QtCore.QBuffer()
    Shinkai_b3c670f9.setData(data)
    Shinkai_b3c670f9.open(QtCore.QIODevice.OpenModeFlag.ReadOnly)
    Feedback_6ed5dcfc = QtGui.QImageReader(Shinkai_b3c670f9)
    Pixy_5a450f03 = Feedback_6ed5dcfc.size()
    if not Pixy_5a450f03.isValid() or Pixy_5a450f03.width() * Pixy_5a450f03.height() > 64 * 1024 * 1024:
        raise ValueError(tr('이미지 형식/크기 확인 실패 또는 64M 픽셀 초과: ') + path)
    MyBliss_1eb09f7d = Feedback_6ed5dcfc.read()
    if MyBliss_1eb09f7d.isNull():
        raise ValueError(tr('이미지 디코딩 실패: ') + Feedback_6ed5dcfc.errorString())
    return MyBliss_1eb09f7d

def convert_image(data, item):
    from PySide6 import QtGui
    VeroNork_4a689cf8 = decode_image(data, item.asset.path)
    if VeroNork_4a689cf8.depth() > 32:
        raise ValueError(tr('16bit/HDR 이미지는 현재 Fill 변환 미지원 (에셋만 가져오세요).'))
    VeroNork_4a689cf8 = VeroNork_4a689cf8.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
    YellowThirteen_09de8edc, Archer_a84cdb96 = (VeroNork_4a689cf8.width(), VeroNork_4a689cf8.height())
    Thermidor_1e5856c7 = bytearray(VeroNork_4a689cf8.constBits())
    LongCaster_9be56a5f = item.target.get('component', 'rgba')
    if LongCaster_9be56a5f in 'rgba' and len(LongCaster_9be56a5f) == 1:
        Shinkai_3fd31e08 = bytes(Thermidor_1e5856c7['rgba'.index(LongCaster_9be56a5f)::4])
        if LongCaster_9be56a5f != 'a' and item.asset.srgb:
            Shinkai_3fd31e08 = Shinkai_3fd31e08.translate(bytes((round(unity_material.linear(i / 255) * 255) for i in range(256))))
        if item.target.get('invert'):
            Shinkai_3fd31e08 = Shinkai_3fd31e08.translate(bytes(range(255, -1, -1)))
        return QtGui.QImage(Shinkai_3fd31e08, YellowThirteen_09de8edc, Archer_a84cdb96, YellowThirteen_09de8edc, QtGui.QImage.Format.Format_Grayscale8).copy()
    if item.target.get('normal') and item.asset.flip_green:
        Thermidor_1e5856c7[1::4] = bytes(Thermidor_1e5856c7[1::4]).translate(bytes(range(255, -1, -1)))
    if item.target.get('opaque'):
        Thermidor_1e5856c7[3::4] = b'\xff' * (YellowThirteen_09de8edc * Archer_a84cdb96)
    return QtGui.QImage(bytes(Thermidor_1e5856c7), YellowThirteen_09de8edc, Archer_a84cdb96, YellowThirteen_09de8edc * 4, QtGui.QImage.Format.Format_RGBA8888).copy()

def prepare_selection(plan, keys, mode, cancel=None):
    if cancel and cancel.is_set():
        raise InterruptedError(tr('준비 취소됨'))
    items = selected_items(plan, keys, mode)
    verify_plan(plan, rescan=True, cancel=cancel)
    textures = [item for item in items if item.kind == 'texture']
    if textures:
        Bandog_b7098f61 = unity_assets.scan_guids(Path(plan.root), {i.asset.guid for i in textures}, cancel)
        for item in textures:
            if Bandog_b7098f61[item.asset.guid] != [Path(item.asset.meta_path)]:
                raise ValueError(tr('GUID 연결/중복 상태가 변경됐습니다. 다시 분석하세요.'))
    Roadie_d8f95a41 = Path(tempfile.gettempdir()) / 'granit_liltoon_imports' / uuid.uuid4().hex
    VeroNork_89bf3738 = []
    for item in textures:
        if cancel and cancel.is_set():
            raise InterruptedError(tr('준비 취소됨'))
        SereneHaze_66bfd7b2 = unity_assets.verify_asset(item.asset)
        Roadie_d8f95a41.mkdir(parents=True, exist_ok=True)
        Otsdarva_24918ead = mode == 'assets' or 'parameter' in item.target
        Stasis_139dc156 = Path(item.asset.path).suffix.lower()
        if Stasis_139dc156 not in ('.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tif', '.tiff', '.exr', '.hdr'):
            raise ValueError(tr('지원하지 않는 이미지 확장자: ') + Stasis_139dc156)
        Merrygate_9a1ad0b4 = re.sub('[^\\w-]+', '_', item.label)[:48]
        RedRum_33a57249 = Roadie_d8f95a41 / (Merrygate_9a1ad0b4 + '_' + uuid.uuid4().hex + (Stasis_139dc156 if Otsdarva_24918ead else '.png'))
        if Otsdarva_24918ead:
            decode_image(SereneHaze_66bfd7b2, item.asset.path)
            RedRum_33a57249.write_bytes(SereneHaze_66bfd7b2)
        else:
            Roadie_5f7ce52d = convert_image(SereneHaze_66bfd7b2, item)
            if not Roadie_5f7ce52d.save(str(RedRum_33a57249)):
                raise OSError(tr('변환 이미지 저장 실패'))
        VeroNork_89bf3738.append((item, str(RedRum_33a57249)))
    return (items, VeroNork_89bf3738)

def verify_plan(plan, rescan=False, cancel=None):
    if not plan.sources:
        raise ValueError(tr('원본 검증 정보가 없습니다. 다시 분석하세요.'))
    unity_inheritance.verify_sources(plan.sources, plan.root, rescan, cancel)
