from copy import deepcopy
from dataclasses import dataclass, field, fields
import json
import uuid
from .gradient import Gradient

def json_copy(value):
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))

class Record:

    def to_dict(self):
        result = deepcopy(self.extra)
        for item in fields(self):
            if item.name == 'extra':
                continue
            value = getattr(self, item.name)
            result[item.name] = value.to_dict() if hasattr(value, 'to_dict') else deepcopy(value)
        return json_copy(result)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError(f'{cls.__name__}: object required')
        names = {f.name for f in fields(cls)} - {'extra'}
        return cls(**{k: deepcopy(v) for k, v in data.items() if k in names}, extra={k: deepcopy(v) for k, v in data.items() if k not in names})

@dataclass
class ParameterDefinition(Record):
    identifier: str
    label: str = ''
    data_type: str = 'Float'
    widget: str = 'Slider'
    default: object = 0.0
    group: str = ''
    minimum: object = None
    maximum: object = None
    enum_values: list = field(default_factory=list)
    properties: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

@dataclass
class ParameterValues(Record):
    values: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    def fill_defaults(self, definitions):
        for definition in definitions.values():
            self.values.setdefault(definition.identifier, deepcopy(definition.default))

@dataclass
class ChannelDefinition(Record):
    identifier: str
    label: str = ''
    origin: str = 'shader'
    properties: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

@dataclass
class GranitShader(Record):
    key: str
    name: str
    source_file: str
    ramp_parameter: str = 'ramp_texture'
    parameters: dict = field(default_factory=dict)
    channels: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        result = deepcopy(self.extra)
        result.update(key=self.key, name=self.name, source_file=self.source_file, ramp_parameter=self.ramp_parameter, parameters={k: v.to_dict() for k, v in self.parameters.items()}, channels=[v.to_dict() for v in self.channels])
        return json_copy(result)

    @classmethod
    def from_dict(cls, data):
        result = super().from_dict(data)
        result.parameters = {k: ParameterDefinition.from_dict(v) for k, v in result.parameters.items()}
        result.channels = [ChannelDefinition.from_dict(v) for v in result.channels]
        return result

@dataclass
class GranitShaderInstance(Record):
    key: str
    shader_key: str
    name: str
    parameters: ParameterValues = field(default_factory=ParameterValues)
    gradient: object = field(default_factory=Gradient.default)
    revision: int = 0
    extra: dict = field(default_factory=dict)

    @classmethod
    def create(cls, shader, name):
        values = ParameterValues()
        values.fill_defaults(shader.parameters)
        return cls(uuid.uuid4().hex, shader.key, name, values)

    @classmethod
    def from_dict(cls, data):
        result = super().from_dict(data)
        if not result.key or not result.name:
            raise ValueError('셰이더 ID/이름이 비어 있습니다.')
        result.parameters = ParameterValues.from_dict(result.parameters)
        result.gradient = Gradient.from_dict(result.gradient) if result.gradient is not None else None
        return result

    def duplicate(self, name):
        result = self.from_dict(self.to_dict())
        result.key, result.name, result.revision = (uuid.uuid4().hex, name, 0)
        return result

@dataclass
class PainterBinding(Record):
    instance_key: str
    native_label: str
    resource_url: str = ''
    ramp_url: str = ''
    applied_revision: int = -1
    extra: dict = field(default_factory=dict)

@dataclass
class TextureSetBinding(Record):
    texture_set: str
    instance_key: str
    previous_shader: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

@dataclass
class ProjectState:
    shaders: dict = field(default_factory=dict)
    instances: dict = field(default_factory=dict)
    painter_bindings: dict = field(default_factory=dict)
    texture_bindings: dict = field(default_factory=dict)
    selected: str = ''
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        result = deepcopy(self.extra)
        result.update(version=1, selected=self.selected)
        for name in ('shaders', 'instances', 'painter_bindings', 'texture_bindings'):
            result[name] = {k: v.to_dict() for k, v in getattr(self, name).items()}
        return json_copy(result)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
            raise ValueError('지원하지 않는 GrAnit 프로젝트 데이터 버전입니다.')
        types = {'shaders': GranitShader, 'instances': GranitShaderInstance, 'painter_bindings': PainterBinding, 'texture_bindings': TextureSetBinding}
        known = {'version', 'selected', *types}
        result = cls(selected=data.get('selected', ''), extra={k: v for k, v in data.items() if k not in known})
        for name, kind in types.items():
            setattr(result, name, {k: kind.from_dict(v) for k, v in data.get(name, {}).items()})
        for key, instance in result.instances.items():
            if key != instance.key or instance.shader_key not in result.shaders:
                raise ValueError('셰이더 인스턴스 참조가 올바르지 않습니다.')
            instance.parameters.fill_defaults(result.shaders[instance.shader_key].parameters)
        for key, binding in result.painter_bindings.items():
            if key not in result.instances or binding.instance_key != key or (not binding.native_label):
                raise ValueError('Painter 연결 기록이 올바르지 않습니다.')
        if set(result.instances) != set(result.painter_bindings) and result.painter_bindings:
            raise ValueError('일부 인스턴스의 Painter 연결 기록이 없습니다.')
        for name, binding in result.texture_bindings.items():
            if name != binding.texture_set or binding.instance_key not in result.painter_bindings:
                raise ValueError('텍스처셋 연결 기록이 올바르지 않습니다.')
        if result.selected and result.selected not in result.instances:
            result.selected = next(iter(result.instances), '')
        return result
