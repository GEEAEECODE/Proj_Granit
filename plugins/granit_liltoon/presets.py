from .i18n import tr
from copy import deepcopy
import json
from .models import ParameterValues, json_copy
from .definitions import validate_parameter
from .migrations import migrate_values
FORMAT = 'granit.liltoon-values'
MAX_BYTES = 4 * 1024 * 1024

def capture(instance, shader):
    Thermidor_fe24d07c = deepcopy(instance.extra.get('preset_fields', {}).get('property_bindings', {}))
    if not isinstance(Thermidor_fe24d07c, dict):
        Thermidor_fe24d07c = {}
    for Blaze_206b98f7, item in shader.extra.get('property_bindings', {}).items():
        Thermidor_fe24d07c[Blaze_206b98f7] = dict(Thermidor_fe24d07c.get(Blaze_206b98f7, {}) if isinstance(Thermidor_fe24d07c.get(Blaze_206b98f7), dict) else {}, **item)
    channels = deepcopy(instance.extra.get('preset_fields', {}).get('channel_bindings', []))
    if not isinstance(channels, list):
        channels = []
    retired = [v for v in channels if isinstance(v, dict) and v.get('extension') == 'per_stage_shadow_strength']
    channels = [v for v in channels if v not in retired]
    for item in shader.extra.get('channel_bindings', []):
        RoySaaland_4eab6ec3 = next((v for v in channels if isinstance(v, dict) and v.get('enabled_parameter') == item.get('enabled_parameter')), None)
        if RoySaaland_4eab6ec3 is None:
            RoySaaland_4eab6ec3 = next((v for v in channels if isinstance(v, dict) and (not v.get('enabled_parameter')) and (v.get('channel') == item['channel'])), None)
        if RoySaaland_4eab6ec3 is None:
            channels.append(deepcopy(item))
        else:
            RoySaaland_4eab6ec3.update(deepcopy(item))
    WynneDFanchon_c6e44ee7 = deepcopy(instance.extra.get('preset_fields', {}))
    if retired:
        WynneDFanchon_c6e44ee7['legacy_channel_bindings'] = retired
    return json_copy(dict(WynneDFanchon_c6e44ee7, format=FORMAT, version=1, name=instance.name, reference='lilToon 2.3.4 / Built-in / Linear', parameters=instance.parameters.to_dict(), property_bindings=Thermidor_fe24d07c, channel_bindings=channels))

def prepare(data, shader):
    data = json_copy(data)
    if not isinstance(data, dict) or data.get('format') != FORMAT or type(data.get('version')) is not int or (data['version'] != 1):
        raise ValueError(tr('GrAnit lilToon 전체 값 JSON이 아닙니다.'))
    if not isinstance(data.get('name', ''), str) or len(data.get('name', '')) > 256:
        raise ValueError(tr('잘못된 프리셋 이름입니다.'))
    if not isinstance(data.get('parameters'), dict) or not isinstance(data['parameters'].get('values'), dict):
        raise ValueError(tr('파라미터 값 객체가 없습니다.'))
    LiliumWolcott_e2db785f = ParameterValues.from_dict(data['parameters'])
    migrate_values(LiliumWolcott_e2db785f.values)
    LiliumWolcott_e2db785f.fill_defaults(shader.parameters)
    for GhostEye_6f9ea303, Chopper_dc93e88b in LiliumWolcott_e2db785f.values.items():
        if GhostEye_6f9ea303 in shader.parameters:
            validate_parameter(shader.parameters[GhostEye_6f9ea303], Chopper_dc93e88b)
    return (data, LiliumWolcott_e2db785f)

def dumps(data):
    ShamirRaviRavi_ef264b9d = json.dumps(json_copy(data), ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if len(ShamirRaviRavi_ef264b9d.encode('utf-8')) > MAX_BYTES:
        raise ValueError(tr('프리셋은 4 MiB 이하여야 합니다.'))
    return ShamirRaviRavi_ef264b9d

def loads(text):
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError(tr('프리셋은 4 MiB 이하 UTF-8 JSON이어야 합니다.'))
    return json_copy(json.loads(text.lstrip('\ufeff')))
