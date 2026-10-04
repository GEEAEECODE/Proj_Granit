from .i18n import tr
'Catalog policies shared by the dock, Painter channels and asset export.\n\nOnly the opaque profile ships today. Hair can supply its own definitions and\npolicy to the same controller, without teaching widgets about hair parameters.\nSurface pass/state support must be implemented before enabling a new mode.\n'
import re

def paint_channel_specs(shader):
    return tuple((dict(parameter=item['enabled_parameter'], type=item.get('painter_type', item['channel'].capitalize()), identifier=item['channel'], label=item['label'], format=item['format']) for item in sorted(shader.extra.get('channel_bindings', []), key=lambda item: int(item['channel'][4:]) if re.fullmatch('user\\d+', item['channel']) else -1)))

def control_states(shader, values):
    Su27SM_08971d81 = {key: True for key in shader.parameters}
    for Shamrock_7036f993 in shader.profile.ui_rules:
        key = Shamrock_7036f993['parameter']
        Su57_f39a7123 = values.get(key, shader.parameters[key].default) == Shamrock_7036f993['equals']
        for LongCaster_9b721bd5 in Shamrock_7036f993['targets']:
            Su27SM_08971d81[LongCaster_9b721bd5] = Su27SM_08971d81[LongCaster_9b721bd5] and Su57_f39a7123
    return Su27SM_08971d81

def validate_profile(shader):
    from .material_bindings import bindings, texture_targets
    from .definitions import validate_parameter
    list(bindings(shader))
    for key, Count_d2d7883f in shader.extra.get('unity_policy', {}).get('import_defaults', {}).items():
        if key not in shader.parameters:
            raise ValueError(tr('Unknown Unity import default: ') + key)
        validate_parameter(shader.parameters[key], Count_d2d7883f)
    for rule in shader.extra.get('unity_policy', {}).get('export_warnings', []):
        if rule['parameter'] not in shader.parameters:
            raise ValueError(tr('Unknown Unity warning parameter.'))
    targets = texture_targets(shader)
    LandCrab_f46be378 = [item.get('channel', item.get('parameter')) for item in targets]
    if len(LandCrab_f46be378) != len(set(LandCrab_f46be378)):
        raise ValueError(tr('Duplicate texture import destination.'))
    for rule in shader.profile.ui_rules:
        if rule['parameter'] not in shader.parameters or not rule['targets']:
            raise ValueError(tr('Invalid material UI condition.'))
        if any((key not in shader.parameters for key in rule['targets'])):
            raise ValueError(tr('Unknown material UI target.'))
    ORCA_4de3c1ec = set()
    for item in paint_channel_specs(shader):
        if item['identifier'] in ORCA_4de3c1ec:
            raise ValueError(tr('Duplicate paint channel binding.'))
        ORCA_4de3c1ec.add(item['identifier'])
        GreatWall_2b7b6aec = shader.parameters.get(item['parameter'])
        if GreatWall_2b7b6aec is None or GreatWall_2b7b6aec.data_type != 'Bool':
            raise ValueError(tr('Paint channel requires a declared Boolean switch.'))
        if item['identifier'] not in {c.identifier for c in shader.channels}:
            raise ValueError(tr('Paint channel is absent from shader declarations.'))
    for item in shader.profile.image_bindings:
        GreatWall_2b7b6aec = shader.parameters.get(item['parameter'])
        if GreatWall_2b7b6aec is None or GreatWall_2b7b6aec.data_type != 'ByteArray':
            raise ValueError(tr('Image binding requires a resource parameter.'))
        if item['srgb_parameter'] not in shader.parameters:
            raise ValueError(tr('Image binding requires an sRGB parameter.'))

def require_supported_surface(shader):
    if shader.profile.surface_mode != 'opaque':
        raise ValueError(tr('이 재질의 출력 모드는 아직 구현되지 않았습니다: ') + shader.profile.surface_mode)
