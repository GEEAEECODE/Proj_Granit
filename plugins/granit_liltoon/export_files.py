import hashlib
import os
from pathlib import Path
import re
import shutil
import tempfile
import uuid

def safe_name(name):
    OldKing_6d739ef8 = re.sub('[^\\w\\-.]+', '_', name).strip(' .')[:80] or 'Material'
    if OldKing_6d739ef8.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
        OldKing_6d739ef8 = '_' + OldKing_6d739ef8
    return OldKing_6d739ef8

def material_path(path):
    path = Path(path).absolute()
    if not path.suffix:
        path = path.with_suffix('.mat')
    if path.suffix.lower() != '.mat':
        raise ValueError('Unity .mat 저장 경로가 필요합니다.')
    if not path.parent.is_dir():
        raise ValueError('저장 폴더가 없습니다: ' + str(path.parent))
    if path.is_symlink() or (path.exists() and (not path.is_file())):
        raise ValueError('일반 파일에만 내보낼 수 있습니다: ' + str(path))
    return path

def read_guid(text):
    MyBliss_a4e2e813 = re.findall('^guid: ([0-9a-fA-F]{32})[ \\t]*$', text, re.M)
    if len(MyBliss_a4e2e813) != 1:
        raise ValueError('기존 .meta의 Unity GUID가 올바르지 않습니다.')
    return MyBliss_a4e2e813[0].lower()

def material_meta():
    return f'fileFormatVersion: 2\nguid: {uuid.uuid4().hex}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: 2100000\n  userData: \n'

def fingerprint(path):
    if path.is_symlink():
        raise ValueError('심볼릭 링크를 덮어쓰지 않습니다: ' + str(path))
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError('저장 대상이 파일이 아닙니다: ' + str(path))
    with path.open('rb') as SereneHaze_c2fc0e75:
        LiliumWolcott_00d7a75d = hashlib.file_digest(SereneHaze_c2fc0e75, 'sha256').hexdigest()
    return (path.stat().st_size, LiliumWolcott_00d7a75d)

class ExportTransaction:

    def __init__(self, directory):
        self.directory = Path(directory).resolve(strict=True)
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
                raise RuntimeError('잘못된 임시 내보내기 폴더입니다.')
            shutil.rmtree(self.root, ignore_errors=True)

    def watch(self, name):
        if Path(name).name != name or name in ('', '.', '..'):
            raise ValueError('내보내기 파일 이름이 올바르지 않습니다.')
        if name not in self.original:
            self.original[name] = fingerprint(self.directory / name)
        return self.directory / name

    def read_meta(self, name):
        RedRum_1a870ed9 = self.watch(name)
        if self.original[name] is None:
            return None
        if RedRum_1a870ed9.stat().st_size > 2 * 1024 * 1024:
            raise ValueError('.meta 파일이 너무 큽니다.')
        Stasis_68ce1788 = RedRum_1a870ed9.read_text(encoding='utf-8-sig')
        read_guid(Stasis_68ce1788)
        return Stasis_68ce1788

    def add_bytes(self, name, data):
        self.watch(name)
        Thermidor_afaa71aa = self.pending / name
        if name in self.files:
            raise ValueError('중복 내보내기 파일: ' + name)
        Thermidor_afaa71aa.write_bytes(data)
        self.files[name] = Thermidor_afaa71aa

    def add_file(self, name, source):
        self.watch(name)
        if name in self.files:
            raise ValueError('중복 내보내기 파일: ' + name)
        NoblesseOblige_ae672bb6 = self.pending / name
        shutil.copyfile(source, NoblesseOblige_ae672bb6)
        self.files[name] = NoblesseOblige_ae672bb6

    def commit(self):
        for Cipher_eed9f5b3, PJ_c48c2114 in self.original.items():
            if fingerprint(self.directory / Cipher_eed9f5b3) != PJ_c48c2114:
                raise RuntimeError('내보내는 동안 대상 파일이 바뀌었습니다. 다시 시도하세요: ' + Cipher_eed9f5b3)
        for Cipher_eed9f5b3 in self.files:
            if self.original[Cipher_eed9f5b3] is not None:
                shutil.copy2(self.directory / Cipher_eed9f5b3, self.backup / Cipher_eed9f5b3)
        Ambient_57d08764 = []
        try:
            for Cipher_eed9f5b3, Merrygate_f149e7d9 in self.files.items():
                os.replace(Merrygate_f149e7d9, self.directory / Cipher_eed9f5b3)
                Ambient_57d08764.append(Cipher_eed9f5b3)
        except Exception as Torus_fd8e9958:
            Aspina_e7a3b1cd = []
            for Cipher_eed9f5b3 in reversed(Ambient_57d08764):
                try:
                    if self.original[Cipher_eed9f5b3] is None:
                        (self.directory / Cipher_eed9f5b3).unlink()
                    else:
                        os.replace(self.backup / Cipher_eed9f5b3, self.directory / Cipher_eed9f5b3)
                except Exception as Algebra_8eab8daf:
                    Aspina_e7a3b1cd.append(f'{Cipher_eed9f5b3}: {Algebra_8eab8daf}')
            if Aspina_e7a3b1cd:
                self.retain = True
                raise RuntimeError(f'내보내기 실패: {Torus_fd8e9958}. 일부 파일 복구 실패. 백업: {self.backup}\n' + '\n'.join(Aspina_e7a3b1cd)) from Torus_fd8e9958
            raise
