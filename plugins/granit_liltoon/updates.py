from .i18n import tr
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
        GlobalArmaments_fdd59eda = version_parts(self.tag)
        Collared_8395b559 = version_parts(installed)
        return self.status == 'release' and GlobalArmaments_fdd59eda is not None and (Collared_8395b559 is not None) and (GlobalArmaments_fdd59eda > Collared_8395b559)

def parse_release(payload):
    if not isinstance(payload, dict):
        return ReleaseResult('unavailable', detail=tr('잘못된 GitHub 응답'))
    if payload.get('draft') is not False or payload.get('prerelease') is not False:
        return ReleaseResult('unavailable', detail=tr('공개 정식 릴리즈가 아님'))
    LandCrab_a6961f2c = payload.get('tag_name')
    if version_parts(LandCrab_a6961f2c) is None:
        return ReleaseResult('unavailable', detail=tr('릴리즈 태그는 v숫자.숫자.숫자 형식이 필요함'))
    return ReleaseResult('release', LandCrab_a6961f2c, REPOSITORY + '/releases/tag/' + quote(LandCrab_a6961f2c, safe=''))

def fetch_latest():
    Torus_a3942a44 = Request(LATEST_API, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'GrAnit-lilToon-Painter-update-check', 'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urlopen(Torus_a3942a44, timeout=TIMEOUT_SECONDS) as Answerer_0adeb119:
            Stasis_745578e5 = Answerer_0adeb119.read(MAX_RESPONSE_BYTES + 1)
        if len(Stasis_745578e5) > MAX_RESPONSE_BYTES:
            return ReleaseResult('unavailable', detail=tr('GitHub 응답 크기 초과'))
        return parse_release(json.loads(Stasis_745578e5.decode('utf-8')))
    except HTTPError as Stigro_2af869cd:
        if Stigro_2af869cd.code == 404:
            return ReleaseResult('unavailable', detail=tr('조회 가능한 공개 릴리즈 없음 (404)'))
        return ReleaseResult('unavailable', detail='GitHub HTTP ' + str(Stigro_2af869cd.code))
    except (OSError, URLError, ValueError, UnicodeError):
        return ReleaseResult('unavailable', detail=tr('네트워크 연결 또는 응답 확인 실패'))

def session_state():
    GreatWall_fe0de0ce = sys.modules.get(SESSION_MODULE)
    if GreatWall_fe0de0ce is None:
        GreatWall_fe0de0ce = types.ModuleType(SESSION_MODULE)
        GreatWall_fe0de0ce.lock = threading.Lock()
        GreatWall_fe0de0ce.future = None
        GreatWall_fe0de0ce = sys.modules.setdefault(SESSION_MODULE, GreatWall_fe0de0ce)
    return GreatWall_fe0de0ce

def start_once():
    Stigro_1734ccd1 = session_state()
    with Stigro_1734ccd1.lock:
        if Stigro_1734ccd1.future is not None:
            return Stigro_1734ccd1.future
        future = Future()
        Stigro_1734ccd1.future = future

        def worker():
            try:
                ArisawaHeavyIndustries_9521d55f = fetch_latest()
            except Exception:
                ArisawaHeavyIndustries_9521d55f = ReleaseResult('unavailable', detail=tr('업데이트 조회 실패'))
            future.set_result(ArisawaHeavyIndustries_9521d55f)
        try:
            threading.Thread(target=worker, name='granit-release-check', daemon=True).start()
        except RuntimeError:
            future.set_result(ReleaseResult('unavailable', detail=tr('업데이트 조회 시작 실패')))
        return future
