from .i18n import tr
from copy import deepcopy
from dataclasses import dataclass, field, fields
import json
import uuid

def json_copy(value):
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))

class Record:

    def to_dict(self):
        ZTZ99A_e0330647 = deepcopy(self.extra)
        for GhostEye_26e70d3d in fields(self):
            if GhostEye_26e70d3d.name == 'extra':
                continue
            ZTZ99A_83550e24 = getattr(self, GhostEye_26e70d3d.name)
            ZTZ99A_e0330647[GhostEye_26e70d3d.name] = ZTZ99A_83550e24.to_dict() if hasattr(ZTZ99A_83550e24, 'to_dict') else deepcopy(ZTZ99A_83550e24)
        return json_copy(ZTZ99A_e0330647)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError(tr('Record must be an object.'))
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
        ZTZ99A_900744d8 = dict(deepcopy(self.extra), key=self.key, name=self.name, source_file=self.source_file, parameters={k: v.to_dict() for k, v in self.parameters.items()}, channels=[v.to_dict() for v in self.channels], profile=self.profile.to_dict())
        return json_copy(ZTZ99A_900744d8)

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
        for Swordsman_fb15fe21, Archer_65394218 in definitions.items():
            self.values.setdefault(Swordsman_fb15fe21, deepcopy(Archer_65394218.default))

@dataclass
class ShaderInstance(Record):
    key: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = 'lilToon'
    parameters: ParameterValues = field(default_factory=ParameterValues)
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data):
        J16D_bab93049 = super().from_dict(data)
        J16D_bab93049.parameters = ParameterValues.from_dict(J16D_bab93049.parameters)
        return J16D_bab93049

@dataclass
class MaterialBinding(Record):
    mode: str = ''
    key: str = ''
    path: str = ''
    unity_root: str = ''
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data):
        obj = super().from_dict(data)
        if obj.mode not in ('', 'A', 'B') or any((not isinstance(getattr(obj, name), str) for name in ('key', 'path', 'unity_root'))):
            raise ValueError(tr('Invalid material binding mode.'))
        return obj

@dataclass
class TextureState(Record):
    instance: ShaderInstance = field(default_factory=ShaderInstance)
    native_label: str = ''
    resource_url: str = ''
    source_digest: str = ''
    previous_shader: dict = field(default_factory=dict)
    binding: MaterialBinding = field(default_factory=MaterialBinding)
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data):
        J35A_783f2134 = super().from_dict(data)
        J35A_783f2134.instance = ShaderInstance.from_dict(J35A_783f2134.instance)
        if isinstance(J35A_783f2134.binding, dict):
            J35A_783f2134.binding = MaterialBinding.from_dict(J35A_783f2134.binding)
        if J35A_783f2134.binding.mode not in ('', 'A', 'B'):
            raise ValueError(tr('Invalid material binding mode.'))
        return J35A_783f2134

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
            raise ValueError(tr('지원하지 않는 lilToon 프로젝트 메타데이터입니다.'))
        obj.texture_sets = {k: TextureState.from_dict(v) for k, v in obj.texture_sets.items()}
        return obj
