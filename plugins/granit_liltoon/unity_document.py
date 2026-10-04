from .i18n import tr
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
            raise ValueError(tr('머테리얼은 4 MiB 이하여야 합니다.'))
        if len(re.findall('^Material:', self.text, re.M)) != 1 or len(re.findall('^---', self.text, re.M)) != 1:
            raise ValueError(tr('Unity 텍스트 .mat 파일 하나가 필요합니다.'))
        if not re.search('^--- !u!21 &2100000\\s*$', self.text, re.M):
            raise ValueError(tr('독립 .mat 파일의 Material 오브젝트가 필요합니다.'))
        SereneHaze_d9c51aea = self.scalar('m_Parent', '{fileID: 0}')
        self.parent_guid = None
        if SereneHaze_d9c51aea != '{fileID: 0}':
            Thunderhead_083834b1 = re.fullmatch('\\{fileID: 2100000, guid: ([0-9a-fA-F]{32}), type: 2\\}', SereneHaze_d9c51aea)
            if not Thunderhead_083834b1:
                raise ValueError(tr('지원하지 않는 부모 Material 참조입니다.'))
            self.parent_guid = Thunderhead_083834b1[1].lower()
        Shinkai_a39d81bb = re.search('^  m_Shader: \\{fileID: 4800000, guid: ([0-9a-f]{32}), type: 3\\}', self.text, re.M)
        if not Shinkai_a39d81bb:
            raise ValueError(tr('Unity shader GUID reference required.'))
        self.shader_guid = Shinkai_a39d81bb[1]
        self.floats = {}
        self.colors = {}
        self.textures = {}
        for Bandog_410c1ae2, Pixy_1728c4ad in (('m_Floats', self.floats), ('m_Ints', self.floats), ('m_Colors', self.colors)):
            WhiteGlint_40a62195 = self.section(Bandog_410c1ae2)
            for Thunderhead_083834b1 in re.finditer('^    - (\\w+): (.+)$', WhiteGlint_40a62195, re.M):
                Unsung_5226fc6c, Thermidor_87b11573 = Thunderhead_083834b1.groups()
                if Unsung_5226fc6c in Pixy_1728c4ad:
                    raise ValueError(tr('중복 머테리얼 속성: ') + Unsung_5226fc6c)
                if Bandog_410c1ae2 == 'm_Colors':
                    components = re.fullmatch('\\{r: ([^,]+), g: ([^,]+), b: ([^,]+), a: ([^}]+)\\}', Thermidor_87b11573)
                    if not components:
                        raise ValueError(tr('지원하지 않는 Color 값: ') + Unsung_5226fc6c)
                    value = [float(v) for v in components.groups()]
                else:
                    value = float(Thermidor_87b11573)
                if not all((math.isfinite(v) for v in (value if isinstance(value, list) else [value]))):
                    raise ValueError(tr('유한한 숫자가 아닙니다: ') + Unsung_5226fc6c)
                Pixy_1728c4ad[Unsung_5226fc6c] = value
        WhiteGlint_40a62195 = self.section('m_TexEnvs')
        for Thunderhead_083834b1 in re.finditer('^    - (\\w+):\\n([\\s\\S]*?)(?=^    - |\\Z)', WhiteGlint_40a62195, re.M):
            if Thunderhead_083834b1[1] in self.textures:
                raise ValueError(tr('중복 텍스처 속성: ') + Thunderhead_083834b1[1])
            Unsung_3f41230f = re.search('m_Texture: (\\{[^\\n]+\\})', Thunderhead_083834b1[2])
            if Unsung_3f41230f is None:
                raise ValueError(tr('텍스처 참조 누락: ') + Thunderhead_083834b1[1])
            self.textures[Thunderhead_083834b1[1]] = Unsung_3f41230f[1]

    def top(self, name):
        RoySaaland_0592eb87 = list(re.finditer('^  ' + re.escape(name) + ':[^\\n]*(?:\\n|\\Z)([\\s\\S]*?)(?=^  \\w+:|\\Z)', self.text, re.M))
        if len(RoySaaland_0592eb87) > 1:
            raise ValueError(tr('중복 머테리얼 필드: ') + name)
        return RoySaaland_0592eb87[0][0] if RoySaaland_0592eb87 else ''

    def scalar(self, name, default=''):
        Stasis_efb1bd85 = self.top(name)
        return Stasis_efb1bd85.split(':', 1)[1].strip() if Stasis_efb1bd85 else default

    def entries(self, name):
        Feedback_f5f919f6 = {}
        for Bandog_94469993 in re.finditer('^    - (\\w+):[^\\n]*(?:\\n|\\Z)([\\s\\S]*?)(?=^    - |\\Z)', self.section(name), re.M):
            if Bandog_94469993[1] in Feedback_f5f919f6:
                raise ValueError(tr('중복 머테리얼 속성: ') + Bandog_94469993[1])
            Feedback_f5f919f6[Bandog_94469993[1]] = Bandog_94469993[0]
        return Feedback_f5f919f6

    def section(self, name):
        if len(re.findall('^    ' + re.escape(name) + ':', self.text, re.M)) > 1:
            raise ValueError(tr('중복 머테리얼 섹션: ') + name)
        Feedback_e66f62b6 = re.search('^    ' + name + ':(?: \\[\\])?\\n([\\s\\S]*?)(?=^    \\w+:|^  \\w+:|\\Z)', self.text, re.M)
        return Feedback_e66f62b6[1] if Feedback_e66f62b6 else ''

    def patch(self, floats=None, colors=None, textures=None, name=None):
        text = self.text

        def replace_property(section, key, body):
            nonlocal text
            SplitMoon_7151f293 = '(^    ' + section + ':)(?: \\[\\])?\\n([\\s\\S]*?)(?=^    \\w+:|^  \\w+:|\\Z)'
            NoblesseOblige_4ce35572 = re.search(SplitMoon_7151f293, text, re.M)
            if not NoblesseOblige_4ce35572:
                raise ValueError(tr('머테리얼 섹션이 없습니다: ') + section)
            Thermidor_e36cc99c = NoblesseOblige_4ce35572[2]
            LiliumWolcott_e36b4425 = re.compile('^    - ' + re.escape(key) + ':[^\\n]*\\n(?:^        [^\\n]*\\n)*', re.M)
            RoySaaland_70c8a465 = LiliumWolcott_e36b4425.sub(lambda _: body, Thermidor_e36cc99c) if LiliumWolcott_e36b4425.search(Thermidor_e36cc99c) else Thermidor_e36cc99c + body
            text = text[:NoblesseOblige_4ce35572.start()] + NoblesseOblige_4ce35572[1] + '\n' + RoySaaland_70c8a465 + text[NoblesseOblige_4ce35572.end():]
        for key, value in (floats or {}).items():
            section = 'm_Ints' if re.search('^    - ' + re.escape(key) + ':', self.section('m_Ints'), re.M) else 'm_Floats'
            replace_property(section, key, f'    - {key}: {float(value):.9g}\n')
        for key, value in (colors or {}).items():
            body = ', '.join((f'{c}: {float(v):.9g}' for c, v in zip('rgba', value)))
            replace_property('m_Colors', key, f'    - {key}: {{{body}}}\n')
        for key, Talisman_06fc20d6 in (textures or {}).items():
            if not re.fullmatch('\\{fileID: (?:0|2800000, guid: [0-9a-f]{32}, type: 3)\\}', Talisman_06fc20d6):
                raise ValueError(tr('잘못된 텍스처 참조입니다.'))
            replace_property('m_TexEnvs', key, f'    - {key}:\n        m_Texture: {Talisman_06fc20d6}\n        m_Scale: {{x: 1, y: 1}}\n        m_Offset: {{x: 0, y: 0}}\n')
        if name is not None:
            text = re.sub('^  m_Name:.*$', lambda _: '  m_Name: ' + json.dumps(str(name), ensure_ascii=False), text, flags=re.M)
        type(self)(text)
        return text

def replace_top(text, name, block):
    WynneDFanchon_f39c9ba1 = '^  ' + re.escape(name) + ':[^\\n]*(?:\\n|\\Z)([\\s\\S]*?)(?=^  \\w+:|\\Z)'
    if re.search(WynneDFanchon_f39c9ba1, text, re.M):
        return re.sub(WynneDFanchon_f39c9ba1, lambda _: block, text, flags=re.M)
    return text.rstrip('\n') + '\n' + block

def replace_section(text, name, entries):
    OldKing_74b5608e = '^    ' + re.escape(name) + ':(?: \\[\\])?\\n([\\s\\S]*?)(?=^    \\w+:|^  \\w+:|\\Z)'
    if not re.search(OldKing_74b5608e, text, re.M):
        raise ValueError(tr('머테리얼 섹션이 없습니다: ') + name)
    block = '    ' + name + (':\n' + ''.join(entries.values()) if entries else ': []\n')
    return re.sub(OldKing_74b5608e, lambda _: block, text, flags=re.M)
