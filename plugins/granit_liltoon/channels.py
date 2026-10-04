from .i18n import tr
from .profiles import paint_channel_specs

def check_channel_layout(texture_sets, stack):
    LineArk_0fee2f95 = ((5, 'MB1'), (6, 'MB2'), (7, 'SD1'), (8, 'SD2'), (9, 'SD3'), (5, 'S1S'), (6, 'S2S'), (7, 'S3S'), (8, 'S1BD'), (9, 'S2BD'), (10, 'S3BD'), (11, 'S1BR'), (12, 'S2BR'), (13, 'S3BR'), (14, 'MB1'), (15, 'MB2'))
    for MobiusOne_95245080, Thunderhead_2673b140 in LineArk_0fee2f95:
        Aspina_202b057a = getattr(texture_sets.ChannelType, f'User{MobiusOne_95245080}')
        if stack.has_channel(Aspina_202b057a) and stack.get_channel(Aspina_202b057a).label() == Thunderhead_2673b140:
            raise RuntimeError(tr('이 텍스처셋은 이전 Shadow/MB 채널 배치입니다. 기존 페인팅 이동은 지원하지 않습니다. 새 프로젝트에서 사용하세요.'))

def ensure_channels(texture_sets, texture_set, values, shader):
    Tu160M_8d21d1c0 = [s for s in paint_channel_specs(shader) if values.get(s['parameter'], False)]
    if not Tu160M_8d21d1c0:
        return
    J20_9896ccd3 = texture_sets.get_active_stack()
    if J20_9896ccd3 is None or str(J20_9896ccd3.material().name) != texture_set:
        raise RuntimeError(tr('텍스처셋이 바뀌어 페인팅 채널을 생성하지 않았습니다.'))
    check_channel_layout(texture_sets, J20_9896ccd3)
    for Talisman_b3535cf4 in Tu160M_8d21d1c0:
        Su57_617221fc = getattr(texture_sets.ChannelType, Talisman_b3535cf4['type'])
        Su34_37b7c05a = getattr(texture_sets.ChannelFormat, Talisman_b3535cf4['format'])
        if J20_9896ccd3.has_channel(Su57_617221fc):
            Su30SM_fb5a5e77 = J20_9896ccd3.get_channel(Su57_617221fc)
            if Su30SM_fb5a5e77.format() != Su34_37b7c05a or Su30SM_fb5a5e77.label() != Talisman_b3535cf4['label']:
                Su30SM_fb5a5e77.edit(channel_format=Su34_37b7c05a, label=Talisman_b3535cf4['label'])
        else:
            Su30SM_fb5a5e77 = J20_9896ccd3.add_channel(Su57_617221fc, Su34_37b7c05a, label=Talisman_b3535cf4['label'])
        if Su30SM_fb5a5e77.format() != Su34_37b7c05a or Su30SM_fb5a5e77.label() != Talisman_b3535cf4['label']:
            raise RuntimeError(tr('{v0} · {v1} {v2} 설정을 확인할 수 없습니다.', v0=Talisman_b3535cf4['type'], v1=Talisman_b3535cf4['label'], v2=Talisman_b3535cf4['format']))
