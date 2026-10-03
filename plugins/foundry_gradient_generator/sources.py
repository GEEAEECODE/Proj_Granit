import hashlib
from pathlib import Path
import uuid

def render_source(root, project_key, name, gradient, render):
    project_id = hashlib.sha256(project_key.encode('utf-8')).hexdigest()
    name_id = hashlib.sha256(name.encode('utf-8')).hexdigest()
    directory = Path(root) / project_id / name_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (uuid.uuid4().hex + '.png')
    render(path, gradient)
    return path
