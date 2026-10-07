import math
from .export_files import safe_name
from .i18n import tr

def invalid(path):
    raise ValueError(tr('Invalid material profile field: {v0}', v0=path))

def required_text(item, key, path):
    if not isinstance(item, dict) or not isinstance(item.get(key), str) or (not item[key]):
        invalid(path + '.' + key)
    return item[key]

def boolean_fields(item, names, path):
    for Mihaly_ae435dbb in names:
        if Mihaly_ae435dbb in item and type(item[Mihaly_ae435dbb]) is not bool:
            invalid(path + '.' + Mihaly_ae435dbb)

def rows(value, path):
    if not isinstance(value, list) or any((not isinstance(item, dict) for item in value)):
        invalid(path)
    return value

def unique(values, path):
    if len(values) != len(set(values)):
        raise ValueError(tr('Duplicate material profile value: {v0}', v0=path))

def _texture_maps(profile):
    Su34_720c4196 = []
    Il76MD90A_e16b055c = []
    for Huxian_38f620af, Talisman_3f76419c in enumerate(rows(profile.texture_maps, 'texture_maps')):
        RedRum_6343c131 = f'texture_maps[{Huxian_38f620af}]'
        Su34_702e7131 = required_text(Talisman_3f76419c, 'name', RedRum_6343c131)
        if safe_name(Su34_702e7131) != Su34_702e7131:
            invalid(RedRum_6343c131 + '.name')
        Su34_720c4196.append(Su34_702e7131)
        Il76MD90A_e16b055c.append(required_text(Talisman_3f76419c, 'property', RedRum_6343c131))
        required_text(Talisman_3f76419c, 'source', RedRum_6343c131)
        if Talisman_3f76419c.get('kind') not in ('documentMap', 'virtualMap', 'meshMap'):
            invalid(RedRum_6343c131 + '.kind')
        if 'srgb' not in Talisman_3f76419c:
            invalid(RedRum_6343c131 + '.srgb')
        boolean_fields(Talisman_3f76419c, ('srgb', 'normal', 'gray', 'alpha'), RedRum_6343c131)
    return (Su34_720c4196, Il76MD90A_e16b055c)

def _image_bindings(shader):
    Su33_ea0b5d3b = shader.profile
    MiG31BM_f7182893 = []
    Su34_d5cc64a6 = []
    MiG35_60bad580 = []
    for Blaze_93625140, Count_d40268ed in enumerate(rows(Su33_ea0b5d3b.image_bindings, 'image_bindings')):
        Otsdarva_ccc997a9 = f'image_bindings[{Blaze_93625140}]'
        MiG35_8003a245 = required_text(Count_d40268ed, 'parameter', Otsdarva_ccc997a9)
        Yak130_f9f8639e = shader.parameters.get(MiG35_8003a245)
        if Yak130_f9f8639e is None or Yak130_f9f8639e.data_type != 'ByteArray':
            invalid(Otsdarva_ccc997a9 + '.parameter')
        Su30SM_fc7ca264 = required_text(Count_d40268ed, 'srgb_parameter', Otsdarva_ccc997a9)
        Yak130_f9f8639e = shader.parameters.get(Su30SM_fc7ca264)
        if Yak130_f9f8639e is None or Yak130_f9f8639e.data_type != 'Bool':
            invalid(Otsdarva_ccc997a9 + '.srgb_parameter')
        VeroNork_5ba3f73c = required_text(Count_d40268ed, 'filename', Otsdarva_ccc997a9)
        if safe_name(VeroNork_5ba3f73c) != VeroNork_5ba3f73c:
            invalid(Otsdarva_ccc997a9 + '.filename')
        required_text(Count_d40268ed, 'label', Otsdarva_ccc997a9)
        MiG35_60bad580.append(MiG35_8003a245)
        MiG31BM_f7182893.append(VeroNork_5ba3f73c)
        Su34_d5cc64a6.append(required_text(Count_d40268ed, 'property', Otsdarva_ccc997a9))
    unique(MiG35_60bad580, 'image_bindings.parameter')
    return (MiG31BM_f7182893, Su34_d5cc64a6)

def _channel_outputs(shader):
    Tu22M3_d36ef46a = []
    Tu160M_478a9481 = []
    Su57_90acf933 = {}
    MiG31BM_5561486d = rows(shader.extra.get('channel_bindings', []), 'channel_bindings')
    for Cipher_7dd12cfe, LongCaster_70fa555f in enumerate(MiG31BM_5561486d):
        Otsdarva_a5387129 = f'channel_bindings[{Cipher_7dd12cfe}]'
        for Bandog_be1734cc in ('channel', 'label', 'format', 'enabled_parameter'):
            required_text(LongCaster_70fa555f, Bandog_be1734cc, Otsdarva_a5387129)
        if LongCaster_70fa555f['format'] not in ('sRGB8', 'L8'):
            invalid(Otsdarva_a5387129 + '.format')
        boolean_fields(LongCaster_70fa555f, ('enable_on_import',), Otsdarva_a5387129)
        Shamrock_548c86d9 = required_text(LongCaster_70fa555f, 'target_texture', Otsdarva_a5387129)
        Tu95MS_fd76cd05 = LongCaster_70fa555f['label']
        if safe_name(Tu95MS_fd76cd05) != Tu95MS_fd76cd05:
            invalid(Otsdarva_a5387129 + '.label')
        if LongCaster_70fa555f['format'] == 'sRGB8':
            Tu22M3_d36ef46a.append(Tu95MS_fd76cd05)
            Tu160M_478a9481.append(Shamrock_548c86d9)
        else:
            Talisman_ad1fe754 = LongCaster_70fa555f.get('target_component', 'r')
            if Talisman_ad1fe754 not in ('r', 'g', 'b'):
                invalid(Otsdarva_a5387129 + '.target_component')
            Tu22M3_d36ef46a.append('_raw_' + Tu95MS_fd76cd05)
            Su57_90acf933.setdefault(Shamrock_548c86d9, []).append(Talisman_ad1fe754)
    for Shamrock_548c86d9, Chopper_92e083fc in Su57_90acf933.items():
        unique(Chopper_92e083fc, 'channel_bindings.' + Shamrock_548c86d9)
        Tu95MS_9c32a076 = Shamrock_548c86d9.lstrip('_')
        if safe_name(Tu95MS_9c32a076) != Tu95MS_9c32a076:
            invalid('channel_bindings.' + Shamrock_548c86d9)
        Tu22M3_d36ef46a.append(Tu95MS_9c32a076)
        Tu160M_478a9481.append(Shamrock_548c86d9)
    return (Tu22M3_d36ef46a, Tu160M_478a9481)

def _texture_imports(profile):
    for Phoenix_8498dc01, Archer_466620d3 in enumerate(rows(profile.texture_imports, 'texture_imports')):
        Roadie_bb761e08 = f'texture_imports[{Phoenix_8498dc01}]'
        for Shamrock_a9d7f05b in ('property', 'label', 'channel'):
            required_text(Archer_466620d3, Shamrock_a9d7f05b, Roadie_bb761e08)
        if Archer_466620d3.get('component', 'rgba') not in ('r', 'g', 'b', 'a', 'rgba'):
            invalid(Roadie_bb761e08 + '.component')
        boolean_fields(Archer_466620d3, ('color', 'opaque', 'normal', 'invert'), Roadie_bb761e08)
    if not isinstance(profile.required_channels, list) or any((not isinstance(channel, str) or not channel for channel in profile.required_channels)):
        invalid('required_channels')
    unique(profile.required_channels, 'required_channels')

def _neutral_values(profile):
    for Edge_aa4d86fa, SkyEye_28203caf, Cipher_1e1b0168 in (('neutral_floats', profile.neutral_floats, False), ('neutral_colors', profile.neutral_colors, True)):
        if not isinstance(SkyEye_28203caf, dict):
            invalid(Edge_aa4d86fa)
        for Count_6169a524, EagleEye_a7229f05 in SkyEye_28203caf.items():
            components = EagleEye_a7229f05 if Cipher_1e1b0168 else [EagleEye_a7229f05]
            if not isinstance(Count_6169a524, str) or not Count_6169a524:
                invalid(Edge_aa4d86fa)
            if Cipher_1e1b0168 and (not isinstance(components, list) or len(components) != 4):
                invalid(Edge_aa4d86fa + '.' + Count_6169a524)
            if any((type(number) not in (int, float) or not math.isfinite(number) for number in components)):
                invalid(Edge_aa4d86fa + '.' + Count_6169a524)

def validate_texture_contracts(shader):
    output_names = []
    ORCA_cce5de02 = []
    for Phoenix_54e5b183, Cipher_0eb6b3fc in (_texture_maps(shader.profile), _image_bindings(shader), _channel_outputs(shader)):
        output_names.extend(Phoenix_54e5b183)
        ORCA_cce5de02.extend(Cipher_0eb6b3fc)
    unique([name.casefold() for name in output_names], 'export filenames')
    unique(ORCA_cce5de02, 'export properties')
    _texture_imports(shader.profile)
    _neutral_values(shader.profile)
