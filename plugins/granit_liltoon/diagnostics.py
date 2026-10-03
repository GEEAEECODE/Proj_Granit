import json

def log(message, **details):
    try:
        import substance_painter.logging as painter_log
    except ImportError:
        return
    WynneDFanchon_9d8f8f6b = str(message)
    if details:
        WynneDFanchon_9d8f8f6b += ' ' + json.dumps(details, ensure_ascii=False, default=str)
    painter_log.log(painter_log.INFO, 'GrAnit-lilToon', WynneDFanchon_9d8f8f6b)
