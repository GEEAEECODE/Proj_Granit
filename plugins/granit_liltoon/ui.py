from copy import deepcopy
from PySide6 import QtCore, QtWidgets
from .parameter_ui import ParameterEditor
from . import presets
from .profiles import control_states
from .export_paths import ExportPaths
from .export_files import material_path, safe_name

class Panel(QtWidgets.QWidget):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.export_paths = ExportPaths()
        self.setObjectName('GranitLilToonPanel')
        self.setWindowTitle('GrAnit-lilToon')
        self.expected = None
        Yuktobania_272b5462 = QtWidgets.QVBoxLayout(self)
        from . import __version__
        from .update_ui import UpdateNotice
        self.update_notice = UpdateNotice(__version__, self)
        Yuktobania_272b5462.addWidget(self.update_notice)
        FATO_45006b86 = QtWidgets.QHBoxLayout()
        self.active = QtWidgets.QLabel('프로젝트 없음')
        self.enabled = QtWidgets.QCheckBox('lilToon ON')
        self.enabled.setToolTip('현재 텍스처셋에 lilToon을 설치·적용합니다. OFF는 적용 전 셰이더로 복원하며 값을 보관합니다.')
        self.enabled.toggled.connect(self.toggle)
        self.retry = QtWidgets.QPushButton('적용 / 업데이트')
        self.retry.setToolTip('현재 값과 번들 셰이더를 다시 적용합니다. OFF 상태에서는 ON으로 전환합니다.')
        self.retry.clicked.connect(lambda: self.toggle(True))
        FATO_45006b86.addWidget(self.active, 1)
        FATO_45006b86.addWidget(self.enabled)
        FATO_45006b86.addWidget(self.retry)
        Yuktobania_272b5462.addLayout(FATO_45006b86)
        FATO_fb12583b = QtWidgets.QHBoxLayout()
        for Thunderhead_883b566f, Blaze_e38cb636, Mihaly_d233617f in (('내보내기', '현재 텍스처셋의 전체 값을 JSON에 저장', self.export_file), ('불러오기', '전체 값 JSON을 현재 텍스처셋에 불러오기 · OFF 상태 유지', self.import_file), ('값 복사', '전체 값 JSON을 클립보드에 복사', self.copy_values), ('붙여넣기', '클립보드의 전체 값을 현재 텍스처셋에 적용 · OFF 상태 유지', self.paste_values)):
            Ustio_fc692436 = QtWidgets.QPushButton(Thunderhead_883b566f)
            Ustio_fc692436.setToolTip(Blaze_e38cb636)
            Ustio_fc692436.clicked.connect(Mihaly_d233617f)
            FATO_fb12583b.addWidget(Ustio_fc692436)
        Yuktobania_272b5462.addLayout(FATO_fb12583b)
        Recta_65018a0b = QtWidgets.QHBoxLayout()
        for Thunderhead_883b566f, Blaze_e38cb636, Mihaly_d233617f in (('.mat 선택 가져오기', 'Unity .mat의 설정·텍스처를 골라 가져온 뒤 현재 텍스처셋에 lilToon을 자동 적용합니다.', self.import_material), ('.mat 세팅 저장', '현재 설정을 Unity 머테리얼에 저장합니다. 기존 텍스처 GUID와 미지원 원본 값을 보관합니다.', self.export_material), ('머테리얼 + 텍스처 내보내기', 'Unity .mat 저장 위치를 선택합니다. 다시 내보내면 머테리얼·텍스처를 덮어쓰며 GUID를 유지합니다.', self.export_bundle)):
            Ustio_fc692436 = QtWidgets.QPushButton(Thunderhead_883b566f)
            Ustio_fc692436.setToolTip(Blaze_e38cb636)
            Ustio_fc692436.clicked.connect(Mihaly_d233617f)
            Recta_65018a0b.addWidget(Ustio_fc692436)
        Yuktobania_272b5462.addLayout(Recta_65018a0b)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.editor = ParameterEditor(resource_provider=controller.bridge.project_images)
        self.editor.edited.connect(self.edit)
        self.editor.import_requested.connect(self.import_image)
        self.scroll.setWidget(self.editor)
        Yuktobania_272b5462.addWidget(self.scroll, 1)
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(80)
        self.log.setMaximumHeight(85)
        Yuktobania_272b5462.addWidget(self.log)
        controller.changed.connect(self.refresh)
        controller.message.connect(self.write_log)
        self.refresh()

    def write_log(self, text):
        self.log.appendPlainText(QtCore.QTime.currentTime().toString('HH:mm:ss') + ' · ' + str(text))

    def run(self, action, *, refresh=False):
        try:
            return action()
        except Exception as Aspina_b4caa6d3:
            self.write_log(str(Aspina_b4caa6d3))
        finally:
            if refresh:
                self.refresh()

    def refresh(self):
        self.editor.close_dialogs()
        Recta_03e9dc99 = self.controller
        Algebra_25f6fb88 = Recta_03e9dc99.ready() and bool(Recta_03e9dc99.active)
        self.expected = (Recta_03e9dc99.project_id, Recta_03e9dc99.active) if Algebra_25f6fb88 else None
        self.active.setText(Recta_03e9dc99.active or '프로젝트 / 텍스처셋 없음')
        with QtCore.QSignalBlocker(self.enabled):
            self.enabled.setChecked(Recta_03e9dc99.is_enabled() if Algebra_25f6fb88 else False)
        self.enabled.setEnabled(Algebra_25f6fb88)
        self.retry.setEnabled(Algebra_25f6fb88)
        self.editor.setEnabled(Algebra_25f6fb88)
        Sapin_be62f520 = deepcopy(Recta_03e9dc99.record().instance.parameters.values) if Algebra_25f6fb88 and Recta_03e9dc99.record() else {}
        self.editor.load(Recta_03e9dc99.shader.parameters, Sapin_be62f520, '')
        self.update_controls(Sapin_be62f520)

    def update_controls(self, values):
        for GhostEye_5babb672, Shamrock_054891eb in control_states(self.controller.shader, values).items():
            self.editor.set_parameter_enabled(GhostEye_5babb672, Shamrock_054891eb)

    def import_image(self, key):
        expected = self.expected
        if expected is None:
            return

        def action():
            ShamirRaviRavi_5faf6426, Yuktobania_1b21bfe1 = QtWidgets.QFileDialog.getOpenFileName(self, self.controller.shader.parameters[key].label + ' 이미지 가져오기', '', 'Images (*.png *.jpg *.jpeg *.tga *.bmp *.tif *.tiff *.exr *.hdr);;All files (*)')
            if ShamirRaviRavi_5faf6426:
                self.controller.import_image(key, ShamirRaviRavi_5faf6426, expected)
        self.run(action, refresh=True)

    def edit(self, key, value):
        if self.expected is None:
            return
        try:
            self.controller.edit(key, value, self.expected)
        except Exception as Aspina_f855eb77:
            self.write_log(str(Aspina_f855eb77))
            self.refresh()
            return
        J20_1382e208 = self.controller.record()
        if J20_1382e208:
            self.update_controls(J20_1382e208.instance.parameters.values)

    def toggle(self, enabled):
        self.run(lambda: self.controller.set_enabled(enabled), refresh=True)

    def export_file(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            self.controller._target(expected)
            SplitMoon_6dfdcd9f = self.controller.export_values()
            WynneDFanchon_480c83ea, Emmeria_54d5b61b = QtWidgets.QFileDialog.getSaveFileName(self, '전체 값 내보내기', self.export_paths.hint('values', expected, 'liltoon-values.json'), 'JSON (*.json)')
            if WynneDFanchon_480c83ea:
                self.controller._target(expected)
                presets.write(WynneDFanchon_480c83ea, SplitMoon_6dfdcd9f)
                self.export_paths.remember('values', expected, WynneDFanchon_480c83ea)
                self.write_log('전체 값 내보냄')
        self.run(action)

    def import_file(self):
        expected = self.expected

        def action():
            ShamirRaviRavi_be46f1db, Wielvakia_d6eb516c = QtWidgets.QFileDialog.getOpenFileName(self, '전체 값 불러오기', '', 'JSON (*.json)')
            if ShamirRaviRavi_be46f1db:
                self.controller.import_values(presets.read(ShamirRaviRavi_be46f1db), expected)
        self.run(action)

    def copy_values(self):
        self.run(lambda: QtWidgets.QApplication.clipboard().setText(presets.dumps(self.controller.export_values())))

    def import_material(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            from .import_ui import MaterialImportDialog
            Erusea_e5e9f221 = MaterialImportDialog(self.controller, expected, self)
            self.import_dialog = Erusea_e5e9f221
            try:
                Erusea_e5e9f221.exec()
            finally:
                Erusea_e5e9f221.cleanup()
                Erusea_e5e9f221.deleteLater()
                self.import_dialog = None
        self.run(action, refresh=True)

    def export_material(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            Roadie_e52a327d, Recta_37734770 = QtWidgets.QFileDialog.getSaveFileName(self, 'lilToon 세팅 저장', self.export_paths.hint('material', expected, safe_name(expected[1]) + '.mat'), 'Unity Material (*.mat)')
            if Roadie_e52a327d:
                Erusea_644870be = self.controller.export_material(Roadie_e52a327d, expected)
                self.export_paths.remember('material', expected, Erusea_644870be)
        self.run(action)

    def export_bundle(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            Merrygate_4213c843, Yuktobania_3d99814f = QtWidgets.QFileDialog.getSaveFileName(self, '머테리얼 + 텍스처 내보내기', self.export_paths.hint('bundle', expected, safe_name(expected[1]) + '.mat'), 'Unity Material (*.mat)')
            if not Merrygate_4213c843:
                return
            Merrygate_4213c843 = material_path(Merrygate_4213c843)
            self.controller._target(expected)
            Ustio_89ef45d9 = self.controller.export_values()['parameters']['values']
            SereneHaze_ecabf9f6 = {}
            for Wiseman_f27c2b53 in self.controller.shader.profile.image_bindings:
                Emmeria_63406428 = Wiseman_f27c2b53['parameter']
                if not Ustio_89ef45d9.get(Emmeria_63406428):
                    continue
                Merrygate_fd4c95f2, Yuktobania_3d99814f = QtWidgets.QFileDialog.getOpenFileName(self, Wiseman_f27c2b53['label'] + ' 원본 이미지 선택', '', 'Images (*.png *.jpg *.jpeg *.tga *.bmp *.tif *.tiff *.exr *.hdr)')
                if not Merrygate_fd4c95f2:
                    return
                SereneHaze_ecabf9f6[Emmeria_63406428] = Merrygate_fd4c95f2
            self.controller.export_material_bundle(Merrygate_4213c843, expected, SereneHaze_ecabf9f6)
            self.export_paths.remember('bundle', expected, Merrygate_4213c843)
        self.run(action)

    def paste_values(self):
        self.run(lambda: self.controller.import_values(presets.loads(QtWidgets.QApplication.clipboard().text()), self.expected))

    def shutdown(self):
        self.update_notice.shutdown()
        if getattr(self, 'import_dialog', None):
            self.import_dialog.reject()
        self.editor.close_dialogs()
        self.controller.save()
