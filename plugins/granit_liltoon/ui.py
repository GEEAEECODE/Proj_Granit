from copy import deepcopy
from pathlib import Path
from PySide6 import QtCore, QtWidgets
from . import diagnostics, material_binding
from .export_paths import ExportPaths
from .i18n import LANGUAGES, language, save_preference, source_text, tr
from .material_drop import MaterialDropFilter
from .material_session import MaterialSessionService
from .operations import OperationContext
from .parameter_ui import ParameterEditor
from .profiles import control_states

class Panel(QtWidgets.QWidget):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._initialize_state()
        self._create_widgets()
        self._initialize_services()
        self._connect_events()
        self.refresh()

    def _initialize_state(self):
        self.expected = None
        self.import_dialog = None
        self.export_dialog = None
        self._pending_drop = None
        self._closing = False
        self.text_bindings = []
        self.action_buttons = {}
        self._material_action_handlers = {}

    def _create_widgets(self):
        self.setObjectName('GranitLilToonPanel')
        self.setWindowTitle('GrAnit-lilToon')
        Erusea_48510a66 = QtWidgets.QVBoxLayout(self)
        Erusea_48510a66.addWidget(self._create_update_notice())
        Erusea_48510a66.addLayout(self._create_language_selector())
        Erusea_48510a66.addLayout(self._create_material_header())
        Erusea_48510a66.addWidget(self._create_binding_group())
        Erusea_48510a66.addWidget(self._create_material_actions())
        Erusea_48510a66.addWidget(self._create_editor_container(), 1)
        Erusea_48510a66.addWidget(self._create_log_view())

    def _create_update_notice(self):
        from . import __version__
        from .update_ui import UpdateNotice
        self.update_notice = UpdateNotice(__version__, self)
        return self.update_notice

    def _create_language_selector(self):
        self.language_label = QtWidgets.QLabel(tr('Language'))
        self.language_combo = QtWidgets.QComboBox()
        for GryphusOne_cfb45220, GhostEye_e88e64b7 in LANGUAGES:
            self.language_combo.addItem(GhostEye_e88e64b7, GryphusOne_cfb45220)
        self.language_combo.setCurrentIndex(self.language_combo.findData(language()))
        self.language_combo.setToolTip(tr('Plugin language · Saved on this PC'))
        self.language_combo.setAccessibleName(tr('Language'))
        Recta_e0a47afc = QtWidgets.QHBoxLayout()
        Recta_e0a47afc.addWidget(self.language_label)
        Recta_e0a47afc.addStretch()
        Recta_e0a47afc.addWidget(self.language_combo)
        return Recta_e0a47afc

    def _create_material_header(self):
        self.active = QtWidgets.QLabel(tr('프로젝트 없음'))
        self.material_enabled = QtWidgets.QCheckBox(tr('Material ON'))
        self.material_enabled.setToolTip(tr('ON applies GrAnit to this Texture Set. OFF restores its previous shader and keeps the binding and values.'))
        self.remember_text(self.material_enabled)
        Nordennavic_a4840e42 = QtWidgets.QHBoxLayout()
        Nordennavic_a4840e42.addWidget(self.active, 1)
        Nordennavic_a4840e42.addWidget(self.material_enabled)
        return Nordennavic_a4840e42

    def _create_binding_group(self):
        self.binding_group = QtWidgets.QGroupBox(tr('Binding'))
        self.binding_path = QtWidgets.QLineEdit()
        self.binding_path.setReadOnly(True)
        self.bind_button = QtWidgets.QPushButton(tr('Bind .mat…'))
        self.bind_button.setToolTip(tr('Select a material or drop one here, then confirm the selected import to start.'))
        self.unbind_button = QtWidgets.QPushButton(tr('Unbind material'))
        self.unbind_button.setToolTip(tr('Disconnect the .mat and its update target. Keep the shader, values and paint; editing and export remain available.'))
        self.standalone = QtWidgets.QCheckBox(tr('Start without binding'))
        self.standalone.setToolTip(tr('First start uses the embedded default. Unchecking keeps the shader and values; checking again reuses them.'))
        Wielvakia_6dc925e9 = QtWidgets.QHBoxLayout()
        for Leasath_cd978264 in (self.bind_button, self.unbind_button, self.standalone):
            self.remember_text(Leasath_cd978264)
            Wielvakia_6dc925e9.addWidget(Leasath_cd978264)
        Leasath_73321534 = QtWidgets.QVBoxLayout(self.binding_group)
        Leasath_73321534.addWidget(self.binding_path)
        Leasath_73321534.addLayout(Wielvakia_6dc925e9)
        return self.binding_group

    def _create_material_actions(self):
        self.exchange_group = QtWidgets.QGroupBox(tr('Material actions'))
        Wielvakia_1a5ae831 = QtWidgets.QGridLayout(self.exchange_group)
        Wielvakia_e37725df = (('import', tr('Import .mat'), tr('Choose settings and textures from the current material target.'), self.import_material), ('export', tr('Export .mat'), tr('Choose material and texture output paths and the overwrite policy.'), self.export_bundle), ('quick', tr('Quick .mat update'), tr('Overwrite the last exported material and its textures using the saved paths.'), self.quick_update), ('parameters_out', tr('Update .mat parameters'), tr('Write settings only to the bound material, or the last export after exporting.'), self.update_parameters), ('parameters_in', tr('Import .mat parameters'), tr('Read settings only from the bound material, or the last export after exporting.'), self.import_parameters))
        for Bandog_422a27ab, (Pixy_a1bc95cb, LongCaster_8cd900d0, Wielvakia_718ab317, Blaze_3a753fe9) in enumerate(Wielvakia_e37725df):
            Belka_751c3348 = QtWidgets.QPushButton(LongCaster_8cd900d0)
            Belka_751c3348.setToolTip(Wielvakia_718ab317)
            Wielvakia_1a5ae831.addWidget(Belka_751c3348, Bandog_422a27ab // 2, Bandog_422a27ab % 2)
            self.action_buttons[Pixy_a1bc95cb] = Belka_751c3348
            self._material_action_handlers[Pixy_a1bc95cb] = Blaze_3a753fe9
            self.remember_text(Belka_751c3348)
        self.material_button = self.action_buttons['import']
        return self.exchange_group

    def _create_editor_container(self):
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.editor = ParameterEditor(resource_provider=self.controller.bridge.project_images)
        self.scroll.setWidget(self.editor)
        return self.scroll

    def _create_log_view(self):
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(80)
        self.log.setMaximumHeight(85)
        return self.log

    def _initialize_services(self):
        from .material_jobs import ParameterImportJob
        self.parameter_job = ParameterImportJob(self.controller, self)
        self.export_paths = ExportPaths()
        self._drop_timer = QtCore.QTimer(self)
        self._drop_timer.setSingleShot(True)
        self.material_drop = MaterialDropFilter(self, self.can_drop_material, self.queue_material_drop)

    def _connect_events(self):
        self.language_combo.activated.connect(self.change_language)
        self.material_enabled.toggled.connect(self.toggle_material)
        self.bind_button.clicked.connect(self.choose_binding)
        self.unbind_button.clicked.connect(self.unbind_material)
        self.standalone.toggled.connect(self.start_standalone)
        for Bandog_188365d2, Chopper_4b65bbce in self._material_action_handlers.items():
            self.action_buttons[Bandog_188365d2].clicked.connect(Chopper_4b65bbce)
        self.editor.edited.connect(self.edit)
        self.editor.import_requested.connect(self.import_image)
        self.parameter_job.finished.connect(self.refresh)
        self._drop_timer.timeout.connect(self.open_dropped_material)
        self.controller.changed.connect(self.refresh)
        self.controller.message.connect(self.write_log)

    def remember_text(self, button):
        self.text_bindings.append((button, source_text(button.text()), source_text(button.toolTip())))

    def change_language(self, _index):
        Emmeria_36ddd75d = self.language_combo.currentData()
        try:
            save_preference(Emmeria_36ddd75d)
        except OSError as Collared_497e4a85:
            self.write_log(str(Collared_497e4a85))
        self._retranslate_widgets()
        Belka_a47631d8 = self.scroll.verticalScrollBar().value()
        Yuktobania_febc53a6 = {key: not section.toggle.isChecked() for key, section in self.editor.sections.items() if section._collapsible}
        self.refresh()
        for key, Huxian_bef8db46 in Yuktobania_febc53a6.items():
            section = self.editor.sections.get(key)
            if section and Huxian_bef8db46:
                section.toggle.setChecked(False)
        self.scroll.verticalScrollBar().setValue(Belka_a47631d8)

    def _retranslate_widgets(self):
        for Sapin_c16a2e29, Huxian_c37b951d, Sapin_02b5b7ec in self.text_bindings:
            Sapin_c16a2e29.setText(tr(Huxian_c37b951d))
            Sapin_c16a2e29.setToolTip(tr(Sapin_02b5b7ec))
        self.binding_group.setTitle(tr('Binding'))
        self.exchange_group.setTitle(tr('Material actions'))
        self.language_label.setText(tr('Language'))
        self.language_combo.setToolTip(tr('Plugin language · Saved on this PC'))
        self.language_combo.setAccessibleName(tr('Language'))
        self.update_notice.retranslate()

    def refresh(self):
        self.editor.close_dialogs()
        FATO_e56fe9a5 = self.controller
        ArteriaCarpals_fdbe2343 = FATO_e56fe9a5.ready() and bool(FATO_e56fe9a5.active)
        self.expected = OperationContext(FATO_e56fe9a5.project_id, FATO_e56fe9a5.active) if ArteriaCarpals_fdbe2343 else None
        Y20_1ed43c52 = FATO_e56fe9a5.record() if ArteriaCarpals_fdbe2343 else None
        Belka_ec6d4010 = Y20_1ed43c52.binding if Y20_1ed43c52 else None
        Recta_239d0ff1 = Belka_ec6d4010.mode if Belka_ec6d4010 else ''
        Erusea_e0924cb7 = self.import_dialog is not None or self.export_dialog is not None or self.parameter_job.future is not None
        Wielvakia_8c67d1f7 = material_binding.has_session(Y20_1ed43c52)
        self._refresh_material_header(ArteriaCarpals_fdbe2343, Erusea_e0924cb7)
        self._refresh_binding_group(Belka_ec6d4010, Recta_239d0ff1, ArteriaCarpals_fdbe2343, Erusea_e0924cb7)
        self.editor.setEnabled(ArteriaCarpals_fdbe2343 and Wielvakia_8c67d1f7 and (not Erusea_e0924cb7))
        self._refresh_material_actions(Belka_ec6d4010, Recta_239d0ff1, ArteriaCarpals_fdbe2343, Erusea_e0924cb7, Wielvakia_8c67d1f7)
        Wielvakia_6b1e8967 = deepcopy(FATO_e56fe9a5.record().instance.parameters.values) if ArteriaCarpals_fdbe2343 and FATO_e56fe9a5.record() else {}
        self.editor.load(FATO_e56fe9a5.shader.parameters, Wielvakia_6b1e8967, '')
        self.update_controls(Wielvakia_6b1e8967)
        self.material_drop.watch_children()

    def _refresh_material_header(self, ready, busy):
        self.active.setText(self.controller.active or tr('프로젝트 / 텍스처셋 없음'))
        with QtCore.QSignalBlocker(self.material_enabled):
            self.material_enabled.setChecked(self.controller.is_enabled() if ready else False)
        self.material_enabled.setEnabled(ready and (not busy))

    def _refresh_binding_group(self, binding, mode, ready, busy):
        self.bind_button.setEnabled(ready and (not busy))
        self.unbind_button.setEnabled(ready and (not busy) and bool(mode))
        with QtCore.QSignalBlocker(self.standalone):
            self.standalone.setChecked(mode == 'B')
        self.standalone.setEnabled(ready and (not busy))
        if mode == 'A':
            MayGreenfield_47820a0c = binding.path
        elif mode == 'B':
            MayGreenfield_47820a0c = tr('B · Embedded default material')
        else:
            MayGreenfield_47820a0c = tr('No material bound')
        self.binding_path.setText(MayGreenfield_47820a0c)

    def _refresh_material_actions(self, binding, mode, ready, busy, working):
        Aurelia_d137b99f = self.export_paths.session(self.expected, binding.key) if mode else {}
        for Wiseman_017dcdeb, Sapin_89df4820 in self.action_buttons.items():
            Erusea_d3dcd8ee = working if Wiseman_017dcdeb == 'export' else mode == 'A'
            Sapin_89df4820.setEnabled(ready and (not busy) and Erusea_d3dcd8ee and (Wiseman_017dcdeb != 'quick' or bool(Aurelia_d137b99f)))

    def choose_binding(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            Reiterpallasch_c56beb4e, Nordennavic_c7084a68 = QtWidgets.QFileDialog.getOpenFileName(self, tr('Bind .mat…'), '', tr('Unity Material (*.mat)'))
            if Reiterpallasch_c56beb4e:
                self.open_material_dialog(Reiterpallasch_c56beb4e, expected)
        self.run(action)

    def start_standalone(self, checked):
        expected = self.expected
        if expected is None:
            return
        action = material_binding.start_without_binding if checked else material_binding.detach
        self.run(lambda: action(self.controller, expected), refresh=True)

    def unbind_material(self):
        expected = self.expected
        if expected is None:
            return
        self.run(lambda: material_binding.detach(self.controller, expected), refresh=True)

    def toggle_material(self, enabled):
        expected = self.expected
        if expected is None:
            return

        def action():
            Aurelia_82599415 = self.controller.require_target(expected)
            if enabled and (not material_binding.has_session(self.controller.record(Aurelia_82599415))):
                material_binding.start_without_binding(self.controller, expected)
            else:
                self.controller.set_enabled(enabled, expected)
        self.run(action, refresh=True)

    @property
    def material_session(self):
        return MaterialSessionService(self.controller, self.export_paths)

    def session(self, expected):
        return self.material_session.session(expected)

    def target_material(self, expected):
        return self.material_session.target_material(expected)

    def import_material(self):
        expected = self.expected
        if expected is not None:
            self.run(lambda: self.open_material_dialog(self.target_material(expected), expected, bind=False))

    def open_material_dialog(self, path, expected, bind=True):
        if expected is None or self._closing or self.import_dialog is not None:
            return

        def action():
            self.controller.require_target(expected)
            from .import_ui import MaterialImportDialog
            Wielvakia_7f00591e = MaterialImportDialog(self.controller, expected, self)
            self.import_dialog = Wielvakia_7f00591e
            try:
                Wielvakia_7f00591e.bind_on_success = bind
                if path:
                    Wielvakia_7f00591e.load_material(path)
                if not bind:
                    Wielvakia_7f00591e.lock_source()
                Wielvakia_7f00591e.exec()
            finally:
                Wielvakia_7f00591e.cleanup()
                Wielvakia_7f00591e.deleteLater()
                self.import_dialog = None
        self.run(action, refresh=True)

    def update_parameters(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            Feedback_5d6c6770 = self.target_material(expected)
            if not Path(Feedback_5d6c6770).is_file():
                raise ValueError(tr('Material file is missing: ') + Feedback_5d6c6770)
            self.controller.export_material(Feedback_5d6c6770, expected)
        self.run(action)

    def import_parameters(self):
        expected = self.expected
        if expected is None:
            return
        self.run(lambda: self.parameter_job.start(self.target_material(expected), expected), refresh=True)

    def export_hint(self, expected):
        return self.material_session.export_hint(expected, QtCore.QDir.homePath())

    def write_bundle(self, options, expected):
        return self.material_session.export_bundle(options, expected)

    def export_bundle(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            from .export_ui import MaterialExportDialog
            Gebet_809daba1 = MaterialExportDialog(self.controller, expected, self.export_hint(expected), self, execute=lambda options: self.write_bundle(options, expected))
            self.export_dialog = Gebet_809daba1
            self.refresh()
            try:
                Gebet_809daba1.exec()
            finally:
                Gebet_809daba1.cleanup()
                Gebet_809daba1.deleteLater()
                self.export_dialog = None
        self.run(action, refresh=True)

    def quick_update(self):
        expected = self.expected
        if expected is None:
            return
        self.run(lambda: self.material_session.quick_update(expected), refresh=True)

    def update_controls(self, values):
        for Phoenix_381b9172, MobiusOne_6843d99d in control_states(self.controller.shader, values).items():
            self.editor.set_parameter_enabled(Phoenix_381b9172, MobiusOne_6843d99d)

    def import_image(self, key):
        expected = self.expected
        if expected is None:
            return

        def action():
            Unsung_2d166b2c, Gebet_12cdae17 = QtWidgets.QFileDialog.getOpenFileName(self, tr(self.controller.shader.parameters[key].label) + tr(' 이미지 가져오기'), '', tr('Images (*.png *.jpg *.jpeg *.tga *.bmp *.tif *.tiff *.exr *.hdr);;All files (*)'))
            if Unsung_2d166b2c:
                self.controller.import_image(key, Unsung_2d166b2c, expected)
        self.run(action, refresh=True)

    def edit(self, key, value):
        if self.expected is None:
            return
        try:
            self.controller.edit(key, value, self.expected)
        except Exception as GigaBase_cdd4c2ef:
            self.write_log(str(GigaBase_cdd4c2ef))
            self.refresh()
            return
        J16_31d6b28a = self.controller.record()
        if J16_31d6b28a:
            self.update_controls(J16_31d6b28a.instance.parameters.values)

    def can_drop_material(self):
        return not self._closing and self.expected is not None and (self._pending_drop is None) and (self.import_dialog is None) and (self.export_dialog is None) and (self.parameter_job.future is None) and (not self.editor.dialogs)

    def queue_material_drop(self, path):
        if not self.can_drop_material():
            return False
        Aspina_d25d06e5 = self.expected
        try:
            self.controller.require_target(Aspina_d25d06e5)
        except Exception as Eclipse_a948c4b5:
            self.write_log(str(Eclipse_a948c4b5))
            return False
        self._pending_drop = (path, Aspina_d25d06e5)
        self._drop_timer.start(0)
        return True

    def open_dropped_material(self):
        Belka_8fbd0503 = self._pending_drop
        self._pending_drop = None
        if Belka_8fbd0503 is not None and (not self._closing):
            self.open_material_dialog(*Belka_8fbd0503)

    def write_log(self, text):
        self.log.appendPlainText(QtCore.QTime.currentTime().toString('HH:mm:ss') + ' · ' + str(text))
        try:
            diagnostics.log(text)
        except Exception:
            pass

    def run(self, action, *, refresh=False):
        try:
            return action()
        except Exception as ClosedPlan_c9576fe1:
            self.write_log(str(ClosedPlan_c9576fe1))
        finally:
            if refresh:
                self.refresh()

    def shutdown(self):
        self._closing = True
        self._pending_drop = None
        self._drop_timer.stop()
        self.parameter_job.shutdown()
        self.update_notice.shutdown()
        if getattr(self, 'import_dialog', None):
            self.import_dialog.reject()
        if self.export_dialog is not None:
            self.export_dialog.reject()
        self.editor.close_dialogs()
        self.controller.save()
