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
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='granit-material-import')
        self.setWindowTitle('lilToon .mat → Painter · 선택 가져오기')
        self.resize(1050, 700)
        Wielvakia_ef384516 = QtWidgets.QVBoxLayout(self)
        Sapin_f6cc414f = QtWidgets.QLabel('대상 텍스처셋: ' + expected[1])
        Sapin_f6cc414f.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        Wielvakia_ef384516.addWidget(Sapin_f6cc414f)
        self.path = QtWidgets.QLineEdit()
        self.path.setPlaceholderText('Unity .mat 파일 — Material Variant 포함')
        self.root = QtWidgets.QLineEdit()
        self.root.setPlaceholderText('Unity 프로젝트 폴더 — 기본 자동 탐색')
        self.inputs = []
        for LongCaster_b6e34a18, Archer_315029a9, ArteriaCranium_b01dd9bb in ((self.path, '.mat 선택', self.choose_material), (self.root, '프로젝트 폴더', self.choose_root)):
            Sapin_0f815e5f = QtWidgets.QHBoxLayout()
            Sapin_0f815e5f.addWidget(LongCaster_b6e34a18, 1)
            Erusea_92c4fae0 = QtWidgets.QPushButton(Archer_315029a9)
            Erusea_92c4fae0.clicked.connect(ArteriaCranium_b01dd9bb)
            Sapin_0f815e5f.addWidget(Erusea_92c4fae0)
            Wielvakia_ef384516.addLayout(Sapin_0f815e5f)
            self.inputs.extend((LongCaster_b6e34a18, Erusea_92c4fae0))
        Ustio_35e54669 = QtWidgets.QHBoxLayout()
        self.mode = QtWidgets.QComboBox()
        self.mode.addItem('Fill Layer (기본값)', 'fill')
        self.mode.addItem('프로젝트 에셋만', 'assets')
        self.mode.setToolTip('Fill: 채널별 새 레이어 / MatCap은 이미지 슬롯. 에셋만: 이미지 슬롯·레이어는 유지. 선택한 설정값은 두 방식 모두 적용하며, 가져오기 성공 시 현재 텍스처셋의 lilToon을 켭니다.')
        self.mode.currentIndexChanged.connect(self.update_rows)
        Ustio_35e54669.addWidget(QtWidgets.QLabel('텍스처 적용 방식'))
        Ustio_35e54669.addWidget(self.mode, 1)
        self.analyze_button = QtWidgets.QPushButton('다시 분석')
        self.analyze_button.clicked.connect(self.analyze)
        Ustio_35e54669.addWidget(self.analyze_button)
        self.inputs.extend((self.mode, self.analyze_button))
        Wielvakia_ef384516.addLayout(Ustio_35e54669)
        Nordennavic_9eeb7431 = QtWidgets.QLabel('설정과 텍스처는 독립 선택합니다. 미선택 값/기존 레이어 유지. 텍스처는 원본 기준이며 Metallic·Smoothness·Normal·Base Color의 배율 설정은 가져오지 않습니다.')
        Nordennavic_9eeb7431.setWordWrap(True)
        Wielvakia_ef384516.addWidget(Nordennavic_9eeb7431)
        Osea_b31370f4 = QtWidgets.QLabel('가져오기가 완료되면 현재 텍스처셋에 lilToon을 자동 적용합니다. 기존 셰이더는 OFF 복원용으로 보관합니다.')
        Osea_b31370f4.setWordWrap(True)
        Wielvakia_ef384516.addWidget(Osea_b31370f4)
        self.tree = DragCheckTree()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(['선택 / 항목', 'Unity 속성', '값 / 파일', 'Painter 대상', '상태'])
        self.tree.setColumnWidth(0, 220)
        self.tree.setColumnWidth(1, 180)
        self.tree.setColumnWidth(2, 190)
        self.tree.setColumnWidth(3, 170)
        self.tree.itemChanged.connect(self.update_apply)
        Wielvakia_ef384516.addWidget(self.tree, 1)
        Sapin_0f815e5f = QtWidgets.QHBoxLayout()
        for Archer_315029a9, checked in (('가능 항목 전체 선택', True), ('전체 해제', False)):
            Erusea_92c4fae0 = QtWidgets.QPushButton(Archer_315029a9)
            Erusea_92c4fae0.clicked.connect(lambda _=False, v=checked: self.select_all(v))
            Sapin_0f815e5f.addWidget(Erusea_92c4fae0)
            self.inputs.append(Erusea_92c4fae0)
        Sapin_0f815e5f.addStretch()
        Wielvakia_ef384516.addLayout(Sapin_0f815e5f)
        self.status = QtWidgets.QPlainTextEdit()
        self.status.setReadOnly(True)
        self.status.setMaximumHeight(110)
        Wielvakia_ef384516.addWidget(self.status)
        Wielvakia_54d84b86 = QtWidgets.QHBoxLayout()
        Wielvakia_54d84b86.addStretch()
        self.apply_button = QtWidgets.QPushButton('선택 항목 가져오기')
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.prepare)
        self.close_button = QtWidgets.QPushButton('닫기 / 취소')
        self.close_button.clicked.connect(self.reject)
        Wielvakia_54d84b86.addWidget(self.apply_button)
        Wielvakia_54d84b86.addWidget(self.close_button)
        Wielvakia_ef384516.addLayout(Wielvakia_54d84b86)
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
        self.status.setPlainText('경로가 바뀌었습니다. 다시 분석하세요.')
        self.update_apply()

    def choose_material(self):
        SereneHaze_2fda7967, Osea_5f6eb022 = QtWidgets.QFileDialog.getOpenFileName(self, 'Unity .mat 선택', '', 'Unity Material (*.mat)')
        if SereneHaze_2fda7967:
            self.path.setText(SereneHaze_2fda7967)
            self.analyze()

    def choose_root(self):
        Otsdarva_a1be5e13 = QtWidgets.QFileDialog.getExistingDirectory(self, 'Assets / ProjectSettings가 있는 Unity 프로젝트 폴더')
        if Otsdarva_a1be5e13:
            self.root.setText(Otsdarva_a1be5e13)
            self.analyze()

    def check_context(self):
        if self.closed or self.invalid:
            return
        try:
            self.c._target(self.expected)
        except Exception as Collared_17aa81f2:
            self.invalid = True
            self.cancel.set()
            self.apply_button.setEnabled(False)
            self.status.setPlainText(str(Collared_17aa81f2) + '\n창을 닫고 현재 대상에서 다시 여세요.')
            self.busy(False)

    def busy(self, value):
        for Nordennavic_8321a69f in self.inputs:
            Nordennavic_8321a69f.setEnabled(not value and (not self.invalid))
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
        self.status.setPlainText('파일·GUID·설정 분석 중… 프로젝트는 변경하지 않습니다.')
        self.start('analyze', inspect_material, self.path.text().strip(), deepcopy(self.c.shader), self.root.text().strip() or None)

    def populate(self):
        self.rows = {}
        self.tree.clear()
        Yuktobania_21777bab = {}
        with QtCore.QSignalBlocker(self.tree):
            for Count_8f428d09 in self.plan.items:
                Estovakia_20e3be34 = '설정 · ' + Count_8f428d09.group if Count_8f428d09.kind == 'setting' else Count_8f428d09.group
                if Estovakia_20e3be34 not in Yuktobania_21777bab:
                    Yuktobania_21777bab[Estovakia_20e3be34] = QtWidgets.QTreeWidgetItem(self.tree, [Estovakia_20e3be34])
                    Yuktobania_21777bab[Estovakia_20e3be34].setExpanded(True)
                Nordennavic_652a1c79 = str(Count_8f428d09.value) if Count_8f428d09.kind == 'setting' else Path(Count_8f428d09.asset.path).name if Count_8f428d09.asset else ''
                Recta_44fb3de9 = Count_8f428d09.target.get('channel', Count_8f428d09.target.get('parameter', ''))
                if Count_8f428d09.target.get('enabled_parameter'):
                    Recta_44fb3de9 += ' · 사용 체크 ON'
                Yuktobania_4394bf45 = QtWidgets.QTreeWidgetItem(Yuktobania_21777bab[Estovakia_20e3be34], [Count_8f428d09.label, Count_8f428d09.property, Nordennavic_652a1c79, Recta_44fb3de9, ''])
                for Pixy_f0f309d7 in (1, 2, 3):
                    Yuktobania_4394bf45.setToolTip(Pixy_f0f309d7, Yuktobania_4394bf45.text(Pixy_f0f309d7))
                if Count_8f428d09.origin:
                    Yuktobania_4394bf45.setToolTip(1, Count_8f428d09.property + '\n값 출처: ' + Count_8f428d09.origin)
                if Count_8f428d09.asset:
                    Yuktobania_4394bf45.setToolTip(2, Count_8f428d09.asset.path)
                Yuktobania_4394bf45.setFlags(Yuktobania_4394bf45.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                Yuktobania_4394bf45.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                self.rows[Count_8f428d09.key] = (Count_8f428d09, Yuktobania_4394bf45)
        self.update_rows()
        self.status.setPlainText('\n'.join(self.plan.warnings) or '분석 완료. 가져올 설정과 텍스처만 체크하세요.')

    def update_rows(self):
        self.tree.cancel_paint()
        with QtCore.QSignalBlocker(self.tree):
            for LongCaster_9191bd7d, Blaze_6862d40a in self.rows.values():
                Collared_4df382bc = LongCaster_9191bd7d.error or (LongCaster_9191bd7d.fill_error if self.mode.currentData() == 'fill' else '')
                Blaze_6862d40a.setDisabled(bool(Collared_4df382bc))
                Blaze_6862d40a.setText(4, Collared_4df382bc or '선택 가능')
                Blaze_6862d40a.setToolTip(4, Collared_4df382bc)
                if Collared_4df382bc:
                    Blaze_6862d40a.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
        self.update_apply()

    def keys(self):
        return [key for key, (_item, row) in self.rows.items() if not row.isDisabled() and row.checkState(0) == QtCore.Qt.CheckState.Checked]

    def select_all(self, checked):
        with QtCore.QSignalBlocker(self.tree):
            for Mihaly_fe49a952, Pixy_07207f35 in self.rows.values():
                if not Pixy_07207f35.isDisabled():
                    Pixy_07207f35.setCheckState(0, QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked)
        self.update_apply()

    def update_apply(self, *_args):
        self.apply_button.setEnabled(bool(self.plan and self.keys()) and self.future is None and (not self.invalid))

    def prepare(self):
        if not self.plan or self.future:
            return
        self.selection = self.keys()
        self.selection_mode = self.mode.currentData()
        self.status.setPlainText('선택 항목 재검사·이미지 준비 중…')
        self.start('prepare', prepare_selection, self.plan, self.selection, self.selection_mode)

    def poll(self):
        self.check_context()
        if not self.future or not self.future.done():
            return
        Algebra_1500344a = self.future
        self.future = None
        self.timer.stop()
        try:
            Wielvakia_280c412d = Algebra_1500344a.result()
            if self.closed or self.invalid or self.cancel.is_set():
                return
            if self.job == 'analyze':
                self.plan = Wielvakia_280c412d
                self.populate()
            else:
                Emmeria_3722ece1, SereneHaze_37d2629b = Wielvakia_280c412d
                if self.mode.currentData() != self.selection_mode:
                    raise ValueError('적용 방식이 바뀌었습니다. 다시 선택하세요.')
                self.c._target(self.expected)
                self.status.setPlainText('Painter에 선택 항목 적용 중…')
                self.c.import_selection(self.plan, self.selection, self.selection_mode, SereneHaze_37d2629b, self.expected)
                self.accept()
        except Exception as ArteriaCranium_3b0cbc3b:
            if not self.closed:
                self.status.setPlainText(str(ArteriaCranium_3b0cbc3b))
            self.c.message.emit('선택 가져오기: ' + str(ArteriaCranium_3b0cbc3b))
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
