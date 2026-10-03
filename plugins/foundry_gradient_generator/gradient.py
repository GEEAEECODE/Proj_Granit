from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass, replace
import colorsys
import json
import math
from pathlib import Path
import re
import struct
import unicodedata
import uuid
import zlib
MAX_STOPS = 32
WIDTH, HEIGHT = (1024, 16)
INTERPOLATIONS = ('LINEAR', 'CONSTANT', 'EASE', 'CARDINAL', 'B_SPLINE')
COLOR_MODES = ('RGB', 'HSV', 'HSL')
HUE_MODES = ('NEAR', 'FAR', 'CW', 'CCW')

def clamp(value):
    return min(1.0, max(0.0, value))

def validate_name(value: str) -> str:
    name = unicodedata.normalize('NFC', value).strip()
    if not name or len(name) > 96:
        raise ValueError('이름을 1~96자로 입력하세요.')
    if re.search('[\\x00-\\x1f<>:"/\\\\|?*#%]', name) or name.endswith('.'):
        raise ValueError('이름에 경로 문자, 제어 문자 또는 <>:"/\\|?*#%를 사용할 수 없습니다.')
    if name.lower().endswith('.png'):
        raise ValueError('이름에는 .png 확장자를 제외하세요.')
    return name

@dataclass(frozen=True)
class Stop:
    key: str
    position: float
    color: tuple[float, float, float, float]

    @classmethod
    def create(cls, position, color):
        return cls(uuid.uuid4().hex, float(position), tuple(color))

@dataclass(frozen=True)
class Gradient:
    stops: tuple[Stop, ...]
    interpolation: str = 'LINEAR'
    color_mode: str = 'RGB'
    hue_mode: str = 'NEAR'

    def __post_init__(self):
        if not 2 <= len(self.stops) <= MAX_STOPS:
            raise ValueError(f'스톱은 2~{MAX_STOPS}개여야 합니다.')
        if len({s.key for s in self.stops}) != len(self.stops):
            raise ValueError('스톱 ID가 중복됩니다.')
        for stop in self.stops:
            if len(stop.color) != 4:
                raise ValueError('색상은 RGBA 4개 값이어야 합니다.')
            if any((not math.isfinite(x) or not 0 <= x <= 1 for x in (stop.position, *stop.color))):
                raise ValueError('스톱 위치와 RGBA는 0~1의 유한한 값이어야 합니다.')
        if self.interpolation not in INTERPOLATIONS or self.color_mode not in COLOR_MODES or self.hue_mode not in HUE_MODES:
            raise ValueError('지원하지 않는 보간 설정입니다.')
        object.__setattr__(self, 'stops', tuple(sorted(self.stops, key=lambda s: s.position)))

    @classmethod
    def default(cls):
        return cls((Stop.create(0, (0, 0, 0, 1)), Stop.create(1, (1, 1, 1, 1))))

    def change_stop(self, key, **changes):
        return replace(self, stops=tuple((replace(s, **changes) if s.key == key else s for s in self.stops)))

    def add_stop(self, position):
        stop = Stop.create(clamp(position), self.evaluate(position))
        return (replace(self, stops=(*self.stops, stop)), stop.key)

    def remove_stop(self, key):
        return replace(self, stops=tuple((s for s in self.stops if s.key != key)))

    def _hue_mix(self, left, right, t):
        convert = colorsys.rgb_to_hsv if self.color_mode == 'HSV' else colorsys.rgb_to_hls
        restore = colorsys.hsv_to_rgb if self.color_mode == 'HSV' else colorsys.hls_to_rgb
        a, b = (list(convert(*left[:3])), list(convert(*right[:3])))
        saturation = 1 if self.color_mode == 'HSV' else 2
        if a[saturation] < 1e-08:
            a[0] = b[0]
        if b[saturation] < 1e-08:
            b[0] = a[0]
        delta = b[0] - a[0]
        if self.hue_mode == 'NEAR':
            if delta > 0.5:
                delta -= 1
            elif delta < -0.5:
                delta += 1
        elif self.hue_mode == 'FAR':
            if 0 <= delta < 0.5:
                delta -= 1
            elif -0.5 < delta < 0:
                delta += 1
        elif self.hue_mode == 'CW':
            if delta > 0:
                delta -= 1
        elif self.hue_mode == 'CCW':
            if delta < 0:
                delta += 1
        values = ((a[0] + t * delta) % 1, a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2]))
        return (*restore(*values), left[3] + t * (right[3] - left[3]))

    def evaluate(self, value):
        if not math.isfinite(value):
            raise ValueError('Ramp 입력값이 유한하지 않습니다.')
        x = clamp(value)
        index = bisect_right([s.position for s in self.stops], x) - 1
        cubic = self.color_mode == 'RGB' and self.interpolation in ('CARDINAL', 'B_SPLINE')
        if index < 0:
            if not cubic:
                return self.stops[0].color
            left = right = self.stops[0]
            previous, following = (left.color, self.stops[1].color)
            t = x / right.position
        elif index >= len(self.stops) - 1:
            if not cubic:
                return self.stops[-1].color
            left = right = self.stops[-1]
            previous, following = (self.stops[-2].color, right.color)
            t = (x - left.position) / (1 - left.position) if left.position < 1 else 0
        else:
            left, right = self.stops[index:index + 2]
            t = (x - left.position) / (right.position - left.position)
            previous = self.stops[max(0, index - 1)].color
            following = self.stops[min(len(self.stops) - 1, index + 2)].color
        if self.color_mode != 'RGB':
            return self._hue_mix(left.color, right.color, t)
        if self.interpolation == 'CONSTANT':
            return left.color
        if self.interpolation == 'EASE':
            t = t * t * (3 - 2 * t)
        if self.interpolation in ('LINEAR', 'EASE'):
            return tuple((a + (b - a) * t for a, b in zip(left.color, right.color)))
        t2, t3 = (t * t, t * t * t)
        if self.interpolation == 'B_SPLINE':
            weights = ((1 - 3 * t + 3 * t2 - t3) / 6, (4 - 6 * t2 + 3 * t3) / 6, (1 + 3 * t + 3 * t2 - 3 * t3) / 6, t3 / 6)
            return tuple((clamp(sum((w * c for w, c in zip(weights, channel)))) for channel in zip(previous, left.color, right.color, following)))
        h00, h10, h01, h11 = (2 * t3 - 3 * t2 + 1, t3 - 2 * t2 + t, -2 * t3 + 3 * t2, t3 - t2)
        return tuple((clamp(h00 * a + h10 * 0.71 * (b - p) + h01 * b + h11 * 0.71 * (n - a)) for p, a, b, n in zip(previous, left.color, right.color, following)))

    def row_bytes(self, width):
        if width < 2:
            raise ValueError('가로 해상도는 2 이상이어야 합니다.')
        return bytes((round(clamp(c) * 255) for i in range(width) for c in self.evaluate(i / (width - 1))))

    def to_dict(self):
        return dict(version=1, interpolation=self.interpolation, color_mode=self.color_mode, hue_mode=self.hue_mode, stops=[dict(key=s.key, position=s.position, color=list(s.color)) for s in self.stops])

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError('그라디언트 데이터는 JSON 객체여야 합니다.')
        if type(data.get('version')) is not int or data['version'] != 1:
            raise ValueError('지원하지 않는 그라디언트 버전입니다. version은 1이어야 합니다.')
        try:
            raw_stops = data['stops']
            settings = {name: data[name] for name in ('interpolation', 'color_mode', 'hue_mode')}
            if not isinstance(raw_stops, (list, tuple)) or not 2 <= len(raw_stops) <= MAX_STOPS:
                raise ValueError(f'스톱 목록은 2~{MAX_STOPS}개여야 합니다.')
            stops = []
            for index, item in enumerate(raw_stops):
                if not isinstance(item, dict):
                    raise ValueError(f'스톱 {index + 1}의 형식이 올바르지 않습니다.')
                key, position, color = (item['key'], item['position'], item['color'])
                if not isinstance(key, str) or not key.strip():
                    raise ValueError(f'스톱 {index + 1}의 ID는 빈 문자열이 아니어야 합니다.')
                if not isinstance(color, (list, tuple)) or len(color) != 4:
                    raise ValueError(f'스톱 {index + 1}의 색상은 RGBA 4개 값이어야 합니다.')
                for value in (position, *color):
                    if type(value) not in (int, float) or not 0 <= value <= 1:
                        raise ValueError(f'스톱 {index + 1}의 위치와 RGBA는 0~1의 유한한 숫자여야 합니다.')
                stops.append(Stop(key, float(position), tuple((float(value) for value in color))))
        except KeyError as exc:
            raise ValueError(f'필수 그라디언트 필드가 없습니다: {exc.args[0]}') from exc
        return cls(tuple(stops), **settings)

def _chunk(kind, payload):
    return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))

def write_png(path: Path, gradient: Gradient):
    row = gradient.row_bytes(WIDTH)
    info = json.dumps(gradient.to_dict(), ensure_ascii=True, separators=(',', ':')).encode('ascii')
    data = b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 6, 0, 0, 0)) + _chunk(b'tEXt', b'FoundryGradient\x00' + info) + _chunk(b'IDAT', zlib.compress((b'\x00' + row) * HEIGHT)) + _chunk(b'IEND', b'')
    path.write_bytes(data)
    return path
