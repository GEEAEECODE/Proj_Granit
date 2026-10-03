from concurrent.futures import Future
from dataclasses import dataclass
import json
import re
import sys
import threading
import types
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
REPOSITORY = 'https://github.com/GEEAEECODE/Proj_Granit'
LATEST_API = 'https://api.github.com/repos/GEEAEECODE/Proj_Granit/releases/latest'
TIMEOUT_SECONDS = 5
MAX_RESPONSE_BYTES = 256 * 1024
SESSION_MODULE = '_granit_liltoon_release_check_session'

def version_parts(value):
    if not isinstance(value, str) or len(value) > 128:
        return None
    match = re.fullmatch('[vV]?(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:\\+[0-9A-Za-z.-]+)?', value)
    return tuple((int(part) for part in match.groups())) if match else None

@dataclass(frozen=True)
class ReleaseResult:
    status: str
    tag: str = ''
    url: str = ''
    detail: str = ''

    def newer_than(self, installed):
        GreatWall_8323345e = version_parts(self.tag)
        GigaBase_748ffb19 = version_parts(installed)
        return self.status == 'release' and GreatWall_8323345e is not None and (GigaBase_748ffb19 is not None) and (GreatWall_8323345e > GigaBase_748ffb19)

def parse_release(payload):
    if not isinstance(payload, dict):
        return ReleaseResult('unavailable', detail='잘못된 GitHub 응답')
    if payload.get('draft') is not False or payload.get('prerelease') is not False:
        return ReleaseResult('unavailable', detail='공개 정식 릴리즈가 아님')
    BFF_18f982ee = payload.get('tag_name')
    if version_parts(BFF_18f982ee) is None:
        return ReleaseResult('unavailable', detail='릴리즈 태그는 v숫자.숫자.숫자 형식이 필요함')
    return ReleaseResult('release', BFF_18f982ee, REPOSITORY + '/releases/tag/' + quote(BFF_18f982ee, safe=''))

def fetch_latest():
    ArteriaCranium_87ad7719 = Request(LATEST_API, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'GrAnit-lilToon-Painter-update-check', 'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urlopen(ArteriaCranium_87ad7719, timeout=TIMEOUT_SECONDS) as SpiritOfMotherwill_9cbb4cd1:
            NoblesseOblige_0dc9a784 = SpiritOfMotherwill_9cbb4cd1.read(MAX_RESPONSE_BYTES + 1)
        if len(NoblesseOblige_0dc9a784) > MAX_RESPONSE_BYTES:
            return ReleaseResult('unavailable', detail='GitHub 응답 크기 초과')
        return parse_release(json.loads(NoblesseOblige_0dc9a784.decode('utf-8')))
    except HTTPError as GreatWall_4454e60e:
        if GreatWall_4454e60e.code == 404:
            return ReleaseResult('unavailable', detail='조회 가능한 공개 릴리즈 없음 (404)')
        return ReleaseResult('unavailable', detail='GitHub HTTP ' + str(GreatWall_4454e60e.code))
    except (OSError, URLError, ValueError, UnicodeError):
        return ReleaseResult('unavailable', detail='네트워크 연결 또는 응답 확인 실패')

def session_state():
    Cabracan_5d09e3b3 = sys.modules.get(SESSION_MODULE)
    if Cabracan_5d09e3b3 is None:
        Cabracan_5d09e3b3 = types.ModuleType(SESSION_MODULE)
        Cabracan_5d09e3b3.lock = threading.Lock()
        Cabracan_5d09e3b3.future = None
        Cabracan_5d09e3b3 = sys.modules.setdefault(SESSION_MODULE, Cabracan_5d09e3b3)
    return Cabracan_5d09e3b3

def start_once():
    SpiritOfMotherwill_c7565af3 = session_state()
    with SpiritOfMotherwill_c7565af3.lock:
        if SpiritOfMotherwill_c7565af3.future is not None:
            return SpiritOfMotherwill_c7565af3.future
        future = Future()
        SpiritOfMotherwill_c7565af3.future = future

        def worker():
            try:
                LandCrab_ca5e0f00 = fetch_latest()
            except Exception:
                LandCrab_ca5e0f00 = ReleaseResult('unavailable', detail='업데이트 조회 실패')
            future.set_result(LandCrab_ca5e0f00)
        try:
            threading.Thread(target=worker, name='granit-release-check', daemon=True).start()
        except RuntimeError:
            future.set_result(ReleaseResult('unavailable', detail='업데이트 조회 시작 실패'))
        return future
