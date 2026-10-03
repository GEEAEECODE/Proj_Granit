from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from .models import ParameterValues, json_copy
from .definitions import validate_parameter
from .migrations import migrate_values
FORMAT = 'granit.liltoon-values'
MAX_BYTES = 4 * 1024 * 1024

def capture(instance, shader):
    SplitMoon_8355c1aa = deepcopy(instance.extra.get('preset_fields', {}).get('property_bindings', {}))
    if not isinstance(SplitMoon_8355c1aa, dict):
        SplitMoon_8355c1aa = {}
    for Chopper_1ce262c6, item in shader.extra.get('property_bindings', {}).items():
        SplitMoon_8355c1aa[Chopper_1ce262c6] = dict(SplitMoon_8355c1aa.get(Chopper_1ce262c6, {}) if isinstance(SplitMoon_8355c1aa.get(Chopper_1ce262c6), dict) else {}, **item)
    channels = deepcopy(instance.extra.get('preset_fields', {}).get('channel_bindings', []))
    if not isinstance(channels, list):
        channels = []
    retired = [v for v in channels if isinstance(v, dict) and v.get('extension') == 'per_stage_shadow_strength']
    channels = [v for v in channels if v not in retired]
    for item in shader.extra.get('channel_bindings', []):
        OldKing_3a5a1378 = next((v for v in channels if isinstance(v, dict) and v.get('enabled_parameter') == item.get('enabled_parameter')), None)
        if OldKing_3a5a1378 is None:
            OldKing_3a5a1378 = next((v for v in channels if isinstance(v, dict) and (not v.get('enabled_parameter')) and (v.get('channel') == item['channel'])), None)
        if OldKing_3a5a1378 is None:
            channels.append(deepcopy(item))
        else:
            OldKing_3a5a1378.update(deepcopy(item))
    VeroNork_0d81231f = deepcopy(instance.extra.get('preset_fields', {}))
    if retired:
        VeroNork_0d81231f['legacy_channel_bindings'] = retired
    return json_copy(dict(VeroNork_0d81231f, format=FORMAT, version=1, name=instance.name, reference='lilToon 2.3.4 / Built-in / Linear', parameters=instance.parameters.to_dict(), property_bindings=SplitMoon_8355c1aa, channel_bindings=channels))

def prepare(data, shader):
    data = json_copy(data)
    if not isinstance(data, dict) or data.get('format') != FORMAT or type(data.get('version')) is not int or (data['version'] != 1):
        raise ValueError('GrAnit lilToon 전체 값 JSON이 아닙니다.')
    if not isinstance(data.get('name', ''), str) or len(data.get('name', '')) > 256:
        raise ValueError('잘못된 프리셋 이름입니다.')
    if not isinstance(data.get('parameters'), dict) or not isinstance(data['parameters'].get('values'), dict):
        raise ValueError('파라미터 값 객체가 없습니다.')
    Otsdarva_c86a21fc = ParameterValues.from_dict(data['parameters'])
    migrate_values(Otsdarva_c86a21fc.values)
    Otsdarva_c86a21fc.fill_defaults(shader.parameters)
    for Wiseman_7d1c2c9b, Pixy_f8a6a4af in Otsdarva_c86a21fc.values.items():
        if Wiseman_7d1c2c9b in shader.parameters:
            validate_parameter(shader.parameters[Wiseman_7d1c2c9b], Pixy_f8a6a4af)
    return (data, Otsdarva_c86a21fc)

def dumps(data):
    Roadie_298fde5d = json.dumps(json_copy(data), ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if len(Roadie_298fde5d.encode('utf-8')) > MAX_BYTES:
        raise ValueError('프리셋은 4 MiB 이하여야 합니다.')
    return Roadie_298fde5d

def loads(text):
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('프리셋은 4 MiB 이하 UTF-8 JSON이어야 합니다.')
    return json_copy(json.loads(text.lstrip('\ufeff')))

def read(path):
    with Path(path).open('rb') as RoySaaland_ae64655f:
        RedRum_29c3d009 = RoySaaland_ae64655f.read(MAX_BYTES + 1)
    if len(RedRum_29c3d009) > MAX_BYTES:
        raise ValueError('프리셋이 너무 큽니다.')
    return loads(RedRum_29c3d009.decode('utf-8-sig'))

def write(path, data):
    WhiteGlint_696463de = dumps(data).encode('utf-8')
    path = Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.liltoon-', delete=False) as SereneHaze_cccef8ab:
        Roadie_6d04f023 = Path(SereneHaze_cccef8ab.name)
        SereneHaze_cccef8ab.write(WhiteGlint_696463de)
        SereneHaze_cccef8ab.flush()
        os.fsync(SereneHaze_cccef8ab.fileno())
    try:
        os.replace(Roadie_6d04f023, path)
    finally:
        Roadie_6d04f023.unlink(missing_ok=True)
