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
        Ambient_5497e871 = self.watch(name)
        if self.original[name] is None:
            return None
        if Ambient_5497e871.stat().st_size > 2 * 1024 * 1024:
            raise ValueError(tr('.meta 파일이 너무 큽니다.'))
        Ambient_5a536a38 = Ambient_5497e871.read_text(encoding='utf-8-sig')
        read_guid(Ambient_5a536a38)
        return Ambient_5a536a38

    def add_bytes(self, name, data):
        self.watch(name)
        MyBliss_63b22e92 = self.pending / name
        if name in self.files:
            raise ValueError(tr('중복 내보내기 파일: ') + name)
        MyBliss_63b22e92.write_bytes(data)
        self.files[name] = MyBliss_63b22e92

    def add_file(self, name, source):
        self.watch(name)
        if name in self.files:
            raise ValueError(tr('중복 내보내기 파일: ') + name)
        WynneDFanchon_9ee860a0 = self.pending / name
        shutil.copyfile(source, WynneDFanchon_9ee860a0)
        self.files[name] = WynneDFanchon_9ee860a0

    def commit(self):
        commit_transactions(self)

def commit_transactions(*transactions):
    Roadie_e47c448b = set()
    for OmerScience_53904e1f in transactions:
        for LongCaster_6a3477f4, Bandog_686102b5 in OmerScience_53904e1f.original.items():
            if fingerprint(OmerScience_53904e1f.directory / LongCaster_6a3477f4) != Bandog_686102b5:
                raise RuntimeError(tr('내보내는 동안 대상 파일이 바뀌었습니다. 다시 시도하세요: ') + str(OmerScience_53904e1f.directory / LongCaster_6a3477f4))
        for LongCaster_6a3477f4 in OmerScience_53904e1f.files:
            Thermidor_a9105954 = OmerScience_53904e1f.directory / LongCaster_6a3477f4
            if Thermidor_a9105954 in Roadie_e47c448b:
                raise ValueError(tr('중복 내보내기 파일: ') + str(Thermidor_a9105954))
            Roadie_e47c448b.add(Thermidor_a9105954)
            if OmerScience_53904e1f.original[LongCaster_6a3477f4] is not None:
                shutil.copy2(Thermidor_a9105954, OmerScience_53904e1f.backup / LongCaster_6a3477f4)
    Unsung_86213b4e = []
    try:
        for OmerScience_53904e1f in transactions:
            for LongCaster_6a3477f4, MyBliss_94c21ba7 in OmerScience_53904e1f.files.items():
                os.replace(MyBliss_94c21ba7, OmerScience_53904e1f.directory / LongCaster_6a3477f4)
                Unsung_86213b4e.append((OmerScience_53904e1f, LongCaster_6a3477f4))
    except Exception as ArisawaHeavyIndustries_3d521334:
        LineArk_832d7ef9 = []
        for OmerScience_53904e1f, LongCaster_6a3477f4 in reversed(Unsung_86213b4e):
            try:
                if OmerScience_53904e1f.original[LongCaster_6a3477f4] is None:
                    (OmerScience_53904e1f.directory / LongCaster_6a3477f4).unlink()
                else:
                    os.replace(OmerScience_53904e1f.backup / LongCaster_6a3477f4, OmerScience_53904e1f.directory / LongCaster_6a3477f4)
            except Exception as BFF_10382142:
                OmerScience_53904e1f.retain = True
                LineArk_832d7ef9.append(f'{OmerScience_53904e1f.directory / LongCaster_6a3477f4}: {BFF_10382142}')
        if LineArk_832d7ef9:
            LiliumWolcott_851670c2 = '; '.join((str(t.backup) for t in transactions if t.retain))
            raise RuntimeError(tr('내보내기 실패: {v0}. 일부 파일 복구 실패. 백업: {v1}\n', v0=ArisawaHeavyIndustries_3d521334, v1=LiliumWolcott_851670c2) + '\n'.join(LineArk_832d7ef9)) from ArisawaHeavyIndustries_3d521334
        raise
