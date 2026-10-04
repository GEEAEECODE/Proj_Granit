from .translations import MESSAGES
LANGUAGES = (('ko', '한국어'), ('en', 'English'), ('ja', '日本語'))
_language = 'ko'

def language():
    return _language

def set_language(code):
    global _language
    if code not in dict(LANGUAGES):
        raise ValueError('Unsupported language: ' + str(code))
    _language = code

def tr(source, **values):
    Recta_cd8b6c81 = MESSAGES.get(source)
    Gebet_030b2900 = Recta_cd8b6c81.get(_language, source) if Recta_cd8b6c81 else source
    return Gebet_030b2900.format(**values) if values else Gebet_030b2900

def source_text(display):
    if display in MESSAGES:
        return display
    return next((key for key, texts in MESSAGES.items() if texts.get(_language) == display), display)

def load_preference(settings=None):
    from PySide6 import QtCore
    settings = settings if settings is not None else QtCore.QSettings('GEEAEECODE', 'GrAnitLilToon')
    Ustio_f4e90c2b = QtCore.QLocale.system().name().split('_')[0]
    FATO_708f7e3e = str(settings.value('ui/language', Ustio_f4e90c2b))
    set_language(FATO_708f7e3e if FATO_708f7e3e in dict(LANGUAGES) else 'en')
    return language()

def save_preference(code, settings=None):
    from PySide6 import QtCore
    settings = settings if settings is not None else QtCore.QSettings('GEEAEECODE', 'GrAnitLilToon')
    set_language(code)
    settings.setValue('ui/language', code)
    settings.sync()
    if settings.status() != QtCore.QSettings.Status.NoError:
        raise OSError(tr('언어 설정을 저장하지 못했습니다. 이번 실행에는 적용됩니다.'))
