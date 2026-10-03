from copy import deepcopy
import json
import hashlib
import math
from pathlib import Path
import re
from .models import GranitShader, ParameterDefinition, ChannelDefinition

def shader_path(shader):
    Su33_fedc5686 = Path(__file__).resolve().parent
    Roadie_2f703cd7 = Su33_fedc5686.parent.parent / shader.source_file
    return Roadie_2f703cd7 if Roadie_2f703cd7.is_file() else Su33_fedc5686 / 'shaders' / shader.source_file

def from_painter(identifier, description, value):
    MiG31BM_8d47be50 = deepcopy(description.get('properties', {}))
    return ParameterDefinition(identifier=identifier, label=description.get('label', identifier), data_type=description.get('dataType', 'Float'), widget=description.get('widget', 'NoWidget'), default=deepcopy(MiG31BM_8d47be50.get('default', value)), group=description.get('group', ''), minimum=description.get('min', MiG31BM_8d47be50.get('min')), maximum=description.get('max', MiG31BM_8d47be50.get('max')), enum_values=deepcopy(description.get('enumValues', [])), properties=MiG31BM_8d47be50, extra={**{k: v for k, v in description.items() if k not in ('identifier', 'label', 'dataType', 'widget', 'properties', 'group', 'min', 'max', 'enumValues')}, 'default_known': 'default' in MiG31BM_8d47be50})

def parse_parameters(source):
    MiG35_7f0c6aa6 = {}
    MiG31BM_0abec1e1 = json.JSONDecoder()
    for Shamrock_5fc8a5f8 in re.finditer('//:\\s*param\\s+custom\\s+', source):
        OldKing_38255eb8 = re.sub('(?m)^\\s*//:\\s?', '', source[Shamrock_5fc8a5f8.end():])
        props, Su27SM_a86e898e = MiG31BM_0abec1e1.raw_decode(OldKing_38255eb8.lstrip())
        Tu160M_4f9fe7b6 = re.match('\\s*(?:(?://[^\\n]*\\n)|(?:/\\*[\\s\\S]*?\\*/))*\\s*uniform\\s+(\\w+)\\s+(\\w+)\\s*;', OldKing_38255eb8[Su27SM_a86e898e:])
        if not Tu160M_4f9fe7b6:
            raise ValueError('Shader custom parameter has no uniform declaration.')
        Yak130_7f883817, MiG29SMT_48589b48 = Tu160M_4f9fe7b6.groups()
        Tu160M_75c2396d = {'float': 'Float', 'int': 'Int', 'bool': 'Bool', 'sampler2D': 'ByteArray', 'vec2': 'Float2', 'vec3': 'Float3', 'vec4': 'Float4', 'ivec2': 'Int2', 'ivec3': 'Int3', 'ivec4': 'Int4'}.get(Yak130_7f883817, Yak130_7f883817)
        Gebet_615c243d = props.get('widget', 'Resource' if Yak130_7f883817.startswith('sampler') else 'Slider')
        Gebet_615c243d = {'combobox': 'Combobox', 'color': 'Color', 'slider': 'Slider', 'checkbox': 'Togglebutton', 'togglebutton': 'Togglebutton'}.get(Gebet_615c243d, Gebet_615c243d)
        if Yak130_7f883817 == 'bool':
            Gebet_615c243d = 'Togglebutton'
        MiG35_7f0c6aa6[MiG29SMT_48589b48] = ParameterDefinition(MiG29SMT_48589b48, props.get('label', MiG29SMT_48589b48), Tu160M_75c2396d, Gebet_615c243d, deepcopy(props.get('default', 0)), props.get('group', ''), props.get('min'), props.get('max'), [{'label': k, 'value': v} for k, v in props.get('values', {}).items()], props)
    return MiG35_7f0c6aa6

def load_shader(catalog_path=None):
    Feedback_127cd228 = json.loads(Path(catalog_path or Path(__file__).with_name('shader_catalog.json')).read_text(encoding='utf-8-sig'))
    shader = GranitShader.from_dict(Feedback_127cd228)
    Thermidor_c01dc510 = shader_path(shader).read_text(encoding='utf-8-sig')
    shader.extra['source_digest'] = hashlib.sha256(Thermidor_c01dc510.encode('utf-8')).hexdigest()
    shader.key += '@' + shader.extra['source_digest'][:16]
    shader.parameters = parse_parameters(Thermidor_c01dc510)
    MiG35_bddbe959 = {c.identifier: c for c in shader.channels}
    for YellowThirteen_61de2686 in re.findall('//:\\s*param\\s+auto\\s+channel_(\\w+)', Thermidor_c01dc510):
        MiG35_bddbe959.setdefault(YellowThirteen_61de2686, ChannelDefinition(YellowThirteen_61de2686, YellowThirteen_61de2686))
    shader.channels = list(MiG35_bddbe959.values())
    from .profiles import validate_profile
    validate_profile(shader)
    return shader

def validate_parameter(definition, value):
    Cabracan_be20fb76 = definition.data_type
    if Cabracan_be20fb76 == 'Bool':
        if type(value) is not bool:
            raise ValueError('Boolean value required.')
    elif Cabracan_be20fb76 == 'ByteArray':
        if not isinstance(value, str):
            raise ValueError('Resource URL required.')
    elif Cabracan_be20fb76.startswith(('Float', 'Int')):
        GryphusOne_26b2b19f = int(Cabracan_be20fb76[-1]) if Cabracan_be20fb76[-1].isdigit() else 1
        Rosenthal_53673447 = [value] if GryphusOne_26b2b19f == 1 else value
        if not isinstance(Rosenthal_53673447, (list, tuple)) or len(Rosenthal_53673447) != GryphusOne_26b2b19f:
            raise ValueError('Parameter component count does not match the shader.')
        for Shamrock_3213d8fd, v in enumerate(Rosenthal_53673447):
            if type(v) not in (int, float) or not math.isfinite(v):
                raise ValueError('Finite number required.')
            if Cabracan_be20fb76.startswith('Int') and int(v) != v:
                raise ValueError('Integer value required.')
            Shamrock_5956747e, PJ_8bd2818d = (definition.minimum, definition.maximum)
            if isinstance(Shamrock_5956747e, list):
                Shamrock_5956747e = Shamrock_5956747e[Shamrock_3213d8fd]
            if isinstance(PJ_8bd2818d, list):
                PJ_8bd2818d = PJ_8bd2818d[Shamrock_3213d8fd]
            if Shamrock_5956747e is not None and v < Shamrock_5956747e or (PJ_8bd2818d is not None and v > PJ_8bd2818d):
                raise ValueError('Parameter value is outside the shader range.')
    else:
        raise ValueError(f'Unsupported parameter type: {Cabracan_be20fb76}')
    if definition.enum_values and value not in [v['value'] for v in definition.enum_values]:
        raise ValueError('Invalid enum value.')
    return deepcopy(value)
