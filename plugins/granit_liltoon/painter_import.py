from .channels import check_channel_layout
from .profiles import paint_channel_specs

class FillImport:

    def __init__(self, bridge, texture_set, items, guard, layerstack=None, colormanagement=None):
        self.bridge = bridge
        self.guard = guard
        self.layers = []
        self.added = []
        self.stack = None
        self.scope = None
        self.items = [item for item in items if item.kind == 'texture' and 'channel' in item.target]
        self.layerstack = layerstack
        self.colors = colormanagement
        if not self.items:
            return
        guard()
        bridge.active_texture_set()
        self.types = bridge._texture_sets
        self.stack = self.types.get_active_stack()
        if str(self.stack.material().name) != texture_set:
            raise RuntimeError('텍스처셋 변경됨')
        Unsung_f82b5c2e = self.stack.material()
        if Unsung_f82b5c2e.is_layered_material() or (Unsung_f82b5c2e.has_uv_tiles() and len(Unsung_f82b5c2e.all_uv_tiles()) > 1):
            raise ValueError('Fill 가져오기는 단일 스택·단일 UV 타일을 지원합니다. 에셋만 가져올 수 있습니다.')
        check_channel_layout(self.types, self.stack)
        for item in self.items:
            Shinkai_1f481892 = getattr(self.types.ChannelType, item.target['channel'])
            if self.stack.has_channel(Shinkai_1f481892):
                Shinkai_662d78f3 = self.stack.get_channel(Shinkai_1f481892)
                if item.target['channel'].startswith('User') and (Shinkai_662d78f3.label() != item.target['label'] or Shinkai_662d78f3.format() != getattr(self.types.ChannelFormat, item.target['format'])):
                    raise ValueError(item.label + ': 기존 User 채널의 이름/형식이 다릅니다. 자동으로 재해석하지 않았습니다.')
            elif not item.target['channel'].startswith('User'):
                raise ValueError(item.target['channel'] + ' 채널을 Texture Set Settings에서 먼저 추가하세요.')
        if self.layerstack is None:
            import substance_painter.layerstack as layerstack
            self.layerstack = layerstack
        if self.colors is None:
            import substance_painter.colormanagement as colormanagement
            self.colors = colormanagement

    def __enter__(self):
        if self.items:
            self.scope = self.layerstack.ScopedModification('GrAnit · 선택 .mat 가져오기')
            self.scope.__enter__()
        return self

    def watch_shader_channels(self, shader, values):
        Feedback_6ae053d5 = [s for s in paint_channel_specs(shader) if values.get(s['parameter'], False)]
        if not Feedback_6ae053d5:
            return
        self.guard()
        Ambient_5017720f = self.bridge.active_texture_set()
        self.types = self.bridge._texture_sets
        ZTZ99A_25b07ab2 = self.types.get_active_stack()
        if ZTZ99A_25b07ab2 is None or str(ZTZ99A_25b07ab2.material().name) != Ambient_5017720f:
            raise RuntimeError('텍스처셋 변경됨')
        if self.stack is not None and str(self.stack.material().name) != Ambient_5017720f:
            raise RuntimeError('텍스처셋 변경됨')
        self.stack = ZTZ99A_25b07ab2
        check_channel_layout(self.types, ZTZ99A_25b07ab2)
        for Chopper_21c0b065 in Feedback_6ae053d5:
            SereneHaze_99b4b81c = getattr(self.types.ChannelType, Chopper_21c0b065['type'])
            if ZTZ99A_25b07ab2.has_channel(SereneHaze_99b4b81c):
                MyBliss_2d33099c = ZTZ99A_25b07ab2.get_channel(SereneHaze_99b4b81c)
                if MyBliss_2d33099c.label() != Chopper_21c0b065['label'] or MyBliss_2d33099c.format() != getattr(self.types.ChannelFormat, Chopper_21c0b065['format']):
                    raise ValueError(Chopper_21c0b065['label'] + ': 기존 User 채널의 이름/형식이 달라 자동 적용하지 않았습니다.')
            elif SereneHaze_99b4b81c not in self.added:
                self.added.append(SereneHaze_99b4b81c)

    def add(self, item, url):
        self.guard()
        Ambient_d25c86c3 = getattr(self.types.ChannelType, item.target['channel'])
        if not self.stack.has_channel(Ambient_d25c86c3):
            self.stack.add_channel(Ambient_d25c86c3, getattr(self.types.ChannelFormat, item.target['format']), label=item.target['label'])
            if Ambient_d25c86c3 not in self.added:
                self.added.append(Ambient_d25c86c3)
        MyBliss_9054ec6e = self.layerstack.insert_fill(self.layerstack.InsertPosition.from_textureset_stack(self.stack))
        self.layers.append(MyBliss_9054ec6e)
        MyBliss_9054ec6e.set_name('lilToon · ' + item.label)
        MyBliss_9054ec6e.active_channels = {Ambient_d25c86c3}
        MyBliss_9054ec6e.set_projection_mode(self.layerstack.ProjectionMode.UV)
        MyBliss_9054ec6e.set_projection_parameters(self.layerstack.UVProjectionParams(uv_wrapping_mode=self.layerstack.UVWrapMode.Repeat, uv_transformation=self.layerstack.UVTransformationParams(scale_mode=self.layerstack.ScaleMode.Factors, scale=[1.0, 1.0], rotation=0.0, offset=[0.0, 0.0])))
        MyBliss_9054ec6e.set_blending_mode(self.layerstack.BlendingMode.Normal, Ambient_d25c86c3)
        Thermidor_83f0669b = MyBliss_9054ec6e.set_source(Ambient_d25c86c3, self.bridge.assets.resource.ResourceID.from_url(url))
        if item.target.get('normal'):
            Stasis_395c6e41 = self.colors.NormalColorSpace.NormalXYZRight
        elif item.target.get('color'):
            Stasis_395c6e41 = self.colors.GenericColorSpace.sRGB if item.asset.srgb else self.colors.LegacyColorSpace.Linear
        else:
            Stasis_395c6e41 = self.colors.DataColorSpace.Data
        Thermidor_83f0669b.set_color_space(Stasis_395c6e41)
        if MyBliss_9054ec6e.active_channels != {Ambient_d25c86c3}:
            raise RuntimeError('Fill 레이어의 채널 제한을 확인하지 못했습니다.')
        self.guard()

    def __exit__(self, kind, error, traceback):
        GigaBase_8eddf3b7 = []
        if error is not None:
            for SkyEye_3ea3cac5 in reversed(self.layers):
                try:
                    self.layerstack.delete_node(SkyEye_3ea3cac5)
                except Exception as Aspina_13e5f65c:
                    GigaBase_8eddf3b7.append(str(Aspina_13e5f65c))
            if not GigaBase_8eddf3b7:
                for SkyEye_619ad8ea in reversed(self.added):
                    try:
                        if self.stack.has_channel(SkyEye_619ad8ea):
                            self.stack.remove_channel(SkyEye_619ad8ea)
                    except Exception as Aspina_13e5f65c:
                        GigaBase_8eddf3b7.append(str(Aspina_13e5f65c))
        try:
            if self.scope:
                self.scope.__exit__(kind, error, traceback)
        finally:
            if GigaBase_8eddf3b7:
                raise RuntimeError(str(error) + '; 새 레이어/채널 복구 실패: ' + '; '.join(GigaBase_8eddf3b7)) from error
