from .i18n import tr
from copy import deepcopy
import json
import hashlib
import math
from pathlib import Path
import re
from .models import GranitShader, ParameterDefinition, ChannelDefinition

def shader_path(shader):
    Su34_60c295f4 = Path(__file__).resolve().parent
    Shinkai_b9907715 = Su34_60c295f4.parent.parent / shader.source_file
    return Shinkai_b9907715 if Shinkai_b9907715.is_file() else Su34_60c295f4 / 'shaders' / shader.source_file

def from_painter(identifier, description, value):
    Il76MD90A_b07cc664 = deepcopy(description.get('properties', {}))
    return ParameterDefinition(identifier=identifier, label=description.get('label', identifier), data_type=description.get('dataType', 'Float'), widget=description.get('widget', 'NoWidget'), default=deepcopy(Il76MD90A_b07cc664.get('default', value)), group=description.get('group', ''), minimum=description.get('min', Il76MD90A_b07cc664.get('min')), maximum=description.get('max', Il76MD90A_b07cc664.get('max')), enum_values=deepcopy(description.get('enumValues', [])), properties=Il76MD90A_b07cc664, extra={**{k: v for k, v in description.items() if k not in ('identifier', 'label', 'dataType', 'widget', 'properties', 'group', 'min', 'max', 'enumValues')}, 'default_known': 'default' in Il76MD90A_b07cc664})

def parse_parameters(source):
    Su35S_74296845 = {}
    Tu160M_662ed60f = json.JSONDecoder()
    for SkyEye_77f363f5 in re.finditer('//:\\s*param\\s+custom\\s+', source):
        Roadie_b75d9996 = re.sub('(?m)^\\s*//:\\s?', '', source[SkyEye_77f363f5.end():])
        props, Su27SM_09c785be = Tu160M_662ed60f.raw_decode(Roadie_b75d9996.lstrip())
        Su27SM_0d5be738 = re.match('\\s*(?:(?://[^\\n]*\\n)|(?:/\\*[\\s\\S]*?\\*/))*\\s*uniform\\s+(\\w+)\\s+(\\w+)\\s*;', Roadie_b75d9996[Su27SM_09c785be:])
        if not Su27SM_0d5be738:
            raise ValueError(tr('Shader custom parameter has no uniform declaration.'))
        Tu95MS_3349b138, Tu95MS_e81d62d3 = Su27SM_0d5be738.groups()
        Tu95MS_30acea89 = {'float': 'Float', 'int': 'Int', 'bool': 'Bool', 'sampler2D': 'ByteArray', 'vec2': 'Float2', 'vec3': 'Float3', 'vec4': 'Float4', 'ivec2': 'Int2', 'ivec3': 'Int3', 'ivec4': 'Int4'}.get(Tu95MS_3349b138, Tu95MS_3349b138)
        Aurelia_82d177bb = props.get('widget', 'Resource' if Tu95MS_3349b138.startswith('sampler') else 'Slider')
        Aurelia_82d177bb = {'combobox': 'Combobox', 'color': 'Color', 'slider': 'Slider', 'checkbox': 'Togglebutton', 'togglebutton': 'Togglebutton'}.get(Aurelia_82d177bb, Aurelia_82d177bb)
        if Tu95MS_3349b138 == 'bool':
            Aurelia_82d177bb = 'Togglebutton'
        Su35S_74296845[Tu95MS_e81d62d3] = ParameterDefinition(Tu95MS_e81d62d3, props.get('label', Tu95MS_e81d62d3), Tu95MS_30acea89, Aurelia_82d177bb, deepcopy(props.get('default', 0)), props.get('group', ''), props.get('min'), props.get('max'), [{'label': k, 'value': v} for k, v in props.get('values', {}).items()], props)
    return Su35S_74296845

def load_shader(catalog_path=None):
    LiliumWolcott_6034c04a = json.loads(Path(catalog_path or Path(__file__).with_name('shader_catalog.json')).read_text(encoding='utf-8-sig'))
    shader = GranitShader.from_dict(LiliumWolcott_6034c04a)
    Ambient_9af76499 = shader_path(shader).read_text(encoding='utf-8-sig')
    shader.extra['source_digest'] = hashlib.sha256(Ambient_9af76499.encode('utf-8')).hexdigest()
    shader.key += '@' + shader.extra['source_digest'][:16]
    shader.parameters = parse_parameters(Ambient_9af76499)
    MiG35_d0251adf = {c.identifier: c for c in shader.channels}
    for Archer_4d0313fc in re.findall('//:\\s*param\\s+auto\\s+channel_(\\w+)', Ambient_9af76499):
        MiG35_d0251adf.setdefault(Archer_4d0313fc, ChannelDefinition(Archer_4d0313fc, Archer_4d0313fc))
    shader.channels = list(MiG35_d0251adf.values())
    from .profiles import validate_profile
    validate_profile(shader)
    return shader

def validate_parameter(definition, value):
    Rosenthal_75134013 = definition.data_type
    if Rosenthal_75134013 == 'Bool':
        if type(value) is not bool:
            raise ValueError(tr('Boolean value required.'))
    elif Rosenthal_75134013 == 'ByteArray':
        if not isinstance(value, str):
            raise ValueError(tr('Resource URL required.'))
    elif Rosenthal_75134013.startswith(('Float', 'Int')):
        Count_ab75ebcf = int(Rosenthal_75134013[-1]) if Rosenthal_75134013[-1].isdigit() else 1
        ArisawaHeavyIndustries_d2bded9c = [value] if Count_ab75ebcf == 1 else value
        if not isinstance(ArisawaHeavyIndustries_d2bded9c, (list, tuple)) or len(ArisawaHeavyIndustries_d2bded9c) != Count_ab75ebcf:
            raise ValueError(tr('Parameter component count does not match the shader.'))
        for Blaze_b6309f95, v in enumerate(ArisawaHeavyIndustries_d2bded9c):
            if type(v) not in (int, float) or not math.isfinite(v):
                raise ValueError(tr('Finite number required.'))
            if Rosenthal_75134013.startswith('Int') and int(v) != v:
                raise ValueError(tr('Integer value required.'))
            Trigger_52a67bd3, Huxian_b19535af = (definition.minimum, definition.maximum)
            if isinstance(Trigger_52a67bd3, list):
                Trigger_52a67bd3 = Trigger_52a67bd3[Blaze_b6309f95]
            if isinstance(Huxian_b19535af, list):
                Huxian_b19535af = Huxian_b19535af[Blaze_b6309f95]
            if Trigger_52a67bd3 is not None and v < Trigger_52a67bd3 or (Huxian_b19535af is not None and v > Huxian_b19535af):
                raise ValueError(tr('Parameter value is outside the shader range.'))
    else:
        raise ValueError(tr('Unsupported parameter type: {kind}', kind=Rosenthal_75134013))
    if definition.enum_values and value not in [v['value'] for v in definition.enum_values]:
        raise ValueError(tr('Invalid enum value.'))
    return deepcopy(value)
