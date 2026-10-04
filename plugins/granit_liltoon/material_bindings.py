from .i18n import tr
'Catalog-driven Unity property codecs shared by full and selective exchange.\n\nFeature names are data, not branches here. New features declare parameters,\nproperty bindings, optional image/channel bindings and unsupported-value rules.\n'
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
    for Edge_d01996d2, SkyEye_bfbbba78 in shader.extra.get('property_bindings', {}).items():
        Ambient_e7013603 = shader.parameters.get(Edge_d01996d2)
        RoySaaland_4260d330 = SkyEye_bfbbba78.get('property')
        if not RoySaaland_4260d330:
            continue
        if not Ambient_e7013603:
            raise ValueError(tr('Unknown Unity-bound parameter: ') + Edge_d01996d2)
        if Ambient_e7013603.data_type == 'ByteArray':
            continue
        YellowThirteen_af0ae32d = SkyEye_bfbbba78.get('component', '')
        Ambient_aaf5e9f7 = YellowThirteen_af0ae32d == 'rgb' or Ambient_e7013603.widget.lower() == 'color'
        MyBliss_2ebebc13 = SkyEye_bfbbba78.get('unity_codec', 'srgb_color' if Ambient_aaf5e9f7 else 'raw')
        if MyBliss_2ebebc13 not in ('raw', 'srgb_color', 'toggle'):
            raise ValueError(tr('Unknown Unity value codec: ') + MyBliss_2ebebc13)
        if YellowThirteen_af0ae32d not in ('', 'r', 'g', 'b', 'a', 'rgb', 'rgba'):
            raise ValueError(tr('Unknown Unity component: ') + YellowThirteen_af0ae32d)
        if SkyEye_bfbbba78.get('multiply_by') and SkyEye_bfbbba78['multiply_by'] not in shader.parameters:
            raise ValueError(tr('Unknown Unity binding multiplier: ') + SkyEye_bfbbba78['multiply_by'])
        yield PropertyBinding(Edge_d01996d2, Ambient_e7013603, RoySaaland_4260d330, YellowThirteen_af0ae32d, MyBliss_2ebebc13, SkyEye_bfbbba78.get('multiply_by', ''))

def decode(material, binding):
    LongCaster_e8ca9196 = binding.definition
    Swordsman_25d5f4f9 = binding.component
    RoySaaland_f662501d = LongCaster_e8ca9196.data_type[-1:].isdigit()
    Thermidor_7692af3f = material.colors.get(binding.property) if Swordsman_25d5f4f9 or RoySaaland_f662501d else material.floats.get(binding.property)
    if Thermidor_7692af3f is None:
        raise ValueError(tr('머테리얼에 저장된 값 없음'))
    if Swordsman_25d5f4f9 in ('r', 'g', 'b', 'a'):
        value = Thermidor_7692af3f['rgba'.index(Swordsman_25d5f4f9)]
    elif Swordsman_25d5f4f9 == 'rgb':
        value = Thermidor_7692af3f[:3]
    elif RoySaaland_f662501d:
        value = Thermidor_7692af3f[:int(LongCaster_e8ca9196.data_type[-1])]
    else:
        value = deepcopy(Thermidor_7692af3f)
    if binding.codec == 'srgb_color':
        if not isinstance(value, list):
            raise ValueError(tr('Color codec requires a vector.'))
        value = [linear(v) if i < 3 else v for i, v in enumerate(value)]
    elif binding.codec == 'toggle':
        value = float(bool(value))
    if LongCaster_e8ca9196.data_type == 'Bool':
        value = bool(value)
    value = validate_parameter(LongCaster_e8ca9196, value)
    if LongCaster_e8ca9196.data_type == 'Int':
        value = int(value)
    return value

def encode(material, binding, value, floats, colors):
    if binding.codec == 'toggle':
        value = float(value > 0)
    if binding.component or isinstance(value, list):
        MayGreenfield_15b09541 = colors.setdefault(binding.property, list(material.colors.get(binding.property, [1, 1, 1, 1])))
        if binding.component in ('r', 'g', 'b', 'a'):
            MayGreenfield_15b09541['rgba'.index(binding.component)] = value
        else:
            Shinkai_e391d523 = [srgb(v) if binding.codec == 'srgb_color' and i < 3 else v for i, v in enumerate(value)]
            MayGreenfield_15b09541[:len(Shinkai_e391d523)] = Shinkai_e391d523
    else:
        floats[binding.property] = float(value)

def texture_targets(shader):
    Thermidor_131621d0 = deepcopy(shader.profile.texture_imports)
    for Thunderhead_a5dfef83 in shader.extra.get('channel_bindings', []):
        WynneDFanchon_41bc89b9 = Thunderhead_a5dfef83['enabled_parameter']
        RoySaaland_ad233540 = Thunderhead_a5dfef83.get('enable_on_import', shader.extra['property_bindings'].get(WynneDFanchon_41bc89b9, {}).get('extension') in ('color_channel_enabled', 'mask_channel_enabled'))
        Thermidor_131621d0.append(dict(property=Thunderhead_a5dfef83['target_texture'], label=Thunderhead_a5dfef83['label'], channel=Thunderhead_a5dfef83['channel'].capitalize(), format=Thunderhead_a5dfef83['format'], component=Thunderhead_a5dfef83.get('target_component', 'rgba' if Thunderhead_a5dfef83['format'] == 'sRGB8' else 'r'), enabled_parameter=WynneDFanchon_41bc89b9 if RoySaaland_ad233540 else '', color=Thunderhead_a5dfef83['format'] == 'sRGB8'))
    for Thunderhead_a5dfef83 in shader.profile.image_bindings:
        Thermidor_131621d0.append(dict(property=Thunderhead_a5dfef83['property'], label=Thunderhead_a5dfef83['label'], parameter=Thunderhead_a5dfef83['parameter'], srgb_parameter=Thunderhead_a5dfef83['srgb_parameter'], component='rgba', color=True))
    return Thermidor_131621d0

def unsupported_warnings(material, shader):
    supported = {b.property for b in bindings(shader)}
    return [prop + tr(': 미지원 동작, 원본 저장값만 보관') for prop, neutral in shader.extra.get('unity_policy', {}).get('unsupported_defaults', {}).items() if prop not in supported and prop in material.floats and (material.floats[prop] != neutral)]

def export_warnings(values, shader):
    LiliumWolcott_e1b1df67 = []
    for Trigger_05195eef in shader.extra.get('unity_policy', {}).get('export_warnings', []):
        if values.get(Trigger_05195eef['parameter'], Trigger_05195eef['equals']) != Trigger_05195eef['equals'] and Trigger_05195eef['message'] not in LiliumWolcott_e1b1df67:
            LiliumWolcott_e1b1df67.append(Trigger_05195eef['message'])
    for Count_7273e15f in bindings(shader):
        if Count_7273e15f.codec == 'toggle' and values.get(Count_7273e15f.key, 0) not in (0, 1):
            LiliumWolcott_e1b1df67.append(Count_7273e15f.definition.label + tr(' 중간값: lilToon은 ON/OFF만 지원'))
    return LiliumWolcott_e1b1df67
