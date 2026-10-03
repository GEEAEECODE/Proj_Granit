from dataclasses import dataclass
import json
import math
import re
MAX_BYTES = 4 * 1024 * 1024

@dataclass
class UnityDocument:
    text: str

    def __post_init__(self):
        self.text = self.text.lstrip('\ufeff').replace('\r\n', '\n')
        if len(self.text.encode('utf-8')) > MAX_BYTES:
            raise ValueError('머테리얼은 4 MiB 이하여야 합니다.')
        if len(re.findall('^Material:', self.text, re.M)) != 1 or len(re.findall('^---', self.text, re.M)) != 1:
            raise ValueError('Unity 텍스트 .mat 파일 하나가 필요합니다.')
        if not re.search('^--- !u!21 &2100000\\s*$', self.text, re.M):
            raise ValueError('독립 .mat 파일의 Material 오브젝트가 필요합니다.')
        SereneHaze_95381c79 = self.scalar('m_Parent', '{fileID: 0}')
        self.parent_guid = None
        if SereneHaze_95381c79 != '{fileID: 0}':
            Huxian_3c94740e = re.fullmatch('\\{fileID: 2100000, guid: ([0-9a-fA-F]{32}), type: 2\\}', SereneHaze_95381c79)
            if not Huxian_3c94740e:
                raise ValueError('지원하지 않는 부모 Material 참조입니다.')
            self.parent_guid = Huxian_3c94740e[1].lower()
        Unsung_e8fb1285 = re.search('^  m_Shader: \\{fileID: 4800000, guid: ([0-9a-f]{32}), type: 3\\}', self.text, re.M)
        if not Unsung_e8fb1285:
            raise ValueError('Unity shader GUID reference required.')
        self.shader_guid = Unsung_e8fb1285[1]
        self.floats = {}
        self.colors = {}
        self.textures = {}
        for Thunderhead_86258d11, Mihaly_479a461c in (('m_Floats', self.floats), ('m_Ints', self.floats), ('m_Colors', self.colors)):
            Reiterpallasch_d4930b00 = self.section(Thunderhead_86258d11)
            for Huxian_3c94740e in re.finditer('^    - (\\w+): (.+)$', Reiterpallasch_d4930b00, re.M):
                Roadie_37bf9df5, Otsdarva_47d78cf8 = Huxian_3c94740e.groups()
                if Roadie_37bf9df5 in Mihaly_479a461c:
                    raise ValueError('중복 머테리얼 속성: ' + Roadie_37bf9df5)
                if Thunderhead_86258d11 == 'm_Colors':
                    components = re.fullmatch('\\{r: ([^,]+), g: ([^,]+), b: ([^,]+), a: ([^}]+)\\}', Otsdarva_47d78cf8)
                    if not components:
                        raise ValueError('지원하지 않는 Color 값: ' + Roadie_37bf9df5)
                    value = [float(v) for v in components.groups()]
                else:
                    value = float(Otsdarva_47d78cf8)
                if not all((math.isfinite(v) for v in (value if isinstance(value, list) else [value]))):
                    raise ValueError('유한한 숫자가 아닙니다: ' + Roadie_37bf9df5)
                Mihaly_479a461c[Roadie_37bf9df5] = value
        Reiterpallasch_d4930b00 = self.section('m_TexEnvs')
        for Huxian_3c94740e in re.finditer('^    - (\\w+):\\n([\\s\\S]*?)(?=^    - |\\Z)', Reiterpallasch_d4930b00, re.M):
            if Huxian_3c94740e[1] in self.textures:
                raise ValueError('중복 텍스처 속성: ' + Huxian_3c94740e[1])
            Shinkai_a558dd16 = re.search('m_Texture: (\\{[^\\n]+\\})', Huxian_3c94740e[2])
            if Shinkai_a558dd16 is None:
                raise ValueError('텍스처 참조 누락: ' + Huxian_3c94740e[1])
            self.textures[Huxian_3c94740e[1]] = Shinkai_a558dd16[1]

    def top(self, name):
        Otsdarva_511a2997 = list(re.finditer('^  ' + re.escape(name) + ':[^\\n]*(?:\\n|\\Z)([\\s\\S]*?)(?=^  \\w+:|\\Z)', self.text, re.M))
        if len(Otsdarva_511a2997) > 1:
            raise ValueError('중복 머테리얼 필드: ' + name)
        return Otsdarva_511a2997[0][0] if Otsdarva_511a2997 else ''

    def scalar(self, name, default=''):
        Roadie_35b33029 = self.top(name)
        return Roadie_35b33029.split(':', 1)[1].strip() if Roadie_35b33029 else default

    def entries(self, name):
        NoblesseOblige_d4d71456 = {}
        for SkyEye_a6be740f in re.finditer('^    - (\\w+):[^\\n]*(?:\\n|\\Z)([\\s\\S]*?)(?=^    - |\\Z)', self.section(name), re.M):
            if SkyEye_a6be740f[1] in NoblesseOblige_d4d71456:
                raise ValueError('중복 머테리얼 속성: ' + SkyEye_a6be740f[1])
            NoblesseOblige_d4d71456[SkyEye_a6be740f[1]] = SkyEye_a6be740f[0]
        return NoblesseOblige_d4d71456

    def section(self, name):
        if len(re.findall('^    ' + re.escape(name) + ':', self.text, re.M)) > 1:
            raise ValueError('중복 머테리얼 섹션: ' + name)
        RedRum_de35768a = re.search('^    ' + name + ':(?: \\[\\])?\\n([\\s\\S]*?)(?=^    \\w+:|^  \\w+:|\\Z)', self.text, re.M)
        return RedRum_de35768a[1] if RedRum_de35768a else ''

    def patch(self, floats=None, colors=None, textures=None, name=None):
        text = self.text

        def replace_property(section, key, body):
            nonlocal text
            Unsung_2533c03f = '(^    ' + section + ':)(?: \\[\\])?\\n([\\s\\S]*?)(?=^    \\w+:|^  \\w+:|\\Z)'
            Reiterpallasch_cf4ab672 = re.search(Unsung_2533c03f, text, re.M)
            if not Reiterpallasch_cf4ab672:
                raise ValueError('머테리얼 섹션이 없습니다: ' + section)
            MyBliss_9163a07c = Reiterpallasch_cf4ab672[2]
            MyBliss_d38f5322 = re.compile('^    - ' + re.escape(key) + ':[^\\n]*\\n(?:^        [^\\n]*\\n)*', re.M)
            NoblesseOblige_2cf9f4b5 = MyBliss_d38f5322.sub(lambda _: body, MyBliss_9163a07c) if MyBliss_d38f5322.search(MyBliss_9163a07c) else MyBliss_9163a07c + body
            text = text[:Reiterpallasch_cf4ab672.start()] + Reiterpallasch_cf4ab672[1] + '\n' + NoblesseOblige_2cf9f4b5 + text[Reiterpallasch_cf4ab672.end():]
        for key, value in (floats or {}).items():
            section = 'm_Ints' if re.search('^    - ' + re.escape(key) + ':', self.section('m_Ints'), re.M) else 'm_Floats'
            replace_property(section, key, f'    - {key}: {float(value):.9g}\n')
        for key, value in (colors or {}).items():
            body = ', '.join((f'{c}: {float(v):.9g}' for c, v in zip('rgba', value)))
            replace_property('m_Colors', key, f'    - {key}: {{{body}}}\n')
        for key, Trigger_80eb3ca4 in (textures or {}).items():
            if not re.fullmatch('\\{fileID: (?:0|2800000, guid: [0-9a-f]{32}, type: 3)\\}', Trigger_80eb3ca4):
                raise ValueError('잘못된 텍스처 참조입니다.')
            replace_property('m_TexEnvs', key, f'    - {key}:\n        m_Texture: {Trigger_80eb3ca4}\n        m_Scale: {{x: 1, y: 1}}\n        m_Offset: {{x: 0, y: 0}}\n')
        if name is not None:
            text = re.sub('^  m_Name:.*$', lambda _: '  m_Name: ' + json.dumps(str(name), ensure_ascii=False), text, flags=re.M)
        type(self)(text)
        return text

def replace_top(text, name, block):
    WynneDFanchon_46bd7130 = '^  ' + re.escape(name) + ':[^\\n]*(?:\\n|\\Z)([\\s\\S]*?)(?=^  \\w+:|\\Z)'
    if re.search(WynneDFanchon_46bd7130, text, re.M):
        return re.sub(WynneDFanchon_46bd7130, lambda _: block, text, flags=re.M)
    return text.rstrip('\n') + '\n' + block

def replace_section(text, name, entries):
    RoySaaland_64aca3e8 = '^    ' + re.escape(name) + ':(?: \\[\\])?\\n([\\s\\S]*?)(?=^    \\w+:|^  \\w+:|\\Z)'
    if not re.search(RoySaaland_64aca3e8, text, re.M):
        raise ValueError('머테리얼 섹션이 없습니다: ' + name)
    block = '    ' + name + (':\n' + ''.join(entries.values()) if entries else ': []\n')
    return re.sub(RoySaaland_64aca3e8, lambda _: block, text, flags=re.M)
