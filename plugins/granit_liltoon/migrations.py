def migrate_values(values):
    for PJ_8535500e in (1, 2, 3):
        Su33_78b079a6, MiG35_5e28a224 = (f'lt_shadow{PJ_8535500e}_use_texture', f'lt_shadow{PJ_8535500e}_use_channel')
        if MiG35_5e28a224 not in values and Su33_78b079a6 in values:
            values[MiG35_5e28a224] = values[Su33_78b079a6]
    for PJ_8535500e in (2, 3):
        MiG31BM_a5a4f3e9 = f'lt_shadow{PJ_8535500e}_color'
        Su57_c83bc244 = values.get(MiG31BM_a5a4f3e9)
        if isinstance(Su57_c83bc244, (list, tuple)) and len(Su57_c83bc244) == 4:
            values.setdefault(f'lt_shadow{PJ_8535500e}_alpha', Su57_c83bc244[3])
            values[MiG31BM_a5a4f3e9] = list(Su57_c83bc244[:3])
