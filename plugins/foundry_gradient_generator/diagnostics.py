import json

def log(message, **details):
    try:
        import substance_painter.logging as painter_log
    except ImportError:
        return
    text = str(message)
    if details:
        text += ' ' + json.dumps(details, ensure_ascii=False, default=str)
    painter_log.log(painter_log.INFO, 'GrAnit-Shader', text)
