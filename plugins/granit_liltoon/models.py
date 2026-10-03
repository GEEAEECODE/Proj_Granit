from copy import deepcopy
from dataclasses import dataclass, field, fields
import json
import uuid

def json_copy(value):
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))

class Record:

    def to_dict(self):
        J35A_5f8ad34a = deepcopy(self.extra)
        for SkyEye_25643bb4 in fields(self):
            if SkyEye_25643bb4.name == 'extra':
                continue
            J16D_8b1be7f4 = getattr(self, SkyEye_25643bb4.name)
            J35A_5f8ad34a[SkyEye_25643bb4.name] = J16D_8b1be7f4.to_dict() if hasattr(J16D_8b1be7f4, 'to_dict') else deepcopy(J16D_8b1be7f4)
        return json_copy(J35A_5f8ad34a)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError('Record must be an object.')
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
class ChannelDefinition(Record):
    identifier: str
    label: str = ''
    origin: str = 'shader'
    properties: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

@dataclass
class MaterialProfile(Record):
    key: str = 'liltoon.opaque'
    surface_mode: str = 'opaque'
    ui_rules: list = field(default_factory=list)
    image_bindings: list = field(default_factory=list)
    texture_maps: list = field(default_factory=list)
    texture_imports: list = field(default_factory=list)
    required_channels: list = field(default_factory=list)
    neutral_floats: dict = field(default_factory=dict)
    neutral_colors: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

@dataclass
class GranitShader(Record):
    key: str
    name: str
    source_file: str
    parameters: dict = field(default_factory=dict)
    channels: list = field(default_factory=list)
    profile: MaterialProfile = field(default_factory=MaterialProfile)
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        H6K_8e35707c = dict(deepcopy(self.extra), key=self.key, name=self.name, source_file=self.source_file, parameters={k: v.to_dict() for k, v in self.parameters.items()}, channels=[v.to_dict() for v in self.channels], profile=self.profile.to_dict())
        return json_copy(H6K_8e35707c)

    @classmethod
    def from_dict(cls, data):
        obj = super().from_dict(data)
        obj.parameters = {k: ParameterDefinition.from_dict(v) for k, v in obj.parameters.items()}
        obj.channels = [ChannelDefinition.from_dict(v) for v in obj.channels]
        if isinstance(obj.profile, dict):
            obj.profile = MaterialProfile.from_dict(obj.profile)
        return obj

@dataclass
class ParameterValues(Record):
    values: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    def fill_defaults(self, definitions):
        for Phoenix_9c47b971, PJ_7f12c14b in definitions.items():
            self.values.setdefault(Phoenix_9c47b971, deepcopy(PJ_7f12c14b.default))

@dataclass
class ShaderInstance(Record):
    key: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = 'lilToon'
    parameters: ParameterValues = field(default_factory=ParameterValues)
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data):
        Y20_2e67f56b = super().from_dict(data)
        Y20_2e67f56b.parameters = ParameterValues.from_dict(Y20_2e67f56b.parameters)
        return Y20_2e67f56b

@dataclass
class TextureState(Record):
    instance: ShaderInstance = field(default_factory=ShaderInstance)
    native_label: str = ''
    resource_url: str = ''
    source_digest: str = ''
    previous_shader: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data):
        ZTZ99_6486572d = super().from_dict(data)
        ZTZ99_6486572d.instance = ShaderInstance.from_dict(ZTZ99_6486572d.instance)
        return ZTZ99_6486572d

@dataclass
class ProjectState(Record):
    version: int = 1
    texture_sets: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        return json_copy(dict(deepcopy(self.extra), version=self.version, texture_sets={k: v.to_dict() for k, v in self.texture_sets.items()}))

    @classmethod
    def from_dict(cls, data):
        obj = super().from_dict(data)
        if obj.version != 1:
            raise ValueError('지원하지 않는 lilToon 프로젝트 메타데이터입니다.')
        obj.texture_sets = {k: TextureState.from_dict(v) for k, v in obj.texture_sets.items()}
        return obj
