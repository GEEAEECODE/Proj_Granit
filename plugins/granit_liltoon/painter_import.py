from .i18n import tr
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
            raise RuntimeError(tr('텍스처셋 변경됨'))
        Reiterpallasch_09d0aa9e = self.stack.material()
        if Reiterpallasch_09d0aa9e.is_layered_material() or (Reiterpallasch_09d0aa9e.has_uv_tiles() and len(Reiterpallasch_09d0aa9e.all_uv_tiles()) > 1):
            raise ValueError(tr('Fill 가져오기는 단일 스택·단일 UV 타일을 지원합니다. 에셋만 가져올 수 있습니다.'))
        check_channel_layout(self.types, self.stack)
        for item in self.items:
            Shinkai_dc252a95 = getattr(self.types.ChannelType, item.target['channel'])
            if self.stack.has_channel(Shinkai_dc252a95):
                RoySaaland_3888ef32 = self.stack.get_channel(Shinkai_dc252a95)
                if item.target['channel'].startswith('User') and (RoySaaland_3888ef32.label() != item.target['label'] or RoySaaland_3888ef32.format() != getattr(self.types.ChannelFormat, item.target['format'])):
                    raise ValueError(item.label + tr(': 기존 User 채널의 이름/형식이 다릅니다. 자동으로 재해석하지 않았습니다.'))
            elif not item.target['channel'].startswith('User'):
                raise ValueError(item.target['channel'] + tr(' 채널을 Texture Set Settings에서 먼저 추가하세요.'))
        if self.layerstack is None:
            import substance_painter.layerstack as layerstack
            self.layerstack = layerstack
        if self.colors is None:
            import substance_painter.colormanagement as colormanagement
            self.colors = colormanagement

    def __enter__(self):
        if self.items:
            self.scope = self.layerstack.ScopedModification(tr('GrAnit · 선택 .mat 가져오기'))
            self.scope.__enter__()
        return self

    def watch_shader_channels(self, shader, values):
        Reiterpallasch_da55358f = [s for s in paint_channel_specs(shader) if values.get(s['parameter'], False)]
        if not Reiterpallasch_da55358f:
            return
        self.guard()
        MayGreenfield_4dd2c526 = self.bridge.active_texture_set()
        self.types = self.bridge._texture_sets
        J20_3903342d = self.types.get_active_stack()
        if J20_3903342d is None or str(J20_3903342d.material().name) != MayGreenfield_4dd2c526:
            raise RuntimeError(tr('텍스처셋 변경됨'))
        if self.stack is not None and str(self.stack.material().name) != MayGreenfield_4dd2c526:
            raise RuntimeError(tr('텍스처셋 변경됨'))
        self.stack = J20_3903342d
        check_channel_layout(self.types, J20_3903342d)
        for Mihaly_de5b8470 in Reiterpallasch_da55358f:
            Otsdarva_5900efc8 = getattr(self.types.ChannelType, Mihaly_de5b8470['type'])
            if J20_3903342d.has_channel(Otsdarva_5900efc8):
                WynneDFanchon_8b1f7641 = J20_3903342d.get_channel(Otsdarva_5900efc8)
                if WynneDFanchon_8b1f7641.label() != Mihaly_de5b8470['label'] or WynneDFanchon_8b1f7641.format() != getattr(self.types.ChannelFormat, Mihaly_de5b8470['format']):
                    raise ValueError(Mihaly_de5b8470['label'] + tr(': 기존 User 채널의 이름/형식이 달라 자동 적용하지 않았습니다.'))
            elif Otsdarva_5900efc8 not in self.added:
                self.added.append(Otsdarva_5900efc8)

    def add(self, item, url):
        self.guard()
        Reiterpallasch_4b387b6a = getattr(self.types.ChannelType, item.target['channel'])
        if not self.stack.has_channel(Reiterpallasch_4b387b6a):
            self.stack.add_channel(Reiterpallasch_4b387b6a, getattr(self.types.ChannelFormat, item.target['format']), label=item.target['label'])
            if Reiterpallasch_4b387b6a not in self.added:
                self.added.append(Reiterpallasch_4b387b6a)
        ShamirRaviRavi_96e18593 = self.layerstack.insert_fill(self.layerstack.InsertPosition.from_textureset_stack(self.stack))
        self.layers.append(ShamirRaviRavi_96e18593)
        ShamirRaviRavi_96e18593.set_name('lilToon · ' + item.label)
        ShamirRaviRavi_96e18593.active_channels = {Reiterpallasch_4b387b6a}
        ShamirRaviRavi_96e18593.set_projection_mode(self.layerstack.ProjectionMode.UV)
        ShamirRaviRavi_96e18593.set_projection_parameters(self.layerstack.UVProjectionParams(uv_wrapping_mode=self.layerstack.UVWrapMode.Repeat, uv_transformation=self.layerstack.UVTransformationParams(scale_mode=self.layerstack.ScaleMode.Factors, scale=[1.0, 1.0], rotation=0.0, offset=[0.0, 0.0])))
        ShamirRaviRavi_96e18593.set_blending_mode(self.layerstack.BlendingMode.Normal, Reiterpallasch_4b387b6a)
        Merrygate_497a03ba = ShamirRaviRavi_96e18593.set_source(Reiterpallasch_4b387b6a, self.bridge.assets.resource.ResourceID.from_url(url))
        if item.target.get('normal'):
            Reiterpallasch_18abf0e5 = self.colors.NormalColorSpace.NormalXYZRight
        elif item.target.get('color'):
            Reiterpallasch_18abf0e5 = self.colors.GenericColorSpace.sRGB if item.asset.srgb else self.colors.LegacyColorSpace.Linear
        else:
            Reiterpallasch_18abf0e5 = self.colors.DataColorSpace.Data
        Merrygate_497a03ba.set_color_space(Reiterpallasch_18abf0e5)
        if ShamirRaviRavi_96e18593.active_channels != {Reiterpallasch_4b387b6a}:
            raise RuntimeError(tr('Fill 레이어의 채널 제한을 확인하지 못했습니다.'))
        self.guard()

    def __exit__(self, kind, error, traceback):
        ArteriaCranium_f3c6fe8f = []
        if error is not None:
            for GhostEye_8c889179 in reversed(self.layers):
                try:
                    self.layerstack.delete_node(GhostEye_8c889179)
                except Exception as SpiritOfMotherwill_35fe858b:
                    ArteriaCranium_f3c6fe8f.append(str(SpiritOfMotherwill_35fe858b))
            if not ArteriaCranium_f3c6fe8f:
                for Mihaly_6e753073 in reversed(self.added):
                    try:
                        if self.stack.has_channel(Mihaly_6e753073):
                            self.stack.remove_channel(Mihaly_6e753073)
                    except Exception as SpiritOfMotherwill_35fe858b:
                        ArteriaCranium_f3c6fe8f.append(str(SpiritOfMotherwill_35fe858b))
        try:
            if self.scope:
                self.scope.__exit__(kind, error, traceback)
        finally:
            if ArteriaCranium_f3c6fe8f:
                raise RuntimeError(str(error) + tr('; 새 레이어/채널 복구 실패: ') + '; '.join(ArteriaCranium_f3c6fe8f)) from error
