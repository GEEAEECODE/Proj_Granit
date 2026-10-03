from copy import deepcopy
from dataclasses import dataclass
from .definitions import validate_parameter

def linear(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

def srgb(value):
    return value * 12.92 if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055

@dataclass(frozen=True)
class PropertyBinding:
    key: str
    definition: object
    property: str
    component: str
    codec: str
    multiply_by: str = ''

def bindings(shader):
    for PJ_216d090c, Huxian_ff949139 in shader.extra.get('property_bindings', {}).items():
        OldKing_ed4439af = shader.parameters.get(PJ_216d090c)
        Feedback_1263a9fe = Huxian_ff949139.get('property')
        if not Feedback_1263a9fe:
            continue
        if not OldKing_ed4439af:
            raise ValueError('Unknown Unity-bound parameter: ' + PJ_216d090c)
        if OldKing_ed4439af.data_type == 'ByteArray':
            continue
        Thunderhead_95ed7e71 = Huxian_ff949139.get('component', '')
        Merrygate_59006e42 = Thunderhead_95ed7e71 == 'rgb' or OldKing_ed4439af.widget.lower() == 'color'
        Reiterpallasch_ecf38fdb = Huxian_ff949139.get('unity_codec', 'srgb_color' if Merrygate_59006e42 else 'raw')
        if Reiterpallasch_ecf38fdb not in ('raw', 'srgb_color', 'toggle'):
            raise ValueError('Unknown Unity value codec: ' + Reiterpallasch_ecf38fdb)
        if Thunderhead_95ed7e71 not in ('', 'r', 'g', 'b', 'a', 'rgb', 'rgba'):
            raise ValueError('Unknown Unity component: ' + Thunderhead_95ed7e71)
        if Huxian_ff949139.get('multiply_by') and Huxian_ff949139['multiply_by'] not in shader.parameters:
            raise ValueError('Unknown Unity binding multiplier: ' + Huxian_ff949139['multiply_by'])
        yield PropertyBinding(PJ_216d090c, OldKing_ed4439af, Feedback_1263a9fe, Thunderhead_95ed7e71, Reiterpallasch_ecf38fdb, Huxian_ff949139.get('multiply_by', ''))

def decode(material, binding):
    Chopper_2b872a52 = binding.definition
    LongCaster_9175b6e9 = binding.component
    Reiterpallasch_a244bd4b = Chopper_2b872a52.data_type[-1:].isdigit()
    RedRum_788149a1 = material.colors.get(binding.property) if LongCaster_9175b6e9 or Reiterpallasch_a244bd4b else material.floats.get(binding.property)
    if RedRum_788149a1 is None:
        raise ValueError('머테리얼에 저장된 값 없음')
    if LongCaster_9175b6e9 in ('r', 'g', 'b', 'a'):
        value = RedRum_788149a1['rgba'.index(LongCaster_9175b6e9)]
    elif LongCaster_9175b6e9 == 'rgb':
        value = RedRum_788149a1[:3]
    elif Reiterpallasch_a244bd4b:
        value = RedRum_788149a1[:int(Chopper_2b872a52.data_type[-1])]
    else:
        value = deepcopy(RedRum_788149a1)
    if binding.codec == 'srgb_color':
        if not isinstance(value, list):
            raise ValueError('Color codec requires a vector.')
        value = [linear(v) if i < 3 else v for i, v in enumerate(value)]
    elif binding.codec == 'toggle':
        value = float(bool(value))
    if Chopper_2b872a52.data_type == 'Bool':
        value = bool(value)
    value = validate_parameter(Chopper_2b872a52, value)
    if Chopper_2b872a52.data_type == 'Int':
        value = int(value)
    return value

def encode(material, binding, value, floats, colors):
    if binding.codec == 'toggle':
        value = float(value > 0)
    if binding.component or isinstance(value, list):
        OldKing_c93e4420 = colors.setdefault(binding.property, list(material.colors.get(binding.property, [1, 1, 1, 1])))
        if binding.component in ('r', 'g', 'b', 'a'):
            OldKing_c93e4420['rgba'.index(binding.component)] = value
        else:
            VeroNork_92163ba7 = [srgb(v) if binding.codec == 'srgb_color' and i < 3 else v for i, v in enumerate(value)]
            OldKing_c93e4420[:len(VeroNork_92163ba7)] = VeroNork_92163ba7
    else:
        floats[binding.property] = float(value)

def texture_targets(shader):
    Ambient_efd24387 = deepcopy(shader.profile.texture_imports)
    for PJ_b2d1f16d in shader.extra.get('channel_bindings', []):
        Feedback_0783f9a6 = PJ_b2d1f16d['enabled_parameter']
        NoblesseOblige_97c3e9fa = PJ_b2d1f16d.get('enable_on_import', shader.extra['property_bindings'].get(Feedback_0783f9a6, {}).get('extension') in ('color_channel_enabled', 'mask_channel_enabled'))
        Ambient_efd24387.append(dict(property=PJ_b2d1f16d['target_texture'], label=PJ_b2d1f16d['label'], channel=PJ_b2d1f16d['channel'].capitalize(), format=PJ_b2d1f16d['format'], component=PJ_b2d1f16d.get('target_component', 'rgba' if PJ_b2d1f16d['format'] == 'sRGB8' else 'r'), enabled_parameter=Feedback_0783f9a6 if NoblesseOblige_97c3e9fa else '', color=PJ_b2d1f16d['format'] == 'sRGB8'))
    for PJ_b2d1f16d in shader.profile.image_bindings:
        Ambient_efd24387.append(dict(property=PJ_b2d1f16d['property'], label=PJ_b2d1f16d['label'], parameter=PJ_b2d1f16d['parameter'], srgb_parameter=PJ_b2d1f16d['srgb_parameter'], component='rgba', color=True))
    return Ambient_efd24387

def unsupported_warnings(material, shader):
    supported = {b.property for b in bindings(shader)}
    return [prop + ': 미지원 동작, 원본 저장값만 보관' for prop, neutral in shader.extra.get('unity_policy', {}).get('unsupported_defaults', {}).items() if prop not in supported and prop in material.floats and (material.floats[prop] != neutral)]

def export_warnings(values, shader):
    WynneDFanchon_645f9e91 = []
    for MobiusOne_c17e0533 in shader.extra.get('unity_policy', {}).get('export_warnings', []):
        if values.get(MobiusOne_c17e0533['parameter'], MobiusOne_c17e0533['equals']) != MobiusOne_c17e0533['equals'] and MobiusOne_c17e0533['message'] not in WynneDFanchon_645f9e91:
            WynneDFanchon_645f9e91.append(MobiusOne_c17e0533['message'])
    for Blaze_a794f247 in bindings(shader):
        if Blaze_a794f247.codec == 'toggle' and values.get(Blaze_a794f247.key, 0) not in (0, 1):
            WynneDFanchon_645f9e91.append(Blaze_a794f247.definition.label + ' 중간값: lilToon은 ON/OFF만 지원')
    return WynneDFanchon_645f9e91
