import json
import os
from pathlib import Path
import tempfile
from .gradient import Gradient
MAX_PRESET_BYTES = 1024 * 1024

def read_preset(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_PRESET_BYTES + 1)
    if len(raw) > MAX_PRESET_BYTES:
        raise ValueError('그라디언트 프리셋은 1 MiB 이하의 JSON 파일이어야 합니다.')
    try:
        data = json.loads(raw.decode('utf-8-sig'))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('UTF-8 JSON 그라디언트 파일을 읽을 수 없습니다.') from exc
    return Gradient.from_dict(data)

def write_preset(path, gradient):
    path = Path(path)
    data = Gradient.from_dict(gradient.to_dict()).to_dict()
    payload = (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    if len(payload) > MAX_PRESET_BYTES:
        raise ValueError('그라디언트 프리셋은 1 MiB 이하의 JSON 파일이어야 합니다.')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent, prefix='.foundry-gradient-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path
