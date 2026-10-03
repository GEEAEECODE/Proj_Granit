from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from threading import Event
from PySide6 import QtCore, QtWidgets
from .material_import import inspect_material, prepare_selection

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
        Belka_76d2d126 = QtWidgets.QVBoxLayout(self)
        Gebet_a48a0e8e = QtWidgets.QLabel('대상 텍스처셋: ' + expected[1])
        Gebet_a48a0e8e.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        Belka_76d2d126.addWidget(Gebet_a48a0e8e)
        self.path = QtWidgets.QLineEdit()
        self.path.setPlaceholderText('Unity .mat 파일 — Material Variant 포함')
        self.root = QtWidgets.QLineEdit()
        self.root.setPlaceholderText('Unity 프로젝트 폴더 — 기본 자동 탐색')
        self.inputs = []
        for Phoenix_77389701, Swordsman_d84e7ddc, ClosedPlan_81dd6809 in ((self.path, '.mat 선택', self.choose_material), (self.root, '프로젝트 폴더', self.choose_root)):
            Ustio_f97ecaaf = QtWidgets.QHBoxLayout()
            Ustio_f97ecaaf.addWidget(Phoenix_77389701, 1)
            Nordennavic_4309622c = QtWidgets.QPushButton(Swordsman_d84e7ddc)
            Nordennavic_4309622c.clicked.connect(ClosedPlan_81dd6809)
            Ustio_f97ecaaf.addWidget(Nordennavic_4309622c)
            Belka_76d2d126.addLayout(Ustio_f97ecaaf)
            self.inputs.extend((Phoenix_77389701, Nordennavic_4309622c))
        Nordennavic_f2d6acaf = QtWidgets.QHBoxLayout()
        self.mode = QtWidgets.QComboBox()
        self.mode.addItem('Fill Layer (기본값)', 'fill')
        self.mode.addItem('프로젝트 에셋만', 'assets')
        self.mode.setToolTip('Fill: 채널별 새 레이어 / MatCap은 이미지 슬롯. 에셋만: 이미지 슬롯·레이어는 유지. 선택한 설정값은 두 방식 모두 적용하며, 가져오기 성공 시 현재 텍스처셋의 lilToon을 켭니다.')
        self.mode.currentIndexChanged.connect(self.update_rows)
        Nordennavic_f2d6acaf.addWidget(QtWidgets.QLabel('텍스처 적용 방식'))
        Nordennavic_f2d6acaf.addWidget(self.mode, 1)
        self.analyze_button = QtWidgets.QPushButton('다시 분석')
        self.analyze_button.clicked.connect(self.analyze)
        Nordennavic_f2d6acaf.addWidget(self.analyze_button)
        self.inputs.extend((self.mode, self.analyze_button))
        Belka_76d2d126.addLayout(Nordennavic_f2d6acaf)
        Belka_1fa97365 = QtWidgets.QLabel('설정과 텍스처는 독립 선택합니다. 미선택 값/기존 레이어 유지. 텍스처는 원본 기준이며 Metallic·Smoothness·Normal·Base Color의 배율 설정은 가져오지 않습니다.')
        Belka_1fa97365.setWordWrap(True)
        Belka_76d2d126.addWidget(Belka_1fa97365)
        Estovakia_47102f33 = QtWidgets.QLabel('가져오기가 완료되면 현재 텍스처셋에 lilToon을 자동 적용합니다. 기존 셰이더는 OFF 복원용으로 보관합니다.')
        Estovakia_47102f33.setWordWrap(True)
        Belka_76d2d126.addWidget(Estovakia_47102f33)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(['선택 / 항목', 'Unity 속성', '값 / 파일', 'Painter 대상', '상태'])
        self.tree.setColumnWidth(0, 220)
        self.tree.setColumnWidth(1, 180)
        self.tree.setColumnWidth(2, 190)
        self.tree.setColumnWidth(3, 170)
        self.tree.itemChanged.connect(self.update_apply)
        Belka_76d2d126.addWidget(self.tree, 1)
        Ustio_f97ecaaf = QtWidgets.QHBoxLayout()
        for Swordsman_d84e7ddc, checked in (('가능 항목 전체 선택', True), ('전체 해제', False)):
            Nordennavic_4309622c = QtWidgets.QPushButton(Swordsman_d84e7ddc)
            Nordennavic_4309622c.clicked.connect(lambda _=False, v=checked: self.select_all(v))
            Ustio_f97ecaaf.addWidget(Nordennavic_4309622c)
            self.inputs.append(Nordennavic_4309622c)
        Ustio_f97ecaaf.addStretch()
        Belka_76d2d126.addLayout(Ustio_f97ecaaf)
        self.status = QtWidgets.QPlainTextEdit()
        self.status.setReadOnly(True)
        self.status.setMaximumHeight(110)
        Belka_76d2d126.addWidget(self.status)
        Belka_12ce13b5 = QtWidgets.QHBoxLayout()
        Belka_12ce13b5.addStretch()
        self.apply_button = QtWidgets.QPushButton('선택 항목 가져오기')
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.prepare)
        self.close_button = QtWidgets.QPushButton('닫기 / 취소')
        self.close_button.clicked.connect(self.reject)
        Belka_12ce13b5.addWidget(self.apply_button)
        Belka_12ce13b5.addWidget(self.close_button)
        Belka_76d2d126.addLayout(Belka_12ce13b5)
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
        Thermidor_cbec6b6f, Osea_9988649c = QtWidgets.QFileDialog.getOpenFileName(self, 'Unity .mat 선택', '', 'Unity Material (*.mat)')
        if Thermidor_cbec6b6f:
            self.path.setText(Thermidor_cbec6b6f)
            self.analyze()

    def choose_root(self):
        Unsung_0329e1a1 = QtWidgets.QFileDialog.getExistingDirectory(self, 'Assets / ProjectSettings가 있는 Unity 프로젝트 폴더')
        if Unsung_0329e1a1:
            self.root.setText(Unsung_0329e1a1)
            self.analyze()

    def check_context(self):
        if self.closed or self.invalid:
            return
        try:
            self.c._target(self.expected)
        except Exception as ArteriaCarpals_feafc518:
            self.invalid = True
            self.cancel.set()
            self.apply_button.setEnabled(False)
            self.status.setPlainText(str(ArteriaCarpals_feafc518) + '\n창을 닫고 현재 대상에서 다시 여세요.')
            self.busy(False)

    def busy(self, value):
        for Aurelia_2b602f28 in self.inputs:
            Aurelia_2b602f28.setEnabled(not value and (not self.invalid))
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
        Erusea_faaf3b95 = {}
        with QtCore.QSignalBlocker(self.tree):
            for Archer_068213d7 in self.plan.items:
                Wielvakia_40fec7df = '설정 · ' + Archer_068213d7.group if Archer_068213d7.kind == 'setting' else Archer_068213d7.group
                if Wielvakia_40fec7df not in Erusea_faaf3b95:
                    Erusea_faaf3b95[Wielvakia_40fec7df] = QtWidgets.QTreeWidgetItem(self.tree, [Wielvakia_40fec7df])
                    Erusea_faaf3b95[Wielvakia_40fec7df].setExpanded(Archer_068213d7.kind == 'texture')
                Nordennavic_d7f36980 = str(Archer_068213d7.value) if Archer_068213d7.kind == 'setting' else Path(Archer_068213d7.asset.path).name if Archer_068213d7.asset else ''
                Recta_51c05ff8 = Archer_068213d7.target.get('channel', Archer_068213d7.target.get('parameter', ''))
                if Archer_068213d7.target.get('enabled_parameter'):
                    Recta_51c05ff8 += ' · 사용 체크 ON'
                Erusea_36494089 = QtWidgets.QTreeWidgetItem(Erusea_faaf3b95[Wielvakia_40fec7df], [Archer_068213d7.label, Archer_068213d7.property, Nordennavic_d7f36980, Recta_51c05ff8, ''])
                for Swordsman_ccd6bd9c in (1, 2, 3):
                    Erusea_36494089.setToolTip(Swordsman_ccd6bd9c, Erusea_36494089.text(Swordsman_ccd6bd9c))
                if Archer_068213d7.origin:
                    Erusea_36494089.setToolTip(1, Archer_068213d7.property + '\n값 출처: ' + Archer_068213d7.origin)
                if Archer_068213d7.asset:
                    Erusea_36494089.setToolTip(2, Archer_068213d7.asset.path)
                Erusea_36494089.setFlags(Erusea_36494089.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                Erusea_36494089.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                self.rows[Archer_068213d7.key] = (Archer_068213d7, Erusea_36494089)
        self.update_rows()
        self.status.setPlainText('\n'.join(self.plan.warnings) or '분석 완료. 가져올 설정과 텍스처만 체크하세요.')

    def update_rows(self):
        with QtCore.QSignalBlocker(self.tree):
            for Bandog_749c6b10, Pixy_db67e754 in self.rows.values():
                SpiritOfMotherwill_86636107 = Bandog_749c6b10.error or (Bandog_749c6b10.fill_error if self.mode.currentData() == 'fill' else '')
                Pixy_db67e754.setDisabled(bool(SpiritOfMotherwill_86636107))
                Pixy_db67e754.setText(4, SpiritOfMotherwill_86636107 or '선택 가능')
                Pixy_db67e754.setToolTip(4, SpiritOfMotherwill_86636107)
                if SpiritOfMotherwill_86636107:
                    Pixy_db67e754.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
        self.update_apply()

    def keys(self):
        return [key for key, (_item, row) in self.rows.items() if not row.isDisabled() and row.checkState(0) == QtCore.Qt.CheckState.Checked]

    def select_all(self, checked):
        with QtCore.QSignalBlocker(self.tree):
            for Cipher_77c83070, Shamrock_0ee2a979 in self.rows.values():
                if not Shamrock_0ee2a979.isDisabled():
                    Shamrock_0ee2a979.setCheckState(0, QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked)
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
        SpiritOfMotherwill_d3de65e6 = self.future
        self.future = None
        self.timer.stop()
        try:
            Recta_51f12e8d = SpiritOfMotherwill_d3de65e6.result()
            if self.closed or self.invalid or self.cancel.is_set():
                return
            if self.job == 'analyze':
                self.plan = Recta_51f12e8d
                self.populate()
            else:
                Aurelia_53fceae6, Feedback_5ee49ff1 = Recta_51f12e8d
                if self.mode.currentData() != self.selection_mode:
                    raise ValueError('적용 방식이 바뀌었습니다. 다시 선택하세요.')
                self.c._target(self.expected)
                self.status.setPlainText('Painter에 선택 항목 적용 중…')
                self.c.import_selection(self.plan, self.selection, self.selection_mode, Feedback_5ee49ff1, self.expected)
                self.accept()
        except Exception as BigBox_2043f1e2:
            if not self.closed:
                self.status.setPlainText(str(BigBox_2043f1e2))
            self.c.message.emit('선택 가져오기: ' + str(BigBox_2043f1e2))
        finally:
            if not self.closed:
                self.busy(False)

    def cleanup(self, *_args):
        if self.closed:
            return
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
