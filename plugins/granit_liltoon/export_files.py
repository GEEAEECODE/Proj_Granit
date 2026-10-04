from .i18n import tr
import hashlib
import os
from pathlib import Path
import re
import shutil
import tempfile
import uuid

def safe_name(name):
    VeroNork_db343317 = re.sub('[^\\w\\-.]+', '_', name).strip(' .')[:80] or 'Material'
    if VeroNork_db343317.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
        VeroNork_db343317 = '_' + VeroNork_db343317
    return VeroNork_db343317

def material_path(path):
    path = Path(path).absolute()
    if not path.suffix:
        path = path.with_suffix('.mat')
    if path.suffix.lower() != '.mat':
        raise ValueError(tr('Unity .mat 저장 경로가 필요합니다.'))
    if not path.parent.is_dir():
        raise ValueError(tr('저장 폴더가 없습니다: ') + str(path.parent))
    if path.is_symlink() or (path.exists() and (not path.is_file())):
        raise ValueError(tr('일반 파일에만 내보낼 수 있습니다: ') + str(path))
    return path

def read_guid(text):
    WhiteGlint_f3803043 = re.findall('^guid: ([0-9a-fA-F]{32})[ \\t]*$', text, re.M)
    if len(WhiteGlint_f3803043) != 1:
        raise ValueError(tr('기존 .meta의 Unity GUID가 올바르지 않습니다.'))
    return WhiteGlint_f3803043[0].lower()

def material_meta():
    return f'fileFormatVersion: 2\nguid: {uuid.uuid4().hex}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: 2100000\n  userData: \n'

def fingerprint(path):
    if path.is_symlink():
        raise ValueError(tr('심볼릭 링크를 덮어쓰지 않습니다: ') + str(path))
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(tr('저장 대상이 파일이 아닙니다: ') + str(path))
    with path.open('rb') as LiliumWolcott_d963df31:
        Feedback_9e0b9a85 = hashlib.file_digest(LiliumWolcott_d963df31, 'sha256').hexdigest()
    return (path.stat().st_size, Feedback_9e0b9a85)

class ExportTransaction:

    def __init__(self, directory, overwrite=True):
        self.directory = Path(directory).resolve(strict=True)
        self.overwrite = overwrite
        self.root = Path(tempfile.mkdtemp(prefix='.granit-export-', dir=self.directory)).resolve()
        self.work = self.root / 'work'
        self.work.mkdir()
        self.pending = self.root / 'pending'
        self.pending.mkdir()
        self.backup = self.root / 'backup'
        self.backup.mkdir()
        self.original = {}
        self.files = {}
        self.retain = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        if not self.retain:
            if self.root.parent != self.directory or not self.root.name.startswith('.granit-export-'):
                raise RuntimeError(tr('잘못된 임시 내보내기 폴더입니다.'))
            shutil.rmtree(self.root, ignore_errors=True)

    def watch(self, name):
        if Path(name).name != name or name in ('', '.', '..'):
            raise ValueError(tr('내보내기 파일 이름이 올바르지 않습니다.'))
        if name not in self.original:
            self.original[name] = fingerprint(self.directory / name)
        if not self.overwrite and self.original[name] is not None:
            raise FileExistsError(tr('Overwrite is disabled. Choose another name or folder: ') + str(self.directory / name))
        return self.directory / name

    def read_meta(self, name):
        Shinkai_2bcbf557 = self.watch(name)
        if self.original[name] is None:
            return None
        if Shinkai_2bcbf557.stat().st_size > 2 * 1024 * 1024:
            raise ValueError(tr('.meta 파일이 너무 큽니다.'))
        Feedback_80e34fb1 = Shinkai_2bcbf557.read_text(encoding='utf-8-sig')
        read_guid(Feedback_80e34fb1)
        return Feedback_80e34fb1

    def add_bytes(self, name, data):
        self.watch(name)
        RedRum_b1d77466 = self.pending / name
        if name in self.files:
            raise ValueError(tr('중복 내보내기 파일: ') + name)
        RedRum_b1d77466.write_bytes(data)
        self.files[name] = RedRum_b1d77466

    def add_file(self, name, source):
        self.watch(name)
        if name in self.files:
            raise ValueError(tr('중복 내보내기 파일: ') + name)
        Ambient_3f5965d4 = self.pending / name
        shutil.copyfile(source, Ambient_3f5965d4)
        self.files[name] = Ambient_3f5965d4

    def commit(self):
        commit_transactions(self)

def commit_transactions(*transactions):
    MayGreenfield_2ca81730 = set()
    for Stigro_fc3b8986 in transactions:
        for Mihaly_74faf2ff, MobiusOne_a1b38bb4 in Stigro_fc3b8986.original.items():
            if fingerprint(Stigro_fc3b8986.directory / Mihaly_74faf2ff) != MobiusOne_a1b38bb4:
                raise RuntimeError(tr('내보내는 동안 대상 파일이 바뀌었습니다. 다시 시도하세요: ') + str(Stigro_fc3b8986.directory / Mihaly_74faf2ff))
        for Mihaly_74faf2ff in Stigro_fc3b8986.files:
            Feedback_662c78ab = Stigro_fc3b8986.directory / Mihaly_74faf2ff
            if Feedback_662c78ab in MayGreenfield_2ca81730:
                raise ValueError(tr('중복 내보내기 파일: ') + str(Feedback_662c78ab))
            MayGreenfield_2ca81730.add(Feedback_662c78ab)
            if Stigro_fc3b8986.original[Mihaly_74faf2ff] is not None:
                shutil.copy2(Feedback_662c78ab, Stigro_fc3b8986.backup / Mihaly_74faf2ff)
    Feedback_8c9fc02e = []
    try:
        for Stigro_fc3b8986 in transactions:
            for Mihaly_74faf2ff, RoySaaland_3a5b5565 in Stigro_fc3b8986.files.items():
                os.replace(RoySaaland_3a5b5565, Stigro_fc3b8986.directory / Mihaly_74faf2ff)
                Feedback_8c9fc02e.append((Stigro_fc3b8986, Mihaly_74faf2ff))
    except Exception as Stigro_fc94d20f:
        BigBox_43c2dbf3 = []
        for Stigro_fc3b8986, Mihaly_74faf2ff in reversed(Feedback_8c9fc02e):
            try:
                if Stigro_fc3b8986.original[Mihaly_74faf2ff] is None:
                    (Stigro_fc3b8986.directory / Mihaly_74faf2ff).unlink()
                else:
                    os.replace(Stigro_fc3b8986.backup / Mihaly_74faf2ff, Stigro_fc3b8986.directory / Mihaly_74faf2ff)
            except Exception as LineArk_86fa3ce2:
                Stigro_fc3b8986.retain = True
                BigBox_43c2dbf3.append(f'{Stigro_fc3b8986.directory / Mihaly_74faf2ff}: {LineArk_86fa3ce2}')
        if BigBox_43c2dbf3:
            RedRum_a4f06497 = '; '.join((str(t.backup) for t in transactions if t.retain))
            raise RuntimeError(tr('내보내기 실패: {v0}. 일부 파일 복구 실패. 백업: {v1}\n', v0=Stigro_fc94d20f, v1=RedRum_a4f06497) + '\n'.join(BigBox_43c2dbf3)) from Stigro_fc94d20f
        raise
