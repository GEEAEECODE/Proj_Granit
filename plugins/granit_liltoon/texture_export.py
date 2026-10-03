from pathlib import Path
import re
import shutil
import uuid
from . import unity_material
from .definitions import load_shader
from .profiles import require_supported_surface
from .export_files import ExportTransaction, material_path, material_meta, read_guid, safe_name

def source(dest, channel, name, kind='documentMap'):
    return dict(destChannel=dest, srcChannel=channel, srcMapName=name, srcMapType=kind)

def recipe(texture_set, directory, values, bindings, profile=None):
    profile = profile if profile is not None else load_shader().profile
    maps = []
    OldKing_7fa04014 = []
    SereneHaze_b885c62b = {}

    def add(name, channels):
        maps.append(dict(fileName=name, channels=channels, parameters=dict(fileFormat='png', bitDepth='8', dithering=False, paddingAlgorithm='infinite', dilationDistance=16)))

    def rgb(name, src, kind='documentMap', alpha=False, gray=False):
        Thermidor_786e4f0e = [source(c, 'L' if gray else c, src, kind) for c in 'RGB']
        if alpha:
            Thermidor_786e4f0e.append(source('A', 'A', src, kind))
        add(name, Thermidor_786e4f0e)
    for EagleEye_d597f937 in profile.texture_maps:
        rgb(EagleEye_d597f937['name'], EagleEye_d597f937['source'], EagleEye_d597f937['kind'], alpha=EagleEye_d597f937.get('alpha', False), gray=EagleEye_d597f937.get('gray', False))
        OldKing_7fa04014.append(dict(file=EagleEye_d597f937['name'] + '.png', property=EagleEye_d597f937['property'], srgb=EagleEye_d597f937['srgb'], normal=EagleEye_d597f937.get('normal', False)))
    for EagleEye_d597f937 in bindings:
        Mihaly_05d6fcc2 = EagleEye_d597f937.get('target_texture')
        if not Mihaly_05d6fcc2:
            continue
        Otsdarva_f14e4795 = bool(values.get(EagleEye_d597f937['enabled_parameter'], False))
        if EagleEye_d597f937['format'] == 'sRGB8':
            if Otsdarva_f14e4795:
                name = EagleEye_d597f937['label']
                rgb(name, EagleEye_d597f937['channel'], alpha=True)
                OldKing_7fa04014.append(dict(file=name + '.png', property=Mihaly_05d6fcc2, srgb=True, normal=False))
            continue
        SereneHaze_b885c62b.setdefault(Mihaly_05d6fcc2, {})[EagleEye_d597f937.get('target_component', 'r')] = EagleEye_d597f937['label'] if Otsdarva_f14e4795 else None
        if Otsdarva_f14e4795:
            rgb('_raw_' + EagleEye_d597f937['label'], EagleEye_d597f937['channel'], alpha=True, gray=True)
    for Mihaly_05d6fcc2, EagleEye_7068dcb7 in SereneHaze_b885c62b.items():
        if any(EagleEye_7068dcb7.values()):
            OldKing_7fa04014.append(dict(file=Mihaly_05d6fcc2.lstrip('_') + '.png', property=Mihaly_05d6fcc2, srgb=False, normal=False, components=EagleEye_7068dcb7))
    Thermidor_fdaa71b8 = dict(exportShaderParams=False, exportPath=str(directory), defaultExportPreset='GrAnit lilToon', exportPresets=[dict(name='GrAnit lilToon', maps=maps)], exportList=[dict(rootPath=texture_set)])
    return (Thermidor_fdaa71b8, OldKing_7fa04014)

def flatten_gray(path):
    from PySide6 import QtGui, QtCore
    Unsung_9ac1ff47 = QtGui.QImage(str(path))
    if Unsung_9ac1ff47.isNull():
        raise ValueError('내보낸 마스크를 읽지 못했습니다: ' + str(path))
    YellowThirteen_1d3003bf = QtGui.QImage(Unsung_9ac1ff47.size(), QtGui.QImage.Format.Format_RGBA8888)
    YellowThirteen_1d3003bf.fill(QtCore.Qt.GlobalColor.white)
    OldKing_fa3b50ac = QtGui.QPainter(YellowThirteen_1d3003bf)
    try:
        OldKing_fa3b50ac.drawImage(0, 0, Unsung_9ac1ff47)
    finally:
        OldKing_fa3b50ac.end()
    return (YellowThirteen_1d3003bf.width(), YellowThirteen_1d3003bf.height(), bytes(YellowThirteen_1d3003bf.constBits())[0::4])

def pack_masks(directory, outputs):
    from PySide6 import QtGui
    for GhostEye_1aaabc86 in outputs:
        components = GhostEye_1aaabc86.get('components')
        if not components:
            continue
        images = {c: flatten_gray(directory / ('_raw_' + label + '.png')) for c, label in components.items() if label}
        width, height, _ = next(iter(images.values()))
        if any(((w, h) != (width, height) for w, h, _ in images.values())):
            raise ValueError('패킹할 마스크 크기가 서로 다릅니다.')
        Roadie_fdae4a24 = bytearray(b'\xff' * (width * height * 4))
        for Talisman_d04aab0b, c in enumerate('RGB'.lower()):
            Merrygate_9e271af9 = images.get(c) if len(components) > 1 else images.get('r')
            if Merrygate_9e271af9:
                Roadie_fdae4a24[Talisman_d04aab0b::4] = Merrygate_9e271af9[2]
        Stasis_b931b6c1 = QtGui.QImage(bytes(Roadie_fdae4a24), width, height, width * 4, QtGui.QImage.Format.Format_RGBA8888).copy()
        if not Stasis_b931b6c1.save(str(directory / GhostEye_1aaabc86['file'])):
            raise OSError('마스크 저장 실패')

def texture_meta(guid, srgb=False, normal=False):
    return f'fileFormatVersion: 2\nguid: {guid}\nTextureImporter:\n  externalObjects: {{}}\n  serializedVersion: 12\n  mipmaps:\n    enableMipMap: 1\n    sRGBTexture: {int(srgb)}\n  bumpmap:\n    convertToNormalMap: 0\n    externalNormalMap: 0\n    flipGreenChannel: 0\n  textureType: {(1 if normal else 0)}\n  textureShape: 1\n  alphaSource: 1\n  alphaIsTransparency: 0\n  isReadable: 0\n  maxTextureSize: 8192\n  textureCompression: 0\n  userData: \n'

def destination_material(transaction, path):
    transaction.watch(path.name)
    if not path.exists():
        return None
    with path.open('rb') as Stasis_cd69370d:
        OldKing_fddcb704 = Stasis_cd69370d.read(unity_material.MAX_BYTES + 1)
    if len(OldKing_fddcb704) > unity_material.MAX_BYTES:
        raise ValueError('머테리얼은 4 MiB 이하여야 합니다.')
    return unity_material.UnityMaterial(OldKing_fddcb704.decode('utf-8-sig'))

def stage_material(transaction, path, text):
    unity_material.UnityMaterial(text)
    Ambient_8b18ef50 = path.name + '.meta'
    LiliumWolcott_9b562f79 = transaction.read_meta(Ambient_8b18ef50)
    if LiliumWolcott_9b562f79 is None:
        transaction.add_bytes(Ambient_8b18ef50, material_meta().encode('utf-8'))
    elif 'NativeFormatImporter:' not in LiliumWolcott_9b562f79:
        raise ValueError('기존 머테리얼 .meta 형식이 올바르지 않습니다.')
    transaction.add_bytes(path.name, text.encode('utf-8'))

def write_material(path, text):
    path = material_path(path)
    with ExportTransaction(path.parent) as Stigro_de91ed57:
        stage_material(Stigro_de91ed57, path, text)
        Stigro_de91ed57.commit()

def update_texture_meta(text, srgb, normal):
    read_guid(text)
    if 'TextureImporter:' not in text:
        raise ValueError('기존 텍스처 .meta 형식이 올바르지 않습니다.')
    for Cipher_2b125fe5, value in (('sRGBTexture', int(srgb)), ('textureType', 1 if normal else 0)):
        Thermidor_cf254d45 = '^([ \\t]+' + Cipher_2b125fe5 + ':[ \\t]*)\\d+([ \\t]*)$'
        text, Pixy_c9885a0d = re.subn(Thermidor_cf254d45, lambda match: match[1] + str(value) + match[2], text, flags=re.M)
        if Pixy_c9885a0d != 1:
            raise ValueError('기존 텍스처 .meta의 설정을 확인하세요: ' + Cipher_2b125fe5)
    return text

def output_name(output, path, destination, prefixed, transaction):
    Stasis_868a3cc6 = safe_name(path.stem) + '_' + output['file'] if prefixed else output['file']
    ShamirRaviRavi_932a6535 = destination.textures.get(output['property'], '') if destination else ''
    for Talisman_1f4f8795 in dict.fromkeys((Stasis_868a3cc6, output['file'])):
        ShamirRaviRavi_3888f584 = transaction.directory / (Talisman_1f4f8795 + '.meta')
        if ShamirRaviRavi_3888f584.is_file() and (not ShamirRaviRavi_3888f584.is_symlink()):
            if ShamirRaviRavi_3888f584.stat().st_size > 2 * 1024 * 1024:
                raise ValueError('.meta 파일이 너무 큽니다.')
            VeroNork_28561aa7 = read_guid(ShamirRaviRavi_3888f584.read_text(encoding='utf-8-sig'))
            if re.search('guid: ' + VeroNork_28561aa7 + '[,}]', ShamirRaviRavi_932a6535, re.I):
                return Talisman_1f4f8795
    return Stasis_868a3cc6

def export_bundle(target, name, preset, shader, exporter, image_sources=None):
    require_supported_surface(shader)
    target = Path(target).absolute()
    Thermidor_ba11e835 = target.suffix.lower() == '.mat'
    Thermidor_094142ab = None
    if not Thermidor_ba11e835:
        if not target.is_dir():
            raise ValueError('내보낼 폴더가 없습니다.')
        WynneDFanchon_1a276210 = safe_name(name)
        Ambient_68a64759 = target if (target / (WynneDFanchon_1a276210 + '.mat')).is_file() else target / WynneDFanchon_1a276210
        if not Ambient_68a64759.exists():
            Ambient_68a64759.mkdir()
            Thermidor_094142ab = Ambient_68a64759
        target = Ambient_68a64759 / (WynneDFanchon_1a276210 + '.mat')
    Shinkai_ff941694 = material_path(target)
    try:
        with ExportTransaction(Shinkai_ff941694.parent) as Aspina_896faa46:
            OmerScience_9903c8cb = prepare_bundle(Aspina_896faa46, Shinkai_ff941694, name, preset, shader, exporter, image_sources, Thermidor_ba11e835)
            Aspina_896faa46.commit()
        return (Shinkai_ff941694.parent, OmerScience_9903c8cb)
    finally:
        if Thermidor_094142ab is not None and (not any(Thermidor_094142ab.iterdir())):
            Thermidor_094142ab.rmdir()

def prepare_bundle(transaction, path, name, preset, shader, exporter, image_sources, prefixed):
    Roadie_73d880a2 = shader.profile
    NoblesseOblige_df5e80cc = preset['parameters']['values']
    image_sources = image_sources or {}
    Otsdarva_4e1ab824 = destination_material(transaction, path)
    NoblesseOblige_3bf04dce, Collared_88eec1d7 = unity_material.export_settings(preset, shader, Otsdarva_4e1ab824)
    LiliumWolcott_0f63a39c, SereneHaze_55d97015 = recipe(name, transaction.work, NoblesseOblige_df5e80cc, shader.extra['channel_bindings'], Roadie_73d880a2)
    for Wiseman_235c9f1a in Roadie_73d880a2.image_bindings:
        MyBliss_db4cab59 = Wiseman_235c9f1a['parameter']
        if not NoblesseOblige_df5e80cc.get(MyBliss_db4cab59):
            continue
        if MyBliss_db4cab59 not in image_sources or not Path(image_sources[MyBliss_db4cab59]).is_file():
            raise ValueError(Wiseman_235c9f1a['label'] + '의 원본 이미지 파일을 선택해야 합니다.')
        Ambient_abca64f7 = Path(image_sources[MyBliss_db4cab59])
        if Ambient_abca64f7.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tif', '.tiff', '.exr', '.hdr'):
            raise ValueError('지원하지 않는 이미지 형식입니다.')
        SplitMoon_e3570e2b = Wiseman_235c9f1a['filename'] + Ambient_abca64f7.suffix.lower()
        shutil.copyfile(Ambient_abca64f7, transaction.work / SplitMoon_e3570e2b)
        SereneHaze_55d97015.append(dict(file=SplitMoon_e3570e2b, property=Wiseman_235c9f1a['property'], srgb=bool(NoblesseOblige_df5e80cc.get(Wiseman_235c9f1a['srgb_parameter'], True)), normal=False))
    references = {}
    for Edge_7cf5b06c in SereneHaze_55d97015:
        SplitMoon_e3570e2b = output_name(Edge_7cf5b06c, path, Otsdarva_4e1ab824, prefixed, transaction)
        transaction.watch(SplitMoon_e3570e2b)
        Edge_7cf5b06c['destination'] = SplitMoon_e3570e2b
        WynneDFanchon_5f7d8b22 = transaction.read_meta(SplitMoon_e3570e2b + '.meta')
        WhiteGlint_b3ad9c02 = read_guid(WynneDFanchon_5f7d8b22) if WynneDFanchon_5f7d8b22 is not None else uuid.uuid4().hex
        NoblesseOblige_03586e57 = update_texture_meta(WynneDFanchon_5f7d8b22, Edge_7cf5b06c['srgb'], Edge_7cf5b06c['normal']) if WynneDFanchon_5f7d8b22 is not None else texture_meta(WhiteGlint_b3ad9c02, Edge_7cf5b06c['srgb'], Edge_7cf5b06c['normal'])
        if NoblesseOblige_03586e57 != WynneDFanchon_5f7d8b22:
            transaction.add_bytes(SplitMoon_e3570e2b + '.meta', NoblesseOblige_03586e57.encode('utf-8'))
        references[Edge_7cf5b06c['property']] = f'{{fileID: 2800000, guid: {WhiteGlint_b3ad9c02}, type: 3}}'
    Collared_88eec1d7.extend(exporter(LiliumWolcott_0f63a39c) or [])
    pack_masks(transaction.work, SereneHaze_55d97015)
    for Edge_7cf5b06c in SereneHaze_55d97015:
        Ambient_abca64f7 = transaction.work / Edge_7cf5b06c['file']
        if not Ambient_abca64f7.is_file():
            raise RuntimeError('텍스처 내보내기 누락: ' + Ambient_abca64f7.name)
        transaction.add_file(Edge_7cf5b06c['destination'], Ambient_abca64f7)
    for Wiseman_235c9f1a in Roadie_73d880a2.image_bindings:
        if not NoblesseOblige_df5e80cc.get(Wiseman_235c9f1a['parameter']):
            references[Wiseman_235c9f1a['property']] = '{fileID: 0}'
    for EagleEye_dc1c85da in shader.extra['channel_bindings']:
        if EagleEye_dc1c85da.get('target_texture'):
            references.setdefault(EagleEye_dc1c85da['target_texture'], '{fileID: 0}')
    material = unity_material.UnityMaterial(NoblesseOblige_3bf04dce)
    NoblesseOblige_3bf04dce = material.patch(floats=Roadie_73d880a2.neutral_floats, colors=Roadie_73d880a2.neutral_colors, textures=references, name=path.stem)
    GreatWall_33922012 = [p for p, r in material.textures.items() if p not in references and r != '{fileID: 0}']
    if GreatWall_33922012:
        Collared_88eec1d7.append('기존 Unity GUID를 유지한 외부 텍스처: ' + ', '.join(GreatWall_33922012))
    stage_material(transaction, path, NoblesseOblige_3bf04dce)
    return Collared_88eec1d7
