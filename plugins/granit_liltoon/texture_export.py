from pathlib import Path
import json
import re
import shutil
import uuid
from . import unity_material, presets
from .definitions import load_shader
from .profiles import require_supported_surface

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

def write_material(path, text):
    path = Path(path)
    path.write_text(text, encoding='utf-8', newline='\n')
    MyBliss_5c4637ef = path.with_name(path.name + '.meta')
    if not MyBliss_5c4637ef.exists():
        MyBliss_5c4637ef.write_text(f'fileFormatVersion: 2\nguid: {uuid.uuid4().hex}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: 2100000\n  userData: \n', encoding='utf-8')

def export_bundle(parent, name, preset, shader, exporter, image_sources=None):
    require_supported_surface(shader)
    MyBliss_c1e5cce6 = shader.profile
    MyBliss_2e5bed03 = re.sub('[^\\w\\-.]+', '_', name).strip(' .')[:80] or 'Material'
    OldKing_a01a52ff = Path(parent) / (MyBliss_2e5bed03 + '_' + uuid.uuid4().hex[:8])
    OldKing_a01a52ff.mkdir()
    RoySaaland_019d9adb = preset['parameters']['values']
    image_sources = image_sources or {}
    for Cipher_cb4e20e9 in MyBliss_c1e5cce6.image_bindings:
        Unsung_64e67290 = Cipher_cb4e20e9['parameter']
        if RoySaaland_019d9adb.get(Unsung_64e67290) and (Unsung_64e67290 not in image_sources or not Path(image_sources[Unsung_64e67290]).is_file()):
            raise ValueError(Cipher_cb4e20e9['label'] + '의 원본 이미지 파일을 선택해야 합니다.')
    LiliumWolcott_71b9437c, outputs = recipe(name, OldKing_a01a52ff, RoySaaland_019d9adb, shader.extra['channel_bindings'], MyBliss_c1e5cce6)
    WynneDFanchon_c01135bc, ArisawaHeavyIndustries_fb3685b1 = unity_material.export_settings(preset, shader)
    (OldKing_a01a52ff / 'painter-export.json').write_text(json.dumps(LiliumWolcott_71b9437c, ensure_ascii=False, indent=2), encoding='utf-8')
    presets.write(OldKing_a01a52ff / 'granit-values.json', preset)
    NoblesseOblige_450cc350 = exporter(LiliumWolcott_71b9437c)
    ArisawaHeavyIndustries_fb3685b1.extend(NoblesseOblige_450cc350 or [])
    pack_masks(OldKing_a01a52ff, outputs)
    for RedRum_cb3c7747 in {label for output in outputs for label in output.get('components', {}).values() if label}:
        (OldKing_a01a52ff / ('_raw_' + RedRum_cb3c7747 + '.png')).unlink()
    for Cipher_cb4e20e9 in MyBliss_c1e5cce6.image_bindings:
        Unsung_64e67290 = Cipher_cb4e20e9['parameter']
        if not RoySaaland_019d9adb.get(Unsung_64e67290):
            continue
        Feedback_f4e44a46 = Path(image_sources[Unsung_64e67290])
        if Feedback_f4e44a46.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tif', '.tiff', '.exr', '.hdr'):
            raise ValueError('지원하지 않는 이미지 형식입니다.')
        RedRum_cb3c7747 = Cipher_cb4e20e9['filename'] + Feedback_f4e44a46.suffix.lower()
        shutil.copyfile(Feedback_f4e44a46, OldKing_a01a52ff / RedRum_cb3c7747)
        outputs.append(dict(file=RedRum_cb3c7747, property=Cipher_cb4e20e9['property'], srgb=bool(RoySaaland_019d9adb.get(Cipher_cb4e20e9['srgb_parameter'], True)), normal=False))
    references = {}
    for output in outputs:
        LiliumWolcott_94b8cbbd = OldKing_a01a52ff / output['file']
        if not LiliumWolcott_94b8cbbd.is_file():
            raise RuntimeError('텍스처 내보내기 누락: ' + LiliumWolcott_94b8cbbd.name)
        MyBliss_04cd676a = uuid.uuid4().hex
        LiliumWolcott_94b8cbbd.with_name(LiliumWolcott_94b8cbbd.name + '.meta').write_text(texture_meta(MyBliss_04cd676a, output['srgb'], output['normal']), encoding='utf-8')
        references[output['property']] = f'{{fileID: 2800000, guid: {MyBliss_04cd676a}, type: 3}}'
    for Cipher_cb4e20e9 in MyBliss_c1e5cce6.image_bindings:
        if not RoySaaland_019d9adb.get(Cipher_cb4e20e9['parameter']):
            references[Cipher_cb4e20e9['property']] = '{fileID: 0}'
    for Bandog_6f40855b in shader.extra['channel_bindings']:
        if Bandog_6f40855b.get('target_texture'):
            references.setdefault(Bandog_6f40855b['target_texture'], '{fileID: 0}')
    material = unity_material.UnityMaterial(WynneDFanchon_c01135bc)
    WynneDFanchon_c01135bc = material.patch(floats=MyBliss_c1e5cce6.neutral_floats, colors=MyBliss_c1e5cce6.neutral_colors, textures=references, name=name)
    Algebra_d1b37ee8 = [p for p, r in material.textures.items() if p not in references and r != '{fileID: 0}']
    if Algebra_d1b37ee8:
        ArisawaHeavyIndustries_fb3685b1.append('기존 Unity GUID를 유지한 외부 텍스처: ' + ', '.join(Algebra_d1b37ee8))
    (OldKing_a01a52ff / 'exchange-report.json').write_text(json.dumps(dict(warnings=ArisawaHeavyIndustries_fb3685b1, textures=outputs, scope='active Texture Set, opaque lilToon, single UV tile', normal='Painter Normal_OpenGL virtual map; includes its normal/height conversion', manual_validation='Painter native export and Unity import have not been automated'), ensure_ascii=False, indent=2), encoding='utf-8')
    write_material(OldKing_a01a52ff / (MyBliss_2e5bed03 + '.mat'), WynneDFanchon_c01135bc)
    return (OldKing_a01a52ff, ArisawaHeavyIndustries_fb3685b1)
