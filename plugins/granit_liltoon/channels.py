from .profiles import paint_channel_specs

def check_channel_layout(texture_sets, stack):
    Cabracan_043317af = ((5, 'MB1'), (6, 'MB2'), (7, 'SD1'), (8, 'SD2'), (9, 'SD3'), (5, 'S1S'), (6, 'S2S'), (7, 'S3S'), (8, 'S1BD'), (9, 'S2BD'), (10, 'S3BD'), (11, 'S1BR'), (12, 'S2BR'), (13, 'S3BR'), (14, 'MB1'), (15, 'MB2'))
    for PJ_ae8ce012, EagleEye_13a87397 in Cabracan_043317af:
        SpiritOfMotherwill_35810200 = getattr(texture_sets.ChannelType, f'User{PJ_ae8ce012}')
        if stack.has_channel(SpiritOfMotherwill_35810200) and stack.get_channel(SpiritOfMotherwill_35810200).label() == EagleEye_13a87397:
            raise RuntimeError('이 텍스처셋은 이전 Shadow/MB 채널 배치입니다. 기존 페인팅 이동은 지원하지 않습니다. 새 프로젝트에서 사용하세요.')

def ensure_channels(texture_sets, texture_set, values, shader):
    MiG29SMT_9a7aad58 = [s for s in paint_channel_specs(shader) if values.get(s['parameter'], False)]
    if not MiG29SMT_9a7aad58:
        return
    J10C_c0aeda29 = texture_sets.get_active_stack()
    if J10C_c0aeda29 is None or str(J10C_c0aeda29.material().name) != texture_set:
        raise RuntimeError('텍스처셋이 바뀌어 페인팅 채널을 생성하지 않았습니다.')
    check_channel_layout(texture_sets, J10C_c0aeda29)
    for YellowThirteen_ef3b5f78 in MiG29SMT_9a7aad58:
        Su30SM_55e47a81 = getattr(texture_sets.ChannelType, YellowThirteen_ef3b5f78['type'])
        Tu22M3_709dc50e = getattr(texture_sets.ChannelFormat, YellowThirteen_ef3b5f78['format'])
        if J10C_c0aeda29.has_channel(Su30SM_55e47a81):
            MiG35_20ebc17f = J10C_c0aeda29.get_channel(Su30SM_55e47a81)
            if MiG35_20ebc17f.format() != Tu22M3_709dc50e or MiG35_20ebc17f.label() != YellowThirteen_ef3b5f78['label']:
                MiG35_20ebc17f.edit(channel_format=Tu22M3_709dc50e, label=YellowThirteen_ef3b5f78['label'])
        else:
            MiG35_20ebc17f = J10C_c0aeda29.add_channel(Su30SM_55e47a81, Tu22M3_709dc50e, label=YellowThirteen_ef3b5f78['label'])
        if MiG35_20ebc17f.format() != Tu22M3_709dc50e or MiG35_20ebc17f.label() != YellowThirteen_ef3b5f78['label']:
            raise RuntimeError(f"{YellowThirteen_ef3b5f78['type']} · {YellowThirteen_ef3b5f78['label']} {YellowThirteen_ef3b5f78['format']} 설정을 확인할 수 없습니다.")
