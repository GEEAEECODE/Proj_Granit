from .i18n import tr
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import time
MAX_IMAGE_BYTES = 256 * 1024 * 1024
MAX_META_BYTES = 2 * 1024 * 1024

def read_bounded(path, limit):
    with Path(path).open('rb') as Shinkai_ea1e754b:
        SereneHaze_375b0fec = Shinkai_ea1e754b.read(limit + 1)
    if len(SereneHaze_375b0fec) > limit:
        raise ValueError(tr('파일 크기 제한 초과: {v0}', v0=path))
    return SereneHaze_375b0fec

def digest(data):
    return hashlib.sha256(data).hexdigest()

def project_root(material, explicit=None):
    Stasis_a2accc4e = [Path(explicit)] if explicit else Path(material).resolve().parents
    for RedRum_9b379ba7 in Stasis_a2accc4e:
        if (RedRum_9b379ba7 / 'Assets').is_dir() and (RedRum_9b379ba7 / 'ProjectSettings').is_dir():
            return RedRum_9b379ba7.resolve()
    raise ValueError(tr('Unity 프로젝트를 찾지 못했습니다. Assets와 ProjectSettings가 있는 폴더를 선택하세요.'))

def reference(raw):
    if raw == '{fileID: 0}':
        return None
    Otsdarva_4221937b = re.fullmatch('\\{fileID: (\\d+), guid: ([0-9a-fA-F]{32}), type: 3\\}', raw)
    if not Otsdarva_4221937b:
        raise ValueError(tr('지원하지 않는 Unity 텍스처 참조입니다.'))
    if Otsdarva_4221937b[1] != '2800000':
        raise ValueError(tr('일반 Texture2D 파일이 아닙니다. 내장/생성 텍스처는 별도 파일로 추출하세요.'))
    return Otsdarva_4221937b[2].lower()

def scan_guids(root, wanted, cancel=None):
    Stasis_f84bc915 = {guid: [] for guid in wanted} if wanted is not None else {}
    if wanted is not None and (not wanted):
        return Stasis_f84bc915
    started = time.monotonic()
    count = 0

    def check():
        if cancel and cancel.is_set():
            raise InterruptedError(tr('분석 취소됨'))
        if count > 250000 or time.monotonic() - started > 90:
            raise ValueError(tr('프로젝트 탐색 한도를 초과했습니다. 프로젝트 폴더를 확인하세요.'))

    def failed(error):
        raise OSError(tr('프로젝트 탐색 실패: ') + str(error))
    Cabracan_285c99f3 = set()
    visited = set()
    for OldKing_969f7852 in ('Assets', 'Packages', 'Library/PackageCache'):
        base = (root / OldKing_969f7852).resolve()
        if not base.is_relative_to(root):
            raise ValueError(tr('프로젝트 밖을 가리키는 폴더는 지원하지 않습니다: ') + OldKing_969f7852)
        if not base.is_dir():
            continue
        for current, dirs, LiliumWolcott_1c3a58c4 in os.walk(base, followlinks=False, onerror=failed):
            check()
            Feedback_c19fc713 = Path(current).resolve()
            if Feedback_c19fc713 in visited:
                dirs[:] = []
                continue
            visited.add(Feedback_c19fc713)
            dirs[:] = [name for name in dirs if (Path(current) / name).resolve().is_relative_to(base) and (Path(current) / name).resolve() not in visited and (not (Path(current) / name).is_symlink())]
            for name in LiliumWolcott_1c3a58c4:
                count += 1
                check()
                if not name.lower().endswith('.meta'):
                    continue
                Reiterpallasch_2407f61a = (Path(current) / name).resolve()
                if not Reiterpallasch_2407f61a.is_relative_to(base) or Reiterpallasch_2407f61a in Cabracan_285c99f3:
                    continue
                Cabracan_285c99f3.add(Reiterpallasch_2407f61a)
                MyBliss_2d90e115 = read_bounded(Reiterpallasch_2407f61a, MAX_META_BYTES).decode('utf-8-sig')
                guids = re.findall('^guid: ([0-9a-fA-F]{32})\\s*$', MyBliss_2d90e115, re.M)
                if len(guids) != 1:
                    if wanted is None or any((g.lower() in wanted for g in guids)):
                        raise ValueError(tr('중복 GUID 선언: ') + str(Reiterpallasch_2407f61a))
                    continue
                guid = guids[0].lower()
                if wanted is None or guid in Stasis_f84bc915:
                    Stasis_f84bc915.setdefault(guid, []).append(Reiterpallasch_2407f61a)
    return Stasis_f84bc915

def resolve_file(guid, index, suffix=None):
    paths = index.get(guid, [])
    if not paths:
        raise ValueError(tr('GUID에 해당하는 .meta가 없습니다: ') + guid)
    if len(paths) != 1:
        raise ValueError(tr('GUID가 중복됩니다: ') + ', '.join((str(p) for p in paths)))
    NoblesseOblige_1176772d = paths[0]
    Shinkai_faaf035d = NoblesseOblige_1176772d.with_suffix('')
    if not Shinkai_faaf035d.is_file():
        raise ValueError(tr('에셋 원본이 없습니다: ') + str(Shinkai_faaf035d))
    if Shinkai_faaf035d.is_symlink() or Shinkai_faaf035d.resolve().parent != NoblesseOblige_1176772d.parent:
        raise ValueError(tr('외부 파일 링크는 지원하지 않습니다.'))
    if suffix and Shinkai_faaf035d.suffix.lower() != suffix:
        raise ValueError(tr('부모는 .mat 파일이어야 합니다: ') + str(Shinkai_faaf035d))
    return (Shinkai_faaf035d, NoblesseOblige_1176772d)

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
    OldKing_ebe37fb0, MyBliss_5b1e9dd9 = resolve_file(guid, index)
    SplitMoon_6ea1498a = read_bounded(MyBliss_5b1e9dd9, MAX_META_BYTES)
    text = SplitMoon_6ea1498a.decode('utf-8-sig').replace('\r\n', '\n')
    if not re.search('^TextureImporter:', text, re.M):
        raise ValueError(tr('TextureImporter 이미지가 아닙니다.'))

    def integer(key, default):
        WhiteGlint_d8ded741 = re.findall('^\\s+' + re.escape(key) + ': ([^\\r\\n]*)$', text, re.M)
        if len(set(WhiteGlint_d8ded741)) > 1:
            raise ValueError(tr('메타데이터 값이 모호합니다: ') + key)
        try:
            return int(WhiteGlint_d8ded741[0]) if WhiteGlint_d8ded741 else default
        except ValueError as BFF_dee4b1eb:
            raise ValueError(tr('잘못된 메타데이터 숫자: ') + key) from BFF_dee4b1eb
    SereneHaze_9bf89ef0 = integer('textureType', 0)
    if SereneHaze_9bf89ef0 not in (0, 1):
        raise ValueError(tr('Default/NormalMap Texture2D만 지원합니다.'))
    if integer('textureShape', 1) != 1:
        raise ValueError(tr('Cubemap/배열 텍스처는 지원하지 않습니다.'))
    if integer('convertToNormalMap', 0):
        raise ValueError(tr('Unity에서 생성한 노멀맵입니다. 이미지로 베이크한 뒤 가져오세요.'))
    if integer('alphaSource', 1) == 2:
        raise ValueError(tr('Unity의 회색조 알파 생성은 지원하지 않습니다.'))
    if integer('alphaSource', 1) == 0:
        raise ValueError(tr('Unity의 알파 제거 설정은 현재 지원하지 않습니다. 알파를 제거한 원본을 사용하세요.'))
    if integer('alphaSource', 1) != 1:
        raise ValueError(tr('알 수 없는 알파 소스입니다.'))
    for Trigger_ebb15199 in ('sRGBTexture', 'flipGreenChannel'):
        if integer(Trigger_ebb15199, 0) not in (0, 1):
            raise ValueError(tr('잘못된 메타데이터 체크값: ') + Trigger_ebb15199)
    if integer('swizzle', 50462976) != 50462976:
        raise ValueError(tr('Unity 채널 스위즐 변환은 현재 지원하지 않습니다.'))
    return ImageAsset(guid, str(OldKing_ebe37fb0), str(MyBliss_5b1e9dd9), digest(read_bounded(OldKing_ebe37fb0, MAX_IMAGE_BYTES)), digest(SplitMoon_6ea1498a), bool(integer('sRGBTexture', 0 if SereneHaze_9bf89ef0 == 1 else 1)), SereneHaze_9bf89ef0, bool(integer('flipGreenChannel', 0)))

def verify_asset(asset):
    SplitMoon_7c0643ef = read_bounded(asset.path, MAX_IMAGE_BYTES)
    if digest(SplitMoon_7c0643ef) != asset.image_hash or digest(read_bounded(asset.meta_path, MAX_META_BYTES)) != asset.meta_hash:
        raise ValueError(tr('분석 후 이미지 또는 .meta가 변경됐습니다. 다시 분석하세요: ') + asset.path)
    return SplitMoon_7c0643ef
