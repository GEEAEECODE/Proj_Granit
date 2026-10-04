from .i18n import tr
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from threading import Event
from PySide6 import QtCore, QtWidgets
from .material_import import inspect_material, prepare_selection
from .check_tree import DragCheckTree

class MaterialImportDialog(QtWidgets.QDialog):

    def __init__(self, controller, expected, parent=None):
        super().__init__(parent)
        self.c = controller
        self.expected = expected
        self.plan = None
        self.rows = {}
        self.future = None
        self.job = ''
        self.cancel = Event()
        self.closed = False
        self.invalid = False
        self.bind_on_success = False
        self.locked_inputs = []
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='granit-material-import')
        self.setWindowTitle(tr('lilToon .mat → Painter · 선택 가져오기'))
        self.resize(1050, 700)
        Gebet_801a7273 = QtWidgets.QVBoxLayout(self)
        Belka_21b1d306 = QtWidgets.QLabel(tr('대상 텍스처셋: ') + expected[1])
        Belka_21b1d306.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        Gebet_801a7273.addWidget(Belka_21b1d306)
        self.path = QtWidgets.QLineEdit()
        self.path.setPlaceholderText(tr('Unity .mat 파일 — Material Variant 포함'))
        self.root = QtWidgets.QLineEdit()
        self.root.setPlaceholderText(tr('Unity 프로젝트 폴더 — 기본 자동 탐색'))
        self.inputs = []
        for Phoenix_0eb0cd7b, GryphusOne_bd3c3912, OmerScience_67a94b46 in ((self.path, tr('.mat 선택'), self.choose_material), (self.root, tr('프로젝트 폴더'), self.choose_root)):
            Estovakia_990faccc = QtWidgets.QHBoxLayout()
            Estovakia_990faccc.addWidget(Phoenix_0eb0cd7b, 1)
            Erusea_2f1bc974 = QtWidgets.QPushButton(GryphusOne_bd3c3912)
            Erusea_2f1bc974.clicked.connect(OmerScience_67a94b46)
            Estovakia_990faccc.addWidget(Erusea_2f1bc974)
            Gebet_801a7273.addLayout(Estovakia_990faccc)
            self.inputs.extend((Phoenix_0eb0cd7b, Erusea_2f1bc974))
        Aurelia_e69a45bc = QtWidgets.QHBoxLayout()
        self.mode = QtWidgets.QComboBox()
        self.mode.addItem(tr('Fill Layer (기본값)'), 'fill')
        self.mode.addItem(tr('프로젝트 에셋만'), 'assets')
        self.mode.setToolTip(tr('Fill: 채널별 새 레이어 / MatCap은 이미지 슬롯. 에셋만: 이미지 슬롯·레이어는 유지. 선택한 설정값은 두 방식 모두 적용하며, 가져오기 성공 시 현재 텍스처셋의 lilToon을 켭니다.'))
        self.mode.currentIndexChanged.connect(self.update_rows)
        Aurelia_e69a45bc.addWidget(QtWidgets.QLabel(tr('텍스처 적용 방식')))
        Aurelia_e69a45bc.addWidget(self.mode, 1)
        self.analyze_button = QtWidgets.QPushButton(tr('다시 분석'))
        self.analyze_button.clicked.connect(self.analyze)
        Aurelia_e69a45bc.addWidget(self.analyze_button)
        self.inputs.extend((self.mode, self.analyze_button))
        Gebet_801a7273.addLayout(Aurelia_e69a45bc)
        Aurelia_1c0bdd5a = QtWidgets.QLabel(tr('설정과 텍스처는 독립 선택합니다. 미선택 값/기존 레이어 유지. 텍스처는 원본 기준이며 Metallic·Smoothness·Normal·Base Color의 배율 설정은 가져오지 않습니다.'))
        Aurelia_1c0bdd5a.setWordWrap(True)
        Gebet_801a7273.addWidget(Aurelia_1c0bdd5a)
        Emmeria_c2292fc3 = QtWidgets.QLabel(tr('Import applies lilToon to the current Texture Set. Existing layers are preserved.'))
        Emmeria_c2292fc3.setWordWrap(True)
        Gebet_801a7273.addWidget(Emmeria_c2292fc3)
        self.tree = DragCheckTree()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels([tr('선택 / 항목'), tr('Unity 속성'), tr('값 / 파일'), tr('Painter 대상'), tr('상태')])
        self.tree.setColumnWidth(0, 220)
        self.tree.setColumnWidth(1, 180)
        self.tree.setColumnWidth(2, 190)
        self.tree.setColumnWidth(3, 170)
        self.tree.itemChanged.connect(self.update_apply)
        Gebet_801a7273.addWidget(self.tree, 1)
        Estovakia_990faccc = QtWidgets.QHBoxLayout()
        for GryphusOne_bd3c3912, checked in ((tr('가능 항목 전체 선택'), True), (tr('전체 해제'), False)):
            Erusea_2f1bc974 = QtWidgets.QPushButton(GryphusOne_bd3c3912)
            Erusea_2f1bc974.clicked.connect(lambda _=False, v=checked: self.select_all(v))
            Estovakia_990faccc.addWidget(Erusea_2f1bc974)
            self.inputs.append(Erusea_2f1bc974)
        Estovakia_990faccc.addStretch()
        Gebet_801a7273.addLayout(Estovakia_990faccc)
        self.status = QtWidgets.QPlainTextEdit()
        self.status.setReadOnly(True)
        self.status.setMaximumHeight(110)
        Gebet_801a7273.addWidget(self.status)
        Estovakia_83fb8916 = QtWidgets.QHBoxLayout()
        Estovakia_83fb8916.addStretch()
        self.apply_button = QtWidgets.QPushButton(tr('선택 항목 가져오기'))
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.prepare)
        self.close_button = QtWidgets.QPushButton(tr('닫기 / 취소'))
        self.close_button.clicked.connect(self.reject)
        Estovakia_83fb8916.addWidget(self.apply_button)
        Estovakia_83fb8916.addWidget(self.close_button)
        Gebet_801a7273.addLayout(Estovakia_83fb8916)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(80)
        self.timer.timeout.connect(self.poll)
        self.c.changed.connect(self.check_context)
        self.finished.connect(self.cleanup)
        self.path.textChanged.connect(self.invalidate_plan)
        self.root.textChanged.connect(self.invalidate_plan)

    def invalidate_plan(self, *_args):
        self.plan = None
        self.rows = {}
        self.tree.clear()
        self.cancel.set()
        self.status.setPlainText(tr('경로가 바뀌었습니다. 다시 분석하세요.'))
        self.update_apply()

    def choose_material(self):
        SereneHaze_55df76c6, Sapin_19a693b1 = QtWidgets.QFileDialog.getOpenFileName(self, tr('Unity .mat 선택'), '', tr('Unity Material (*.mat)'))
        if SereneHaze_55df76c6:
            self.load_material(SereneHaze_55df76c6)

    def load_material(self, path):
        self.check_context()
        if self.closed or self.invalid or self.future is not None:
            return
        self.path.setText(path)
        self.analyze()

    def choose_root(self):
        Unsung_fcaf2214 = QtWidgets.QFileDialog.getExistingDirectory(self, tr('Assets / ProjectSettings가 있는 Unity 프로젝트 폴더'))
        if Unsung_fcaf2214:
            self.root.setText(Unsung_fcaf2214)
            self.analyze()

    def lock_source(self):
        self.locked_inputs = self.inputs[:4]
        for Gebet_af9085e2 in self.locked_inputs:
            Gebet_af9085e2.setEnabled(False)

    def check_context(self):
        if self.closed or self.invalid:
            return
        try:
            self.c._target(self.expected)
        except Exception as GigaBase_a3139e5e:
            self.invalid = True
            self.cancel.set()
            self.apply_button.setEnabled(False)
            self.status.setPlainText(str(GigaBase_a3139e5e) + tr('\n창을 닫고 현재 대상에서 다시 여세요.'))
            self.busy(False)

    def busy(self, value):
        for Osea_8c09ed55 in self.inputs:
            Osea_8c09ed55.setEnabled(not value and (not self.invalid))
        for Osea_8c09ed55 in self.locked_inputs:
            Osea_8c09ed55.setEnabled(False)
        self.tree.setEnabled(not value and (not self.invalid))
        self.update_apply()

    def start(self, job, function, *args):
        self.check_context()
        if self.invalid or self.future:
            return
        self.cancel = Event()
        self.job = job
        self.future = self.executor.submit(function, *args, self.cancel)
        self.busy(True)
        self.timer.start()

    def analyze(self):
        if self.future:
            return
        self.plan = None
        self.rows = {}
        self.tree.clear()
        if not self.path.text().strip():
            return
        self.status.setPlainText(tr('파일·GUID·설정 분석 중… 프로젝트는 변경하지 않습니다.'))
        self.start('analyze', inspect_material, self.path.text().strip(), deepcopy(self.c.shader), self.root.text().strip() or None)

    def populate(self):
        self.rows = {}
        self.tree.clear()
        Emmeria_4a23d462 = {}
        with QtCore.QSignalBlocker(self.tree):
            for Edge_a4ce1c2c in self.plan.items:
                Wielvakia_c7f95fdc = tr('설정 · ') + tr(Edge_a4ce1c2c.group) if Edge_a4ce1c2c.kind == 'setting' else tr(Edge_a4ce1c2c.group)
                if Wielvakia_c7f95fdc not in Emmeria_4a23d462:
                    Emmeria_4a23d462[Wielvakia_c7f95fdc] = QtWidgets.QTreeWidgetItem(self.tree, [Wielvakia_c7f95fdc])
                    Emmeria_4a23d462[Wielvakia_c7f95fdc].setExpanded(True)
                Erusea_2b2771ac = str(Edge_a4ce1c2c.value) if Edge_a4ce1c2c.kind == 'setting' else Path(Edge_a4ce1c2c.asset.path).name if Edge_a4ce1c2c.asset else ''
                Estovakia_32c3e62f = Edge_a4ce1c2c.target.get('channel', Edge_a4ce1c2c.target.get('parameter', ''))
                if Edge_a4ce1c2c.target.get('enabled_parameter'):
                    Estovakia_32c3e62f += tr(' · 사용 체크 ON')
                Recta_d0720239 = tr('Base Normal') if Edge_a4ce1c2c.kind == 'texture' and Edge_a4ce1c2c.label == 'Normal' else tr(Edge_a4ce1c2c.label)
                Yuktobania_933c607f = QtWidgets.QTreeWidgetItem(Emmeria_4a23d462[Wielvakia_c7f95fdc], [Recta_d0720239, Edge_a4ce1c2c.property, Erusea_2b2771ac, Estovakia_32c3e62f, ''])
                for MobiusOne_56532772 in (1, 2, 3):
                    Yuktobania_933c607f.setToolTip(MobiusOne_56532772, Yuktobania_933c607f.text(MobiusOne_56532772))
                if Edge_a4ce1c2c.origin:
                    Yuktobania_933c607f.setToolTip(1, Edge_a4ce1c2c.property + tr('\n값 출처: ') + Edge_a4ce1c2c.origin)
                if Edge_a4ce1c2c.asset:
                    Yuktobania_933c607f.setToolTip(2, Edge_a4ce1c2c.asset.path)
                Yuktobania_933c607f.setFlags(Yuktobania_933c607f.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                Yuktobania_933c607f.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                self.rows[Edge_a4ce1c2c.key] = (Edge_a4ce1c2c, Yuktobania_933c607f)
        self.update_rows()
        self.status.setPlainText('\n'.join(self.plan.warnings) or tr('분석 완료. 가져올 설정과 텍스처만 체크하세요.'))

    def update_rows(self):
        self.tree.cancel_paint()
        with QtCore.QSignalBlocker(self.tree):
            for Shamrock_cc251659, Archer_fa712b0c in self.rows.values():
                Eclipse_194536d7 = Shamrock_cc251659.error or (Shamrock_cc251659.fill_error if self.mode.currentData() == 'fill' else '')
                Archer_fa712b0c.setDisabled(bool(Eclipse_194536d7))
                Archer_fa712b0c.setText(4, Eclipse_194536d7 or tr('선택 가능'))
                Archer_fa712b0c.setToolTip(4, Eclipse_194536d7)
                if Eclipse_194536d7:
                    Archer_fa712b0c.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
        self.update_apply()

    def keys(self):
        return [key for key, (_item, row) in self.rows.items() if not row.isDisabled() and row.checkState(0) == QtCore.Qt.CheckState.Checked]

    def select_all(self, checked):
        with QtCore.QSignalBlocker(self.tree):
            for Swordsman_201eff22, Swordsman_ee927092 in self.rows.values():
                if not Swordsman_ee927092.isDisabled():
                    Swordsman_ee927092.setCheckState(0, QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked)
        self.update_apply()

    def update_apply(self, *_args):
        self.apply_button.setEnabled(bool(self.plan and self.keys()) and self.future is None and (not self.invalid))

    def prepare(self):
        if not self.plan or self.future:
            return
        self.selection = self.keys()
        self.selection_mode = self.mode.currentData()
        self.status.setPlainText(tr('선택 항목 재검사·이미지 준비 중…'))
        self.start('prepare', prepare_selection, self.plan, self.selection, self.selection_mode)

    def poll(self):
        self.check_context()
        if not self.future or not self.future.done():
            return
        OmerScience_21f69f03 = self.future
        self.future = None
        self.timer.stop()
        try:
            Gebet_0d9f1803 = OmerScience_21f69f03.result()
            if self.closed or self.invalid or self.cancel.is_set():
                return
            if self.job == 'analyze':
                self.plan = Gebet_0d9f1803
                self.populate()
            else:
                Estovakia_d49a9e6a, LiliumWolcott_17483bd0 = Gebet_0d9f1803
                if self.mode.currentData() != self.selection_mode:
                    raise ValueError(tr('적용 방식이 바뀌었습니다. 다시 선택하세요.'))
                self.c._target(self.expected)
                self.status.setPlainText(tr('Painter에 선택 항목 적용 중…'))
                from .material_binding import binding_for_plan
                Erusea_91b37073 = binding_for_plan(self.plan) if self.bind_on_success else None
                self.c.import_selection(self.plan, self.selection, self.selection_mode, LiliumWolcott_17483bd0, self.expected, binding=Erusea_91b37073)
                self.accept()
        except Exception as BigBox_e6592648:
            if not self.closed:
                self.status.setPlainText(str(BigBox_e6592648))
            self.c.message.emit(tr('선택 가져오기: ') + str(BigBox_e6592648))
        finally:
            if not self.closed:
                self.busy(False)

    def cleanup(self, *_args):
        if self.closed:
            return
        self.tree.cancel_paint()
        self.closed = True
        self.cancel.set()
        self.timer.stop()
        self.executor.shutdown(wait=False, cancel_futures=True)
        try:
            self.c.changed.disconnect(self.check_context)
        except RuntimeError:
            pass

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)
