from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PySide6 import QtCore
from .gradient import validate_name, write_png
from .sources import render_source

class GenerationJob(QtCore.QObject):
    busyChanged = QtCore.Signal(bool)
    finished = QtCore.Signal(object)
    failed = QtCore.Signal(str)
    discarded = QtCore.Signal()

    def __init__(self, assets, parent=None, render=write_png, source_root=None):
        super().__init__(parent)
        self.assets, self.render = (assets, render)
        if source_root is None:
            location = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.GenericDataLocation)
            if not location:
                raise RuntimeError('PNG 원본을 보관할 사용자 데이터 폴더를 찾을 수 없습니다.')
            source_root = Path(location) / 'FoundryRamp' / 'GradientSources'
        self._source_root = Path(source_root)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='FoundryGradient')
        self._future = None
        self._closed = False
        self._epoch = 0
        self._active_epoch = 0
        self.accept_result = lambda: True
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(25)
        self._timer.timeout.connect(self._poll)

    @property
    def busy(self):
        return self._future is not None

    def invalidate_project(self, _event=None):
        self._epoch += 1

    def start(self, name, gradient):
        if self._closed or self.busy:
            return False
        name = validate_name(name)
        self.assets.ensure_ready()
        self._project = self.assets.project_key()
        self._name, self._active_epoch = (name, self._epoch)
        self._future = self._executor.submit(render_source, self._source_root, self._project, name, gradient, self.render)
        self.busyChanged.emit(True)
        self._timer.start()
        return True

    def _poll(self):
        if self._closed or not self._future or (not self._future.done()):
            return
        self._timer.stop()
        future = self._future
        result, error, discarded = (None, None, False)
        try:
            path = future.result()
            if self._active_epoch != self._epoch or self.assets.project_key() != self._project:
                raise RuntimeError('생성 중 프로젝트가 변경되어 에셋에 적용하지 않았습니다.')
            if self.accept_result():
                result = self.assets.import_gradient(self._name, path, self._project)
            else:
                discarded = True
        except Exception as exc:
            error = str(exc)
        finally:
            self._future = None
            self.busyChanged.emit(False)
        if error is not None:
            self.failed.emit(error)
        elif discarded:
            self.discarded.emit()
        else:
            self.finished.emit(result)

    def close(self):
        if self._closed:
            return
        self._closed = True
        self.invalidate_project()
        self._timer.stop()
        if self._future:
            self._future.cancel()
        self._executor.shutdown(wait=False, cancel_futures=True)
