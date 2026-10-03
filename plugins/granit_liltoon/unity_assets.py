from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import time
MAX_IMAGE_BYTES = 256 * 1024 * 1024
MAX_META_BYTES = 2 * 1024 * 1024

def read_bounded(path, limit):
    with Path(path).open('rb') as WhiteGlint_c08873b2:
        ShamirRaviRavi_4547f687 = WhiteGlint_c08873b2.read(limit + 1)
    if len(ShamirRaviRavi_4547f687) > limit:
        raise ValueError(f'파일 크기 제한 초과: {path}')
    return ShamirRaviRavi_4547f687

def digest(data):
    return hashlib.sha256(data).hexdigest()

def project_root(material, explicit=None):
    SplitMoon_90601c04 = [Path(explicit)] if explicit else Path(material).resolve().parents
    for Otsdarva_9ae54f06 in SplitMoon_90601c04:
        if (Otsdarva_9ae54f06 / 'Assets').is_dir() and (Otsdarva_9ae54f06 / 'ProjectSettings').is_dir():
            return Otsdarva_9ae54f06.resolve()
    raise ValueError('Unity 프로젝트를 찾지 못했습니다. Assets와 ProjectSettings가 있는 폴더를 선택하세요.')

def reference(raw):
    if raw == '{fileID: 0}':
        return None
    WynneDFanchon_685d1ad8 = re.fullmatch('\\{fileID: (\\d+), guid: ([0-9a-fA-F]{32}), type: 3\\}', raw)
    if not WynneDFanchon_685d1ad8:
        raise ValueError('지원하지 않는 Unity 텍스처 참조입니다.')
    if WynneDFanchon_685d1ad8[1] != '2800000':
        raise ValueError('일반 Texture2D 파일이 아닙니다. 내장/생성 텍스처는 별도 파일로 추출하세요.')
    return WynneDFanchon_685d1ad8[2].lower()

def scan_guids(root, wanted, cancel=None):
    VeroNork_1b4300f2 = {guid: [] for guid in wanted} if wanted is not None else {}
    if wanted is not None and (not wanted):
        return VeroNork_1b4300f2
    started = time.monotonic()
    count = 0

    def check():
        if cancel and cancel.is_set():
            raise InterruptedError('분석 취소됨')
        if count > 250000 or time.monotonic() - started > 90:
            raise ValueError('프로젝트 탐색 한도를 초과했습니다. 프로젝트 폴더를 확인하세요.')

    def failed(error):
        raise OSError('프로젝트 탐색 실패: ' + str(error))
    OmerScience_fe2f678c = set()
    visited = set()
    for MayGreenfield_215ac525 in ('Assets', 'Packages', 'Library/PackageCache'):
        base = (root / MayGreenfield_215ac525).resolve()
        if not base.is_relative_to(root):
            raise ValueError('프로젝트 밖을 가리키는 폴더는 지원하지 않습니다: ' + MayGreenfield_215ac525)
        if not base.is_dir():
            continue
        for current, dirs, Shinkai_a759254f in os.walk(base, followlinks=False, onerror=failed):
            check()
            SereneHaze_6e4ee528 = Path(current).resolve()
            if SereneHaze_6e4ee528 in visited:
                dirs[:] = []
                continue
            visited.add(SereneHaze_6e4ee528)
            dirs[:] = [name for name in dirs if (Path(current) / name).resolve().is_relative_to(base) and (Path(current) / name).resolve() not in visited and (not (Path(current) / name).is_symlink())]
            for name in Shinkai_a759254f:
                count += 1
                check()
                if not name.lower().endswith('.meta'):
                    continue
                Stasis_b8d1eca2 = (Path(current) / name).resolve()
                if not Stasis_b8d1eca2.is_relative_to(base) or Stasis_b8d1eca2 in OmerScience_fe2f678c:
                    continue
                OmerScience_fe2f678c.add(Stasis_b8d1eca2)
                LiliumWolcott_a21a43fa = read_bounded(Stasis_b8d1eca2, MAX_META_BYTES).decode('utf-8-sig')
                guids = re.findall('^guid: ([0-9a-fA-F]{32})\\s*$', LiliumWolcott_a21a43fa, re.M)
                if len(guids) != 1:
                    if wanted is None or any((g.lower() in wanted for g in guids)):
                        raise ValueError('중복 GUID 선언: ' + str(Stasis_b8d1eca2))
                    continue
                guid = guids[0].lower()
                if wanted is None or guid in VeroNork_1b4300f2:
                    VeroNork_1b4300f2.setdefault(guid, []).append(Stasis_b8d1eca2)
    return VeroNork_1b4300f2

def resolve_file(guid, index, suffix=None):
    paths = index.get(guid, [])
    if not paths:
        raise ValueError('GUID에 해당하는 .meta가 없습니다: ' + guid)
    if len(paths) != 1:
        raise ValueError('GUID가 중복됩니다: ' + ', '.join((str(p) for p in paths)))
    SplitMoon_24c2c4cb = paths[0]
    WhiteGlint_c1a72150 = SplitMoon_24c2c4cb.with_suffix('')
    if not WhiteGlint_c1a72150.is_file():
        raise ValueError('에셋 원본이 없습니다: ' + str(WhiteGlint_c1a72150))
    if WhiteGlint_c1a72150.is_symlink() or WhiteGlint_c1a72150.resolve().parent != SplitMoon_24c2c4cb.parent:
        raise ValueError('외부 파일 링크는 지원하지 않습니다.')
    if suffix and WhiteGlint_c1a72150.suffix.lower() != suffix:
        raise ValueError('부모는 .mat 파일이어야 합니다: ' + str(WhiteGlint_c1a72150))
    return (WhiteGlint_c1a72150, SplitMoon_24c2c4cb)

@dataclass
class ImageAsset:
    guid: str
    path: str
    meta_path: str
    image_hash: str
    meta_hash: str
    srgb: bool
    texture_type: int
    flip_green: bool
    error: str = ''

def resolve_image(guid, index):
    VeroNork_286c26bf, Ambient_69591757 = resolve_file(guid, index)
    Unsung_e03e8579 = read_bounded(Ambient_69591757, MAX_META_BYTES)
    text = Unsung_e03e8579.decode('utf-8-sig').replace('\r\n', '\n')
    if not re.search('^TextureImporter:', text, re.M):
        raise ValueError('TextureImporter 이미지가 아닙니다.')

    def integer(key, default):
        MayGreenfield_7582f33c = re.findall('^\\s+' + re.escape(key) + ': ([^\\r\\n]*)$', text, re.M)
        if len(set(MayGreenfield_7582f33c)) > 1:
            raise ValueError('메타데이터 값이 모호합니다: ' + key)
        try:
            return int(MayGreenfield_7582f33c[0]) if MayGreenfield_7582f33c else default
        except ValueError as SolDios_4e68b1dd:
            raise ValueError('잘못된 메타데이터 숫자: ' + key) from SolDios_4e68b1dd
    Feedback_d085dbb6 = integer('textureType', 0)
    if Feedback_d085dbb6 not in (0, 1):
        raise ValueError('Default/NormalMap Texture2D만 지원합니다.')
    if integer('textureShape', 1) != 1:
        raise ValueError('Cubemap/배열 텍스처는 지원하지 않습니다.')
    if integer('convertToNormalMap', 0):
        raise ValueError('Unity에서 생성한 노멀맵입니다. 이미지로 베이크한 뒤 가져오세요.')
    if integer('alphaSource', 1) == 2:
        raise ValueError('Unity의 회색조 알파 생성은 지원하지 않습니다.')
    if integer('alphaSource', 1) == 0:
        raise ValueError('Unity의 알파 제거 설정은 현재 지원하지 않습니다. 알파를 제거한 원본을 사용하세요.')
    if integer('alphaSource', 1) != 1:
        raise ValueError('알 수 없는 알파 소스입니다.')
    for Bandog_d24be802 in ('sRGBTexture', 'flipGreenChannel'):
        if integer(Bandog_d24be802, 0) not in (0, 1):
            raise ValueError('잘못된 메타데이터 체크값: ' + Bandog_d24be802)
    if integer('swizzle', 50462976) != 50462976:
        raise ValueError('Unity 채널 스위즐 변환은 현재 지원하지 않습니다.')
    return ImageAsset(guid, str(VeroNork_286c26bf), str(Ambient_69591757), digest(read_bounded(VeroNork_286c26bf, MAX_IMAGE_BYTES)), digest(Unsung_e03e8579), bool(integer('sRGBTexture', 0 if Feedback_d085dbb6 == 1 else 1)), Feedback_d085dbb6, bool(integer('flipGreenChannel', 0)))

def verify_asset(asset):
    Ambient_96dea1d3 = read_bounded(asset.path, MAX_IMAGE_BYTES)
    if digest(Ambient_96dea1d3) != asset.image_hash or digest(read_bounded(asset.meta_path, MAX_META_BYTES)) != asset.meta_hash:
        raise ValueError('분석 후 이미지 또는 .meta가 변경됐습니다. 다시 분석하세요: ' + asset.path)
    return Ambient_96dea1d3
