from copy import deepcopy
import json
import hashlib
import math
from pathlib import Path
import re
from .models import GranitShader, ParameterDefinition, ChannelDefinition

def shader_path(shader):
    package = Path(__file__).resolve().parent
    source = package.parent.parent / shader.source_file
    return source if source.is_file() else package / 'shaders' / shader.source_file

def from_painter(identifier, description, value):
    props = deepcopy(description.get('properties', {}))
    return ParameterDefinition(identifier=identifier, label=description.get('label', identifier), data_type=description.get('dataType', 'Float'), widget=description.get('widget', 'NoWidget'), default=deepcopy(props.get('default', value)), group=description.get('group', ''), minimum=description.get('min', props.get('min')), maximum=description.get('max', props.get('max')), enum_values=deepcopy(description.get('enumValues', [])), properties=props, extra={**{k: v for k, v in description.items() if k not in ('identifier', 'label', 'dataType', 'widget', 'properties', 'group', 'min', 'max', 'enumValues')}, 'default_known': 'default' in props})

def parse_parameters(source):
    result = {}
    decoder = json.JSONDecoder()
    for match in re.finditer('//:\\s*param\\s+custom\\s+', source):
        body = re.sub('(?m)^\\s*//:\\s?', '', source[match.end():])
        props, end = decoder.raw_decode(body.lstrip())
        declaration = re.match('\\s*(?:(?://[^\\n]*\\n)|(?:/\\*[\\s\\S]*?\\*/))*\\s*uniform\\s+(\\w+)\\s+(\\w+)\\s*;', body[end:])
        if not declaration:
            raise ValueError('Shader custom parameter has no uniform declaration.')
        kind, identifier = declaration.groups()
        data_type = {'float': 'Float', 'int': 'Int', 'bool': 'Bool', 'sampler2D': 'ByteArray', 'vec2': 'Float2', 'vec3': 'Float3', 'vec4': 'Float4', 'ivec2': 'Int2', 'ivec3': 'Int3', 'ivec4': 'Int4'}.get(kind, kind)
        widget = props.get('widget', 'Resource' if kind.startswith('sampler') else 'Slider')
        widget = {'combobox': 'Combobox', 'color': 'Color', 'slider': 'Slider', 'checkbox': 'Togglebutton', 'togglebutton': 'Togglebutton'}.get(widget, widget)
        if kind == 'bool':
            widget = 'Togglebutton'
        result[identifier] = ParameterDefinition(identifier, props.get('label', identifier), data_type, widget, deepcopy(props.get('default', 0)), props.get('group', ''), props.get('min'), props.get('max'), [{'label': k, 'value': v} for k, v in props.get('values', {}).items()], props)
    return result

def load_shader():
    data = json.loads(Path(__file__).with_name('shader_catalog.json').read_text(encoding='utf-8-sig'))
    shader = GranitShader.from_dict(data)
    source = shader_path(shader).read_text(encoding='utf-8-sig')
    shader.extra['source_digest'] = hashlib.sha256(source.encode('utf-8')).hexdigest()
    shader.key += '@' + shader.extra['source_digest'][:16]
    shader.parameters = parse_parameters(source)
    channels = {c.identifier: c for c in shader.channels}
    for identifier in re.findall('//:\\s*param\\s+auto\\s+channel_(\\w+)', source):
        channels.setdefault(identifier, ChannelDefinition(identifier, identifier))
    shader.channels = list(channels.values())
    if shader.ramp_parameter not in shader.parameters:
        raise ValueError('Shader ramp parameter is missing from GLSL metadata.')
    return shader

def validate_parameter(definition, value):
    kind = definition.data_type
    if kind == 'Bool':
        if type(value) is not bool:
            raise ValueError('Boolean value required.')
    elif kind == 'ByteArray':
        if not isinstance(value, str):
            raise ValueError('Resource URL required.')
    elif kind.startswith(('Float', 'Int')):
        size = int(kind[-1]) if kind[-1].isdigit() else 1
        values = [value] if size == 1 else value
        if not isinstance(values, (list, tuple)) or len(values) != size:
            raise ValueError('Parameter component count does not match the shader.')
        for i, v in enumerate(values):
            if type(v) not in (int, float) or not math.isfinite(v):
                raise ValueError('Finite number required.')
            if kind.startswith('Int') and int(v) != v:
                raise ValueError('Integer value required.')
            lo, hi = (definition.minimum, definition.maximum)
            if isinstance(lo, list):
                lo = lo[i]
            if isinstance(hi, list):
                hi = hi[i]
            if lo is not None and v < lo or (hi is not None and v > hi):
                raise ValueError('Parameter value is outside the shader range.')
    else:
        raise ValueError(f'Unsupported parameter type: {kind}')
    if definition.enum_values and value not in [v['value'] for v in definition.enum_values]:
        raise ValueError('Invalid enum value.')
    return deepcopy(value)
