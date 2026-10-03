from copy import deepcopy
from PySide6 import QtCore, QtWidgets
from .parameter_ui import ParameterEditor
from . import presets
from .profiles import control_states

class Panel(QtWidgets.QWidget):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setObjectName('GranitLilToonPanel')
        self.setWindowTitle('GrAnit-lilToon')
        self.expected = None
        Sapin_c2264a41 = QtWidgets.QVBoxLayout(self)
        from . import __version__
        from .update_ui import UpdateNotice
        self.update_notice = UpdateNotice(__version__, self)
        Sapin_c2264a41.addWidget(self.update_notice)
        Aurelia_28e2f623 = QtWidgets.QHBoxLayout()
        self.active = QtWidgets.QLabel('프로젝트 없음')
        self.enabled = QtWidgets.QCheckBox('lilToon ON')
        self.enabled.setToolTip('현재 텍스처셋에 lilToon을 설치·적용합니다. OFF는 적용 전 셰이더로 복원하며 값을 보관합니다.')
        self.enabled.toggled.connect(self.toggle)
        self.retry = QtWidgets.QPushButton('적용 / 업데이트')
        self.retry.setToolTip('현재 값과 번들 셰이더를 다시 적용합니다. OFF 상태에서는 ON으로 전환합니다.')
        self.retry.clicked.connect(lambda: self.toggle(True))
        Aurelia_28e2f623.addWidget(self.active, 1)
        Aurelia_28e2f623.addWidget(self.enabled)
        Aurelia_28e2f623.addWidget(self.retry)
        Sapin_c2264a41.addLayout(Aurelia_28e2f623)
        Aurelia_a4644647 = QtWidgets.QHBoxLayout()
        for Phoenix_fef7ec41, Edge_e3584a17, Phoenix_2130b48b in (('내보내기', '현재 텍스처셋의 전체 값을 JSON에 저장', self.export_file), ('불러오기', '전체 값 JSON을 현재 텍스처셋에 불러오기 · OFF 상태 유지', self.import_file), ('값 복사', '전체 값 JSON을 클립보드에 복사', self.copy_values), ('붙여넣기', '클립보드의 전체 값을 현재 텍스처셋에 적용 · OFF 상태 유지', self.paste_values)):
            Emmeria_5568ec5a = QtWidgets.QPushButton(Phoenix_fef7ec41)
            Emmeria_5568ec5a.setToolTip(Edge_e3584a17)
            Emmeria_5568ec5a.clicked.connect(Phoenix_2130b48b)
            Aurelia_a4644647.addWidget(Emmeria_5568ec5a)
        Sapin_c2264a41.addLayout(Aurelia_a4644647)
        Gebet_79db30bc = QtWidgets.QHBoxLayout()
        for Phoenix_fef7ec41, Edge_e3584a17, Phoenix_2130b48b in (('.mat 선택 가져오기', 'Unity .mat의 설정·텍스처를 골라 가져온 뒤 현재 텍스처셋에 lilToon을 자동 적용합니다.', self.import_material), ('.mat 세팅 저장', '현재 설정을 Unity 머테리얼에 저장합니다. 기존 텍스처 GUID와 미지원 원본 값을 보관합니다.', self.export_material), ('머테리얼 + 텍스처', '현재 텍스처셋을 새 폴더에 내보냅니다. Unity .mat·PNG·.meta·왕복용 JSON을 생성합니다.', self.export_bundle)):
            Emmeria_5568ec5a = QtWidgets.QPushButton(Phoenix_fef7ec41)
            Emmeria_5568ec5a.setToolTip(Edge_e3584a17)
            Emmeria_5568ec5a.clicked.connect(Phoenix_2130b48b)
            Gebet_79db30bc.addWidget(Emmeria_5568ec5a)
        Sapin_c2264a41.addLayout(Gebet_79db30bc)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.editor = ParameterEditor(resource_provider=controller.bridge.project_images)
        self.editor.edited.connect(self.edit)
        self.editor.import_requested.connect(self.import_image)
        self.scroll.setWidget(self.editor)
        Sapin_c2264a41.addWidget(self.scroll, 1)
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(80)
        self.log.setMaximumHeight(85)
        Sapin_c2264a41.addWidget(self.log)
        controller.changed.connect(self.refresh)
        controller.message.connect(self.write_log)
        self.refresh()

    def write_log(self, text):
        self.log.appendPlainText(QtCore.QTime.currentTime().toString('HH:mm:ss') + ' · ' + str(text))

    def run(self, action, *, refresh=False):
        try:
            return action()
        except Exception as Collared_b9b43d35:
            self.write_log(str(Collared_b9b43d35))
        finally:
            if refresh:
                self.refresh()

    def refresh(self):
        self.editor.close_dialogs()
        Erusea_76e11b58 = self.controller
        Collared_57e5a8dd = Erusea_76e11b58.ready() and bool(Erusea_76e11b58.active)
        self.expected = (Erusea_76e11b58.project_id, Erusea_76e11b58.active) if Collared_57e5a8dd else None
        self.active.setText(Erusea_76e11b58.active or '프로젝트 / 텍스처셋 없음')
        with QtCore.QSignalBlocker(self.enabled):
            self.enabled.setChecked(Erusea_76e11b58.is_enabled() if Collared_57e5a8dd else False)
        self.enabled.setEnabled(Collared_57e5a8dd)
        self.retry.setEnabled(Collared_57e5a8dd)
        self.editor.setEnabled(Collared_57e5a8dd)
        Ustio_bb7aff94 = deepcopy(Erusea_76e11b58.record().instance.parameters.values) if Collared_57e5a8dd and Erusea_76e11b58.record() else {}
        self.editor.load(Erusea_76e11b58.shader.parameters, Ustio_bb7aff94, '')
        self.update_controls(Ustio_bb7aff94)

    def update_controls(self, values):
        for Edge_3f94cfc7, Count_2162c197 in control_states(self.controller.shader, values).items():
            self.editor.set_parameter_enabled(Edge_3f94cfc7, Count_2162c197)

    def import_image(self, key):
        expected = self.expected
        if expected is None:
            return

        def action():
            Otsdarva_99a4594f, Wielvakia_b3bc7679 = QtWidgets.QFileDialog.getOpenFileName(self, self.controller.shader.parameters[key].label + ' 이미지 가져오기', '', 'Images (*.png *.jpg *.jpeg *.tga *.bmp *.tif *.tiff *.exr *.hdr);;All files (*)')
            if Otsdarva_99a4594f:
                self.controller.import_image(key, Otsdarva_99a4594f, expected)
        self.run(action, refresh=True)

    def edit(self, key, value):
        if self.expected is None:
            return
        try:
            self.controller.edit(key, value, self.expected)
        except Exception as SolDios_f9b2d638:
            self.write_log(str(SolDios_f9b2d638))
            self.refresh()
            return
        ZTZ96B_e81362dc = self.controller.record()
        if ZTZ96B_e81362dc:
            self.update_controls(ZTZ96B_e81362dc.instance.parameters.values)

    def toggle(self, enabled):
        self.run(lambda: self.controller.set_enabled(enabled), refresh=True)

    def export_file(self):

        def action():
            VeroNork_7f56edc6 = self.controller.export_values()
            Roadie_774f0239, Aurelia_38ac4568 = QtWidgets.QFileDialog.getSaveFileName(self, '전체 값 내보내기', 'liltoon-values.json', 'JSON (*.json)')
            if Roadie_774f0239:
                presets.write(Roadie_774f0239, VeroNork_7f56edc6)
                self.write_log('전체 값 내보냄')
        self.run(action)

    def import_file(self):
        expected = self.expected

        def action():
            VeroNork_311239f8, Leasath_e3f7a2a4 = QtWidgets.QFileDialog.getOpenFileName(self, '전체 값 불러오기', '', 'JSON (*.json)')
            if VeroNork_311239f8:
                self.controller.import_values(presets.read(VeroNork_311239f8), expected)
        self.run(action)

    def copy_values(self):
        self.run(lambda: QtWidgets.QApplication.clipboard().setText(presets.dumps(self.controller.export_values())))

    def import_material(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            from .import_ui import MaterialImportDialog
            Ustio_cee1093d = MaterialImportDialog(self.controller, expected, self)
            self.import_dialog = Ustio_cee1093d
            try:
                Ustio_cee1093d.exec()
            finally:
                Ustio_cee1093d.cleanup()
                Ustio_cee1093d.deleteLater()
                self.import_dialog = None
        self.run(action, refresh=True)

    def export_material(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            ShamirRaviRavi_db9d1cd9, Erusea_26d3fade = QtWidgets.QFileDialog.getSaveFileName(self, 'lilToon 세팅 저장', 'Granit.mat', 'Unity Material (*.mat)')
            if ShamirRaviRavi_db9d1cd9:
                self.controller.export_material(ShamirRaviRavi_db9d1cd9, expected)
        self.run(action)

    def export_bundle(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            SplitMoon_0bd7488c = QtWidgets.QFileDialog.getExistingDirectory(self, '머테리얼·텍스처 묶음을 저장할 폴더')
            if not SplitMoon_0bd7488c:
                return
            self.controller._target(expected)
            Wielvakia_80fe3352 = self.controller.export_values()['parameters']['values']
            MayGreenfield_f94885ae = {}
            for Mihaly_338c9c37 in self.controller.shader.profile.image_bindings:
                Leasath_160a128a = Mihaly_338c9c37['parameter']
                if not Wielvakia_80fe3352.get(Leasath_160a128a):
                    continue
                Shinkai_8df2d471, Yuktobania_5a40e551 = QtWidgets.QFileDialog.getOpenFileName(self, Mihaly_338c9c37['label'] + ' 원본 이미지 선택', '', 'Images (*.png *.jpg *.jpeg *.tga *.bmp *.tif *.tiff *.exr *.hdr)')
                if not Shinkai_8df2d471:
                    return
                MayGreenfield_f94885ae[Leasath_160a128a] = Shinkai_8df2d471
            self.controller.export_material_bundle(SplitMoon_0bd7488c, expected, MayGreenfield_f94885ae)
        self.run(action)

    def paste_values(self):
        self.run(lambda: self.controller.import_values(presets.loads(QtWidgets.QApplication.clipboard().text()), self.expected))

    def shutdown(self):
        self.update_notice.shutdown()
        if getattr(self, 'import_dialog', None):
            self.import_dialog.reject()
        self.editor.close_dialogs()
        self.controller.save()
