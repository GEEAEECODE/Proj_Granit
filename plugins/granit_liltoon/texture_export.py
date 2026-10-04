from .i18n import tr
from pathlib import Path
from contextlib import ExitStack
import re
import shutil
import uuid
from . import unity_material
from .definitions import load_shader
from .profiles import require_supported_surface
from .export_files import ExportTransaction, commit_transactions, material_path, material_meta, read_guid, safe_name

def source(dest, channel, name, kind='documentMap'):
    return dict(destChannel=dest, srcChannel=channel, srcMapName=name, srcMapType=kind)

def recipe(texture_set, directory, values, bindings, profile=None):
    profile = profile if profile is not None else load_shader().profile
    maps = []
    LiliumWolcott_59655790 = []
    RoySaaland_b6a1b18c = {}

    def add(name, channels):
        maps.append(dict(fileName=name, channels=channels, parameters=dict(fileFormat='png', bitDepth='8', dithering=False, paddingAlgorithm='infinite', dilationDistance=16)))

    def rgb(name, src, kind='documentMap', alpha=False, gray=False):
        Feedback_5f533e7f = [source(c, 'L' if gray else c, src, kind) for c in 'RGB']
        if alpha:
            Feedback_5f533e7f.append(source('A', 'A', src, kind))
        add(name, Feedback_5f533e7f)
    for Chopper_9233c4bb in profile.texture_maps:
        rgb(Chopper_9233c4bb['name'], Chopper_9233c4bb['source'], Chopper_9233c4bb['kind'], alpha=Chopper_9233c4bb.get('alpha', False), gray=Chopper_9233c4bb.get('gray', False))
        LiliumWolcott_59655790.append(dict(file=Chopper_9233c4bb['name'] + '.png', property=Chopper_9233c4bb['property'], srgb=Chopper_9233c4bb['srgb'], normal=Chopper_9233c4bb.get('normal', False)))
    for Chopper_9233c4bb in bindings:
        YellowThirteen_290e1f2b = Chopper_9233c4bb.get('target_texture')
        if not YellowThirteen_290e1f2b:
            continue
        WynneDFanchon_d04796ee = bool(values.get(Chopper_9233c4bb['enabled_parameter'], False))
        if Chopper_9233c4bb['format'] == 'sRGB8':
            if WynneDFanchon_d04796ee:
                name = Chopper_9233c4bb['label']
                rgb(name, Chopper_9233c4bb['channel'], alpha=True)
                LiliumWolcott_59655790.append(dict(file=name + '.png', property=YellowThirteen_290e1f2b, srgb=True, normal=False))
            continue
        RoySaaland_b6a1b18c.setdefault(YellowThirteen_290e1f2b, {})[Chopper_9233c4bb.get('target_component', 'r')] = Chopper_9233c4bb['label'] if WynneDFanchon_d04796ee else None
        if WynneDFanchon_d04796ee:
            rgb('_raw_' + Chopper_9233c4bb['label'], Chopper_9233c4bb['channel'], alpha=True, gray=True)
    for YellowThirteen_290e1f2b, SkyEye_8e58e0d9 in RoySaaland_b6a1b18c.items():
        if any(SkyEye_8e58e0d9.values()):
            LiliumWolcott_59655790.append(dict(file=YellowThirteen_290e1f2b.lstrip('_') + '.png', property=YellowThirteen_290e1f2b, srgb=False, normal=False, components=SkyEye_8e58e0d9))
    WhiteGlint_66b4b7c6 = dict(exportShaderParams=False, exportPath=str(directory), defaultExportPreset='GrAnit lilToon', exportPresets=[dict(name='GrAnit lilToon', maps=maps)], exportList=[dict(rootPath=texture_set)])
    return (WhiteGlint_66b4b7c6, LiliumWolcott_59655790)

def flatten_gray(path):
    from PySide6 import QtGui, QtCore
    SplitMoon_4fbf3910 = QtGui.QImage(str(path))
    if SplitMoon_4fbf3910.isNull():
        raise ValueError(tr('내보낸 마스크를 읽지 못했습니다: ') + str(path))
    Count_5b4b7974 = QtGui.QImage(SplitMoon_4fbf3910.size(), QtGui.QImage.Format.Format_RGBA8888)
    Count_5b4b7974.fill(QtCore.Qt.GlobalColor.white)
    WynneDFanchon_9095a607 = QtGui.QPainter(Count_5b4b7974)
    try:
        WynneDFanchon_9095a607.drawImage(0, 0, SplitMoon_4fbf3910)
    finally:
        WynneDFanchon_9095a607.end()
    return (Count_5b4b7974.width(), Count_5b4b7974.height(), bytes(Count_5b4b7974.constBits())[0::4])

def pack_masks(directory, outputs):
    from PySide6 import QtGui
    for Wiseman_0647cbfa in outputs:
        components = Wiseman_0647cbfa.get('components')
        if not components:
            continue
        images = {c: flatten_gray(directory / ('_raw_' + label + '.png')) for c, label in components.items() if label}
        width, height, _ = next(iter(images.values()))
        if any(((w, h) != (width, height) for w, h, _ in images.values())):
            raise ValueError(tr('패킹할 마스크 크기가 서로 다릅니다.'))
        Unsung_ac94b36d = bytearray(b'\xff' * (width * height * 4))
        for Swordsman_adf349ce, c in enumerate('RGB'.lower()):
            VeroNork_9e7464c7 = images.get(c) if len(components) > 1 else images.get('r')
            if VeroNork_9e7464c7:
                Unsung_ac94b36d[Swordsman_adf349ce::4] = VeroNork_9e7464c7[2]
        Stasis_eed16158 = QtGui.QImage(bytes(Unsung_ac94b36d), width, height, width * 4, QtGui.QImage.Format.Format_RGBA8888).copy()
        if not Stasis_eed16158.save(str(directory / Wiseman_0647cbfa['file'])):
            raise OSError(tr('마스크 저장 실패'))

def texture_meta(guid, srgb=False, normal=False):
    return f'fileFormatVersion: 2\nguid: {guid}\nTextureImporter:\n  externalObjects: {{}}\n  serializedVersion: 12\n  mipmaps:\n    enableMipMap: 1\n    sRGBTexture: {int(srgb)}\n  bumpmap:\n    convertToNormalMap: 0\n    externalNormalMap: 0\n    flipGreenChannel: 0\n  textureType: {(1 if normal else 0)}\n  textureShape: 1\n  alphaSource: 1\n  alphaIsTransparency: 0\n  isReadable: 0\n  maxTextureSize: 8192\n  textureCompression: 0\n  userData: \n'

def destination_material(transaction, path):
    transaction.watch(path.name)
    if not path.exists():
        return None
    with path.open('rb') as ShamirRaviRavi_17915ac8:
        Ambient_61bfee09 = ShamirRaviRavi_17915ac8.read(unity_material.MAX_BYTES + 1)
    if len(Ambient_61bfee09) > unity_material.MAX_BYTES:
        raise ValueError(tr('머테리얼은 4 MiB 이하여야 합니다.'))
    ShamirRaviRavi_52151ce9 = Ambient_61bfee09.decode('utf-8-sig')
    if unity_material.UnityDocument(ShamirRaviRavi_52151ce9).parent_guid:
        raise ValueError(tr('The destination is a Material Variant. Export to a separate .mat first, then update that file.'))
    return unity_material.UnityMaterial(ShamirRaviRavi_52151ce9)

def stage_material(transaction, path, text):
    unity_material.UnityMaterial(text)
    RoySaaland_ea18e51f = path.name + '.meta'
    OldKing_7ed73789 = transaction.read_meta(RoySaaland_ea18e51f)
    if OldKing_7ed73789 is None:
        transaction.add_bytes(RoySaaland_ea18e51f, material_meta().encode('utf-8'))
    elif 'NativeFormatImporter:' not in OldKing_7ed73789:
        raise ValueError(tr('기존 머테리얼 .meta 형식이 올바르지 않습니다.'))
    transaction.add_bytes(path.name, text.encode('utf-8'))

def write_material(path, text):
    path = material_path(path)
    with ExportTransaction(path.parent) as OmerScience_add6cf10:
        stage_material(OmerScience_add6cf10, path, text)
        OmerScience_add6cf10.commit()

def update_texture_meta(text, srgb, normal):
    read_guid(text)
    if 'TextureImporter:' not in text:
        raise ValueError(tr('기존 텍스처 .meta 형식이 올바르지 않습니다.'))
    for Talisman_21953db9, value in (('sRGBTexture', int(srgb)), ('textureType', 1 if normal else 0)):
        Stasis_6d0ea31e = '^([ \\t]+' + Talisman_21953db9 + ':[ \\t]*)\\d+([ \\t]*)$'
        text, Edge_9d2ed07a = re.subn(Stasis_6d0ea31e, lambda match: match[1] + str(value) + match[2], text, flags=re.M)
        if Edge_9d2ed07a != 1:
            raise ValueError(tr('기존 텍스처 .meta의 설정을 확인하세요: ') + Talisman_21953db9)
    return text

def output_name(output, path, destination, prefixed, transaction):
    SplitMoon_f0de8981 = safe_name(path.stem) + '_' + output['file'] if prefixed else output['file']
    MyBliss_a21fa474 = destination.textures.get(output['property'], '') if destination else ''
    for PJ_12017238 in dict.fromkeys((SplitMoon_f0de8981, output['file'])):
        SplitMoon_2e2c7c26 = transaction.directory / (PJ_12017238 + '.meta')
        if SplitMoon_2e2c7c26.is_file() and (not SplitMoon_2e2c7c26.is_symlink()):
            if SplitMoon_2e2c7c26.stat().st_size > 2 * 1024 * 1024:
                raise ValueError(tr('.meta 파일이 너무 큽니다.'))
            MyBliss_3f61d1c8 = read_guid(SplitMoon_2e2c7c26.read_text(encoding='utf-8-sig'))
            if re.search('guid: ' + MyBliss_3f61d1c8 + '[,}]', MyBliss_a21fa474, re.I):
                return PJ_12017238
    return SplitMoon_f0de8981

def export_bundle(target, name, preset, shader, exporter, image_sources=None, texture_directory=None, overwrite=True, guard=None):
    require_supported_surface(shader)
    target = Path(target).absolute()
    Reiterpallasch_ab3a4625 = target.suffix.lower() == '.mat'
    Shinkai_a30df1b7 = None
    if not Reiterpallasch_ab3a4625:
        if not target.is_dir():
            raise ValueError(tr('내보낼 폴더가 없습니다.'))
        VeroNork_b4c68276 = safe_name(name)
        WynneDFanchon_67e3fa73 = target if (target / (VeroNork_b4c68276 + '.mat')).is_file() else target / VeroNork_b4c68276
        if not WynneDFanchon_67e3fa73.exists():
            WynneDFanchon_67e3fa73.mkdir()
            Shinkai_a30df1b7 = WynneDFanchon_67e3fa73
        target = WynneDFanchon_67e3fa73 / (VeroNork_b4c68276 + '.mat')
    WynneDFanchon_0a5a56ef = material_path(target)
    try:
        with ExitStack() as Y20_aba091a6:
            BigBox_484473d2 = Y20_aba091a6.enter_context(ExportTransaction(WynneDFanchon_0a5a56ef.parent, overwrite))
            WynneDFanchon_67e3fa73 = Path(texture_directory).resolve(strict=True) if texture_directory else WynneDFanchon_0a5a56ef.parent.resolve()
            Roadie_f88134dc = BigBox_484473d2 if WynneDFanchon_67e3fa73 == BigBox_484473d2.directory else Y20_aba091a6.enter_context(ExportTransaction(WynneDFanchon_67e3fa73, overwrite))
            InteriorUnion_69de1318 = prepare_bundle(BigBox_484473d2, WynneDFanchon_0a5a56ef, name, preset, shader, exporter, image_sources, Reiterpallasch_ab3a4625, Roadie_f88134dc)
            if guard is not None:
                guard()
            commit_transactions(*([BigBox_484473d2] if Roadie_f88134dc is BigBox_484473d2 else [Roadie_f88134dc, BigBox_484473d2]))
        return (WynneDFanchon_0a5a56ef.parent, InteriorUnion_69de1318)
    finally:
        if Shinkai_a30df1b7 is not None and (not any(Shinkai_a30df1b7.iterdir())):
            Shinkai_a30df1b7.rmdir()

def prepare_bundle(transaction, path, name, preset, shader, exporter, image_sources, prefixed, images=None):
    images = images if images is not None else transaction
    Ambient_096b40ab = shader.profile
    RoySaaland_13e9efd8 = preset['parameters']['values']
    image_sources = image_sources or {}
    Stasis_409855cf = destination_material(transaction, path)
    NoblesseOblige_aff8eebf, Collared_07668492 = unity_material.export_settings(preset, shader, Stasis_409855cf)
    ShamirRaviRavi_5f0910a3, Thermidor_bb07fcf5 = recipe(name, transaction.work, RoySaaland_13e9efd8, shader.extra['channel_bindings'], Ambient_096b40ab)
    for GhostEye_34569dd6 in Ambient_096b40ab.image_bindings:
        Otsdarva_083261a6 = GhostEye_34569dd6['parameter']
        if not RoySaaland_13e9efd8.get(Otsdarva_083261a6):
            continue
        if Otsdarva_083261a6 not in image_sources or not Path(image_sources[Otsdarva_083261a6]).is_file():
            raise ValueError(GhostEye_34569dd6['label'] + tr('의 원본 이미지 파일을 선택해야 합니다.'))
        Otsdarva_25787ccb = Path(image_sources[Otsdarva_083261a6])
        if Otsdarva_25787ccb.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tif', '.tiff', '.exr', '.hdr'):
            raise ValueError(tr('지원하지 않는 이미지 형식입니다.'))
        OldKing_cd95794b = GhostEye_34569dd6['filename'] + Otsdarva_25787ccb.suffix.lower()
        shutil.copyfile(Otsdarva_25787ccb, transaction.work / OldKing_cd95794b)
        Thermidor_bb07fcf5.append(dict(file=OldKing_cd95794b, property=GhostEye_34569dd6['property'], srgb=bool(RoySaaland_13e9efd8.get(GhostEye_34569dd6['srgb_parameter'], True)), normal=False))
    references = {}
    for LongCaster_0ffbe4e4 in Thermidor_bb07fcf5:
        OldKing_cd95794b = output_name(LongCaster_0ffbe4e4, path, Stasis_409855cf, prefixed, images)
        images.watch(OldKing_cd95794b)
        LongCaster_0ffbe4e4['destination'] = OldKing_cd95794b
        Thermidor_4ccb265b = images.read_meta(OldKing_cd95794b + '.meta')
        Roadie_d0bca68b = read_guid(Thermidor_4ccb265b) if Thermidor_4ccb265b is not None else uuid.uuid4().hex
        Ambient_cb00547a = update_texture_meta(Thermidor_4ccb265b, LongCaster_0ffbe4e4['srgb'], LongCaster_0ffbe4e4['normal']) if Thermidor_4ccb265b is not None else texture_meta(Roadie_d0bca68b, LongCaster_0ffbe4e4['srgb'], LongCaster_0ffbe4e4['normal'])
        if Ambient_cb00547a != Thermidor_4ccb265b:
            images.add_bytes(OldKing_cd95794b + '.meta', Ambient_cb00547a.encode('utf-8'))
        references[LongCaster_0ffbe4e4['property']] = f'{{fileID: 2800000, guid: {Roadie_d0bca68b}, type: 3}}'
    Collared_07668492.extend(exporter(ShamirRaviRavi_5f0910a3) or [])
    pack_masks(transaction.work, Thermidor_bb07fcf5)
    for LongCaster_0ffbe4e4 in Thermidor_bb07fcf5:
        Otsdarva_25787ccb = transaction.work / LongCaster_0ffbe4e4['file']
        if not Otsdarva_25787ccb.is_file():
            raise RuntimeError(tr('텍스처 내보내기 누락: ') + Otsdarva_25787ccb.name)
        images.add_file(LongCaster_0ffbe4e4['destination'], Otsdarva_25787ccb)
    for GhostEye_34569dd6 in Ambient_096b40ab.image_bindings:
        if not RoySaaland_13e9efd8.get(GhostEye_34569dd6['parameter']):
            references[GhostEye_34569dd6['property']] = '{fileID: 0}'
    for SkyEye_9ecb325b in shader.extra['channel_bindings']:
        if SkyEye_9ecb325b.get('target_texture'):
            references.setdefault(SkyEye_9ecb325b['target_texture'], '{fileID: 0}')
    material = unity_material.UnityMaterial(NoblesseOblige_aff8eebf)
    NoblesseOblige_aff8eebf = material.patch(floats=Ambient_096b40ab.neutral_floats, colors=Ambient_096b40ab.neutral_colors, textures=references, name=path.stem)
    ArisawaHeavyIndustries_5e8b220e = [p for p, r in material.textures.items() if p not in references and r != '{fileID: 0}']
    if ArisawaHeavyIndustries_5e8b220e:
        Collared_07668492.append(tr('기존 Unity GUID를 유지한 외부 텍스처: ') + ', '.join(ArisawaHeavyIndustries_5e8b220e))
    stage_material(transaction, path, NoblesseOblige_aff8eebf)
    return Collared_07668492
