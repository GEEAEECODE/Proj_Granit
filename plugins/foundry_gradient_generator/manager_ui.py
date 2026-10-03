from datetime import datetime
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from .gradient import Gradient
from .parameter_ui import Section, ParameterEditor
from .presets import read_preset, write_preset
from .ui import GradientPanel
from .diagnostics import log

class ShaderManagerPanel(QtWidgets.QWidget):

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._editing_key = ''
        self._syncing = False
        self._pending_choice = None
        self._selection_timer = QtCore.QTimer(self)
        self._selection_timer.setSingleShot(True)
        self._selection_timer.timeout.connect(self._apply_selection)
        self.setWindowTitle('GrAnit-Shader')
        self.setObjectName('GranitShaderManagerPanel')
        self.setMinimumWidth(420)
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        heading = QtWidgets.QLabel('GrAnit-Shader')
        font = heading.font()
        font.setPointSize(18)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.section_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.section_splitter.setObjectName('GranitSectionSplitter')
        self.section_splitter.setChildrenCollapsible(False)
        self.section_splitter.setHandleWidth(8)
        self.section_splitter.setStyleSheet('QSplitter#GranitSectionSplitter::handle:vertical { background:palette(mid); margin:3px 0; }QSplitter#GranitSectionSplitter::handle:vertical:hover { background:palette(highlight); }')
        scroll.setWidget(self.section_splitter)
        root.addWidget(scroll, 1)
        self.sections = {}
        for key, title in [('list', '셰이더 목록'), ('parameters', '셰이더 조절'), ('gradient', '그라디언트')]:
            section = Section(title, resizable=True)
            self.sections[key] = section
            self.section_splitter.addWidget(section)
        for index in range(1, self.section_splitter.count()):
            handle = self.section_splitter.handle(index)
            handle.setCursor(QtCore.Qt.CursorShape.SplitVCursor)
            handle.setToolTip('위아래로 드래그하여 섹션 높이 조절')
        top = QtWidgets.QHBoxLayout()
        self.shader_list = QtWidgets.QListWidget()
        self.shader_list.setMinimumWidth(140)
        self.shader_list.setStyleSheet('QListWidget { border:1px solid palette(mid); }')
        self.shader_list.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.shader_list.setMinimumHeight(60)
        self.shader_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.shader_list.setAccessibleName('GrAnit 셰이더 인스턴스 목록')
        self.shader_list.setToolTip('선택하면 Painter에서 현재 선택한 텍스처셋에 즉시 적용합니다.')
        left = QtWidgets.QVBoxLayout()
        left.addWidget(self.shader_list, 1)
        apply_row = QtWidgets.QWidget()
        apply_row.setFixedHeight(30)
        apply_layout = QtWidgets.QHBoxLayout(apply_row)
        apply_layout.setContentsMargins(0, 0, 0, 0)
        self.auto_apply = QtWidgets.QCheckBox('생성 즉시 적용')
        self.auto_apply.setToolTip('새로 만들거나 복사한 셰이더를 Painter에서 현재 선택한 텍스처셋에 적용합니다.')
        apply_layout.addWidget(self.auto_apply)
        apply_layout.addStretch()
        left.addWidget(apply_row)
        top.addLayout(left, 3)
        right = QtWidgets.QVBoxLayout()
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(150)
        self.log.setMinimumWidth(115)
        self.log.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        self.log.setMinimumHeight(30)
        self.log.setPlaceholderText('프로젝트를 열고 +로 셰이더를 추가하세요.')
        right.addWidget(self.log)
        buttons = QtWidgets.QHBoxLayout()
        self.remove_button = QtWidgets.QToolButton()
        self.add_button = QtWidgets.QToolButton()
        self.copy_button = QtWidgets.QToolButton()
        self.refresh_button = QtWidgets.QToolButton()
        for button, icon, tip in [(self.remove_button, 'remove', '선택 셰이더 삭제'), (self.add_button, 'add', 'GrAnit 셰이더 인스턴스 추가'), (self.copy_button, 'duplicate', '독립 셰이더로 복제'), (self.refresh_button, 'refresh', '프로젝트 목록 새로고침')]:
            button.setIcon(QtGui.QIcon(str(Path(__file__).with_name('icons') / (icon + '.png'))))
            button.setIconSize(QtCore.QSize(24, 24))
            button.setToolTip(tip)
            button.setAccessibleName(tip)
            button.setFixedSize(32, 30)
            buttons.addWidget(button)
        buttons.addStretch()
        right.addLayout(buttons)
        top.addLayout(right, 2)
        self.sections['list'].body.addLayout(top)
        self.name = QtWidgets.QLineEdit()
        self.name.setPlaceholderText('셰이더 이름')
        name_row = QtWidgets.QHBoxLayout()
        name_row.addWidget(QtWidgets.QLabel('Name'))
        name_row.addWidget(self.name, 1)
        self.sections['parameters'].body.addLayout(name_row)
        self.channel_label = QtWidgets.QLabel()
        self.channel_label.setWordWrap(True)
        self.sections['parameters'].body.addWidget(self.channel_label)
        self.parameters = ParameterEditor()
        self.parameters.setMinimumWidth(0)
        self.sections['parameters'].body.addWidget(self.parameters, 1)
        self.gradient = GradientPanel(options_above=True)
        self.gradient.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.gradient_note = QtWidgets.QLabel('선택한 셰이더의 그라디언트 원본을 불러오거나 새로 만드세요.')
        self.gradient_note.setWordWrap(True)
        self.new_gradient = QtWidgets.QPushButton('새 그라디언트')
        self.new_gradient.setToolTip('선택한 셰이더에 편집 가능한 기본 흑백 그라디언트를 만듭니다.')
        self.sections['gradient'].body.addWidget(self.gradient_note)
        self.sections['gradient'].body.addWidget(self.new_gradient)
        self.sections['gradient'].body.addWidget(self.gradient)
        files = QtWidgets.QHBoxLayout()
        files.addStretch()
        self.export_button = QtWidgets.QPushButton('내보내기')
        self.import_button = QtWidgets.QPushButton('들여오기')
        self.export_button.setToolTip('선택한 셰이더의 그라디언트 값을 JSON 프리셋으로 저장합니다.')
        self.import_button.setToolTip('JSON 프리셋을 선택한 셰이더의 그라디언트로 불러옵니다.')
        files.addWidget(self.export_button)
        files.addWidget(self.import_button)
        self.sections['gradient'].body.addLayout(files)
        self.sections['gradient'].body.addStretch()
        self.shader_list.currentItemChanged.connect(self._selected)
        self.shader_list.itemClicked.connect(self._selected)
        self.add_button.clicked.connect(lambda: self._add())
        self.copy_button.clicked.connect(lambda: self._add(duplicate=True))
        self.remove_button.clicked.connect(lambda: self._run(lambda: controller.remove(controller.state.selected)))
        self.refresh_button.clicked.connect(lambda: self._run(controller.load_project))
        self.name.editingFinished.connect(self._rename)
        self.parameters.edited.connect(self._parameter_changed)
        self.gradient.gradientEdited.connect(self._gradient_changed)
        self.new_gradient.clicked.connect(self._new_gradient)
        self.export_button.clicked.connect(self.export_gradient)
        self.import_button.clicked.connect(self.import_gradient)
        controller.changed.connect(self.refresh)
        controller.selectionChanged.connect(self.load_selection)
        controller.message.connect(self.write_log)
        self.refresh()
        self.load_selection('')
        self.section_splitter.setSizes([180, 400, 220])

    def write_log(self, message):
        self.log.appendPlainText(f'[{datetime.now():%H:%M:%S}] {message}')
        log(message)

    def _run(self, action):
        try:
            return action()
        except Exception as exc:
            self.write_log(str(exc))
            self.refresh()

    def _add(self, duplicate=False):
        source = self.controller.state.selected if duplicate else None
        self._run(lambda: self.controller.add(source, apply_to_active=self.auto_apply.isChecked()))

    def refresh(self):
        controller = self.controller
        self._syncing = True
        try:
            blocker = QtCore.QSignalBlocker(self.shader_list)
            self.shader_list.clear()
            original = QtWidgets.QListWidgetItem('기존 셰이더')
            original.setData(QtCore.Qt.ItemDataRole.UserRole, '')
            original.setToolTip('현재 텍스처셋을 GrAnit 적용 직전의 셰이더와 설정으로 되돌립니다.')
            self.shader_list.addItem(original)
            if not controller.state.selected:
                self.shader_list.setCurrentItem(original)
            for instance in controller.state.instances.values():
                item = QtWidgets.QListWidgetItem('●  ' + instance.name)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, instance.key)
                item.setToolTip(instance.name + ' · 선택한 텍스처셋에 적용하고 값을 편집합니다.')
                self.shader_list.addItem(item)
                if instance.key == controller.state.selected:
                    self.shader_list.setCurrentItem(item)
            del blocker
            self.shader_list.setEnabled(controller.loaded)
            self.add_button.setEnabled(controller.loaded)
            self.auto_apply.setEnabled(controller.loaded)
            self.copy_button.setEnabled(controller.loaded and controller.current is not None)
            binding = controller.state.painter_bindings.get(controller.state.selected)
            linked = [name for name, item in controller.texture_sets.items() if binding and item['shader'] == binding.native_label]
            self.remove_button.setEnabled(controller.loaded and controller.current is not None and (not linked))
            self.remove_button.setToolTip('사용 중이라 삭제할 수 없습니다: ' + ', '.join(linked) if linked else '선택 셰이더 삭제')
        finally:
            self._syncing = False

    def _selected(self, item, _previous=None):
        if self._syncing or item is None:
            return
        key = item.data(QtCore.Qt.ItemDataRole.UserRole)

        def queue():
            self.controller.require_ready()
            target = self.controller.bridge.active_texture_set()
            self._pending_choice = (self.controller.project, target, key)
            self._selection_timer.start(0)
        self._run(queue)

    def _apply_selection(self):
        choice = self._pending_choice
        self._pending_choice = None
        if choice is None or not self.controller.loaded:
            return
        project, target, key = choice
        if project == self.controller.project:
            self._run(lambda: self.controller.choose(key, target))

    def load_selection(self, key):
        self._selection_timer.stop()
        self._pending_choice = None
        self.gradient.close_editors()
        self._editing_key = key
        instance = self.controller.state.instances.get(key)
        self.sections['parameters'].content.setEnabled(instance is not None and self.controller.loaded)
        self.sections['gradient'].content.setEnabled(instance is not None and self.controller.loaded)
        self.name.setText(instance.name if instance else '')
        self.parameters.clear()
        self.channel_label.clear()
        if instance:
            shader = self.controller.state.shaders[instance.shader_key]
            self.parameters.load(shader.parameters, instance.parameters.values, shader.ramp_parameter)
            self.channel_label.setText('채널 · ' + ', '.join((c.label or c.identifier for c in shader.channels)))
            if instance.gradient is not None:
                self.gradient.load_gradient(instance.gradient)
        has_gradient = bool(instance and instance.gradient is not None)
        self.gradient.setVisible(has_gradient)
        self.gradient_note.setVisible(not has_gradient)
        self.new_gradient.setVisible(not has_gradient)
        self.export_button.setEnabled(has_gradient)
        self.refresh()

    def _rename(self):
        if self._editing_key:
            self._run(lambda: self.controller.rename(self._editing_key, self.name.text()))

    def _parameter_changed(self, identifier, value):
        if self._editing_key:
            self._run(lambda: self.controller.edit_parameter(self._editing_key, identifier, value))

    def _gradient_changed(self, gradient):
        if self._editing_key:
            self._run(lambda: self.controller.edit_gradient(self._editing_key, gradient))

    def _new_gradient(self):
        self._gradient_changed(Gradient.default())
        self.load_selection(self._editing_key)

    def export_gradient(self):
        instance = self.controller.current
        if instance is None or instance.gradient is None:
            return
        path, _filter = QtWidgets.QFileDialog.getSaveFileName(self, '그라디언트 내보내기', 'gradient.json', 'JSON (*.json)')
        if path:
            self._run(lambda: write_preset(path, instance.gradient))

    def import_gradient(self):
        key = self._editing_key
        if not key:
            return
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(self, '그라디언트 들여오기', '', 'JSON (*.json)')
        if path:

            def load():
                self.controller.edit_gradient(key, read_preset(path))
                self.load_selection(key)
                self.write_log('그라디언트 값 불러옴')
            self._run(load)

    def shutdown(self):
        self._selection_timer.stop()
        self._pending_choice = None
        self.gradient.shutdown()
        self.controller.shutdown()
