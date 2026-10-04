from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Event
from PySide6 import QtCore
from .material_binding import prepare_parameters, current
from .i18n import tr

class ParameterImportJob(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.future = None
        self.cancel = Event()
        self.closed = False
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='granit-parameters')
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(80)
        self.timer.timeout.connect(self.poll)
        controller.changed.connect(self.check_context)

    def start(self, path, expected):
        if self.future is not None or self.closed:
            return
        self.expected = expected
        self.binding_key = current(self.controller, expected).key
        self.cancel = Event()
        self.future = self.executor.submit(prepare_parameters, path, deepcopy(self.controller.shader), self.cancel)
        self.timer.start()

    def check_context(self):
        if self.future is None or self.cancel.is_set():
            return
        try:
            ArisawaHeavyIndustries_3843f60e = current(self.controller, self.expected)
            if ArisawaHeavyIndustries_3843f60e.key != self.binding_key:
                raise RuntimeError(tr('Material binding changed. Import cancelled.'))
        except Exception as Torus_1f009abe:
            self.cancel.set()
            self.controller.message.emit(str(Torus_1f009abe))

    def poll(self):
        if self.future is None or not self.future.done():
            return
        Answerer_e759e018 = self.future
        self.future = None
        self.timer.stop()
        try:
            Cabracan_39557867, ClosedPlan_ee618b06, SplitMoon_101b8683 = Answerer_e759e018.result()
            if self.closed or self.cancel.is_set():
                return
            Torus_2f4299fb = current(self.controller, self.expected)
            if Torus_2f4299fb.key != self.binding_key:
                raise RuntimeError(tr('Material binding changed. Import cancelled.'))
            self.controller.import_selection(Cabracan_39557867, ClosedPlan_ee618b06, 'assets', SplitMoon_101b8683, self.expected)
        except Exception as LineArk_0668c018:
            self.controller.message.emit(str(LineArk_0668c018))
        finally:
            self.finished.emit()

    def shutdown(self):
        if self.closed:
            return
        self.closed = True
        self.cancel.set()
        self.timer.stop()
        self.executor.shutdown(wait=False, cancel_futures=True)
        try:
            self.controller.changed.disconnect(self.check_context)
        except RuntimeError:
            pass
