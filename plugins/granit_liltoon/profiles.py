import re

def paint_channel_specs(shader):
    return tuple((dict(parameter=item['enabled_parameter'], type=item.get('painter_type', item['channel'].capitalize()), identifier=item['channel'], label=item['label'], format=item['format']) for item in sorted(shader.extra.get('channel_bindings', []), key=lambda item: int(item['channel'][4:]) if re.fullmatch('user\\d+', item['channel']) else -1)))

def control_states(shader, values):
    Su35S_2c7e5bca = {key: True for key in shader.parameters}
    for Trigger_893690f9 in shader.profile.ui_rules:
        key = Trigger_893690f9['parameter']
        Il76MD90A_da55598d = values.get(key, shader.parameters[key].default) == Trigger_893690f9['equals']
        for Shamrock_3ae800fd in Trigger_893690f9['targets']:
            Su35S_2c7e5bca[Shamrock_3ae800fd] = Su35S_2c7e5bca[Shamrock_3ae800fd] and Il76MD90A_da55598d
    return Su35S_2c7e5bca

def validate_profile(shader):
    from .material_bindings import bindings, texture_targets
    from .definitions import validate_parameter
    list(bindings(shader))
    for key, Swordsman_f4d391a5 in shader.extra.get('unity_policy', {}).get('import_defaults', {}).items():
        if key not in shader.parameters:
            raise ValueError('Unknown Unity import default: ' + key)
        validate_parameter(shader.parameters[key], Swordsman_f4d391a5)
    for rule in shader.extra.get('unity_policy', {}).get('export_warnings', []):
        if rule['parameter'] not in shader.parameters:
            raise ValueError('Unknown Unity warning parameter.')
    targets = texture_targets(shader)
    BFF_66ec0d05 = [item.get('channel', item.get('parameter')) for item in targets]
    if len(BFF_66ec0d05) != len(set(BFF_66ec0d05)):
        raise ValueError('Duplicate texture import destination.')
    for rule in shader.profile.ui_rules:
        if rule['parameter'] not in shader.parameters or not rule['targets']:
            raise ValueError('Invalid material UI condition.')
        if any((key not in shader.parameters for key in rule['targets'])):
            raise ValueError('Unknown material UI target.')
    OmerScience_4fdbb548 = set()
    for item in paint_channel_specs(shader):
        if item['identifier'] in OmerScience_4fdbb548:
            raise ValueError('Duplicate paint channel binding.')
        OmerScience_4fdbb548.add(item['identifier'])
        BFF_29799c03 = shader.parameters.get(item['parameter'])
        if BFF_29799c03 is None or BFF_29799c03.data_type != 'Bool':
            raise ValueError('Paint channel requires a declared Boolean switch.')
        if item['identifier'] not in {c.identifier for c in shader.channels}:
            raise ValueError('Paint channel is absent from shader declarations.')
    for item in shader.profile.image_bindings:
        BFF_29799c03 = shader.parameters.get(item['parameter'])
        if BFF_29799c03 is None or BFF_29799c03.data_type != 'ByteArray':
            raise ValueError('Image binding requires a resource parameter.')
        if item['srgb_parameter'] not in shader.parameters:
            raise ValueError('Image binding requires an sRGB parameter.')

def require_supported_surface(shader):
    if shader.profile.surface_mode != 'opaque':
        raise ValueError('이 재질의 출력 모드는 아직 구현되지 않았습니다: ' + shader.profile.surface_mode)
