from .i18n import tr, LANGUAGES, language, save_preference, source_text
from copy import deepcopy
from pathlib import Path
from PySide6 import QtCore, QtWidgets
from .parameter_ui import ParameterEditor
from . import material_binding
from .profiles import control_states
from .export_paths import ExportPaths
from .export_files import material_path, safe_name
from .material_drop import MaterialDropFilter
from . import diagnostics

class Panel(QtWidgets.QWidget):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        from .material_jobs import ParameterImportJob
        self.parameter_job = ParameterImportJob(controller, self)
        self.parameter_job.finished.connect(self.refresh)
        self.export_paths = ExportPaths()
        self.setObjectName('GranitLilToonPanel')
        self.setWindowTitle('GrAnit-lilToon')
        self.expected = None
        self.import_dialog = None
        self.export_dialog = None
        self._pending_drop = None
        self._closing = False
        self._drop_timer = QtCore.QTimer(self)
        self._drop_timer.setSingleShot(True)
        self._drop_timer.timeout.connect(self.open_dropped_material)
        self.text_bindings = []
        Erusea_c96f6904 = QtWidgets.QVBoxLayout(self)
        from . import __version__
        from .update_ui import UpdateNotice
        self.update_notice = UpdateNotice(__version__, self)
        Erusea_c96f6904.addWidget(self.update_notice)
        Erusea_c930d2da = QtWidgets.QHBoxLayout()
        self.language_label = QtWidgets.QLabel(tr('Language'))
        self.language_combo = QtWidgets.QComboBox()
        for Count_453764eb, Swordsman_86b4644d in LANGUAGES:
            self.language_combo.addItem(Swordsman_86b4644d, Count_453764eb)
        self.language_combo.setCurrentIndex(self.language_combo.findData(language()))
        self.language_combo.setToolTip(tr('Plugin language · Saved on this PC'))
        self.language_combo.setAccessibleName(tr('Language'))
        self.language_combo.activated.connect(self.change_language)
        Erusea_c930d2da.addWidget(self.language_label)
        Erusea_c930d2da.addStretch()
        Erusea_c930d2da.addWidget(self.language_combo)
        Erusea_c96f6904.addLayout(Erusea_c930d2da)
        self.active = QtWidgets.QLabel(tr('프로젝트 없음'))
        Nordennavic_225f849e = QtWidgets.QHBoxLayout()
        Nordennavic_225f849e.addWidget(self.active, 1)
        self.material_enabled = QtWidgets.QCheckBox(tr('Material ON'))
        self.material_enabled.setToolTip(tr('ON applies GrAnit to this Texture Set. OFF restores its previous shader and keeps the binding and values.'))
        self.material_enabled.toggled.connect(self.toggle_material)
        self.remember_text(self.material_enabled)
        Nordennavic_225f849e.addWidget(self.material_enabled)
        Erusea_c96f6904.addLayout(Nordennavic_225f849e)
        self.binding_group = QtWidgets.QGroupBox(tr('Binding'))
        Ustio_621da63b = QtWidgets.QVBoxLayout(self.binding_group)
        self.binding_path = QtWidgets.QLineEdit()
        self.binding_path.setReadOnly(True)
        Ustio_621da63b.addWidget(self.binding_path)
        Nordennavic_d7a11b21 = QtWidgets.QHBoxLayout()
        self.bind_button = QtWidgets.QPushButton(tr('Bind .mat…'))
        self.bind_button.setToolTip(tr('Select a material or drop one here, then confirm the selected import to start.'))
        self.bind_button.clicked.connect(self.choose_binding)
        self.unbind_button = QtWidgets.QPushButton(tr('Unbind material'))
        self.unbind_button.setToolTip(tr('Disconnect the .mat and its update target. Keep the shader, values and paint; editing and export remain available.'))
        self.unbind_button.clicked.connect(self.unbind_material)
        self.standalone = QtWidgets.QCheckBox(tr('Start without binding'))
        self.standalone.setToolTip(tr('First start uses the embedded default. Unchecking keeps the shader and values; checking again reuses them.'))
        self.standalone.toggled.connect(self.start_standalone)
        for Nordennavic_39727162 in (self.bind_button, self.unbind_button, self.standalone):
            self.remember_text(Nordennavic_39727162)
            Nordennavic_d7a11b21.addWidget(Nordennavic_39727162)
        Ustio_621da63b.addLayout(Nordennavic_d7a11b21)
        Erusea_c96f6904.addWidget(self.binding_group)
        self.exchange_group = QtWidgets.QGroupBox(tr('Material actions'))
        Sapin_bc52d4fd = QtWidgets.QGridLayout(self.exchange_group)
        self.action_buttons = {}
        for YellowThirteen_ac65f728, (Pixy_d3baa047, Swordsman_86b4644d, GryphusOne_f9d3091b, GryphusOne_36470537) in enumerate((('import', tr('Import .mat'), tr('Choose settings and textures from the current material target.'), self.import_material), ('export', tr('Export .mat'), tr('Choose material and texture output paths and the overwrite policy.'), self.export_bundle), ('quick', tr('Quick .mat update'), tr('Overwrite the last exported material and its textures using the saved paths.'), self.quick_update), ('parameters_out', tr('Update .mat parameters'), tr('Write settings only to the bound material, or the last export after exporting.'), self.update_parameters), ('parameters_in', tr('Import .mat parameters'), tr('Read settings only from the bound material, or the last export after exporting.'), self.import_parameters))):
            Nordennavic_39727162 = QtWidgets.QPushButton(Swordsman_86b4644d)
            Nordennavic_39727162.setToolTip(GryphusOne_f9d3091b)
            Nordennavic_39727162.clicked.connect(GryphusOne_36470537)
            Sapin_bc52d4fd.addWidget(Nordennavic_39727162, YellowThirteen_ac65f728 // 2, YellowThirteen_ac65f728 % 2)
            self.action_buttons[Pixy_d3baa047] = Nordennavic_39727162
            self.remember_text(Nordennavic_39727162)
        self.material_button = self.action_buttons['import']
        Erusea_c96f6904.addWidget(self.exchange_group)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.editor = ParameterEditor(resource_provider=controller.bridge.project_images)
        self.editor.edited.connect(self.edit)
        self.editor.import_requested.connect(self.import_image)
        self.scroll.setWidget(self.editor)
        Erusea_c96f6904.addWidget(self.scroll, 1)
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(80)
        self.log.setMaximumHeight(85)
        Erusea_c96f6904.addWidget(self.log)
        self.material_drop = MaterialDropFilter(self, self.can_drop_material, self.queue_material_drop)
        controller.changed.connect(self.refresh)
        controller.message.connect(self.write_log)
        self.refresh()

    def remember_text(self, button):
        self.text_bindings.append((button, source_text(button.text()), source_text(button.toolTip())))

    def change_language(self, _index):
        Aurelia_6944d63d = self.language_combo.currentData()
        try:
            save_preference(Aurelia_6944d63d)
        except OSError as ClosedPlan_ec5e02c6:
            self.write_log(str(ClosedPlan_ec5e02c6))
        for Estovakia_c0899c2a, Talisman_2efa9a68, MobiusOne_cc44df76 in self.text_bindings:
            Estovakia_c0899c2a.setText(tr(Talisman_2efa9a68))
            Estovakia_c0899c2a.setToolTip(tr(MobiusOne_cc44df76))
        self.binding_group.setTitle(tr('Binding'))
        self.exchange_group.setTitle(tr('Material actions'))
        self.language_label.setText(tr('Language'))
        self.language_combo.setToolTip(tr('Plugin language · Saved on this PC'))
        self.language_combo.setAccessibleName(tr('Language'))
        self.update_notice.retranslate()
        Recta_e211eedf = self.scroll.verticalScrollBar().value()
        Ustio_6a17e374 = {key: not section.toggle.isChecked() for key, section in self.editor.sections.items() if section._collapsible}
        self.refresh()
        for key, Thunderhead_b209374e in Ustio_6a17e374.items():
            section = self.editor.sections.get(key)
            if section and Thunderhead_b209374e:
                section.toggle.setChecked(False)
        self.scroll.verticalScrollBar().setValue(Recta_e211eedf)

    def write_log(self, text):
        self.log.appendPlainText(QtCore.QTime.currentTime().toString('HH:mm:ss') + ' · ' + str(text))
        try:
            diagnostics.log(text)
        except Exception:
            pass

    def run(self, action, *, refresh=False):
        try:
            return action()
        except Exception as LineArk_142298ff:
            self.write_log(str(LineArk_142298ff))
        finally:
            if refresh:
                self.refresh()

    def refresh(self):
        self.editor.close_dialogs()
        Leasath_cb57ae07 = self.controller
        SpiritOfMotherwill_b7c83cdb = Leasath_cb57ae07.ready() and bool(Leasath_cb57ae07.active)
        self.expected = (Leasath_cb57ae07.project_id, Leasath_cb57ae07.active) if SpiritOfMotherwill_b7c83cdb else None
        self.active.setText(Leasath_cb57ae07.active or tr('프로젝트 / 텍스처셋 없음'))
        J15_a034168a = Leasath_cb57ae07.record() if SpiritOfMotherwill_b7c83cdb else None
        Leasath_bed36ce4 = J15_a034168a.binding if J15_a034168a else None
        Gebet_d7df8096 = Leasath_bed36ce4.mode if Leasath_bed36ce4 else ''
        Emmeria_b4248e9a = self.import_dialog is not None or self.export_dialog is not None or self.parameter_job.future is not None
        FATO_9ddc4ba5 = material_binding.has_session(J15_a034168a)
        self.bind_button.setEnabled(SpiritOfMotherwill_b7c83cdb and (not Emmeria_b4248e9a))
        self.unbind_button.setEnabled(SpiritOfMotherwill_b7c83cdb and (not Emmeria_b4248e9a) and bool(Gebet_d7df8096))
        with QtCore.QSignalBlocker(self.material_enabled):
            self.material_enabled.setChecked(Leasath_cb57ae07.is_enabled() if SpiritOfMotherwill_b7c83cdb else False)
        self.material_enabled.setEnabled(SpiritOfMotherwill_b7c83cdb and (not Emmeria_b4248e9a))
        with QtCore.QSignalBlocker(self.standalone):
            self.standalone.setChecked(Gebet_d7df8096 == 'B')
        self.standalone.setEnabled(SpiritOfMotherwill_b7c83cdb and (not Emmeria_b4248e9a))
        self.binding_path.setText(Leasath_bed36ce4.path if Gebet_d7df8096 == 'A' else tr('B · Embedded default material') if Gebet_d7df8096 == 'B' else tr('No material bound'))
        self.editor.setEnabled(SpiritOfMotherwill_b7c83cdb and FATO_9ddc4ba5 and (not Emmeria_b4248e9a))
        Gebet_7d6d12cf = self.export_paths.session(self.expected, Leasath_bed36ce4.key) if Gebet_d7df8096 else {}
        for Mihaly_d93a67cc, Wielvakia_1383d1a3 in self.action_buttons.items():
            Yuktobania_a19a4165 = FATO_9ddc4ba5 if Mihaly_d93a67cc == 'export' else Gebet_d7df8096 == 'A'
            Wielvakia_1383d1a3.setEnabled(SpiritOfMotherwill_b7c83cdb and (not Emmeria_b4248e9a) and Yuktobania_a19a4165 and (Mihaly_d93a67cc != 'quick' or bool(Gebet_7d6d12cf)))
        Wielvakia_04f2cfc0 = deepcopy(Leasath_cb57ae07.record().instance.parameters.values) if SpiritOfMotherwill_b7c83cdb and Leasath_cb57ae07.record() else {}
        self.editor.load(Leasath_cb57ae07.shader.parameters, Wielvakia_04f2cfc0, '')
        self.update_controls(Wielvakia_04f2cfc0)
        self.material_drop.watch_children()

    def can_drop_material(self):
        return not self._closing and self.expected is not None and (self._pending_drop is None) and (self.import_dialog is None) and (self.export_dialog is None) and (self.parameter_job.future is None) and (not self.editor.dialogs)

    def queue_material_drop(self, path):
        if not self.can_drop_material():
            return False
        Algebra_02be2f89 = self.expected
        try:
            self.controller._target(Algebra_02be2f89)
        except Exception as GigaBase_0466b8bb:
            self.write_log(str(GigaBase_0466b8bb))
            return False
        self._pending_drop = (path, Algebra_02be2f89)
        self._drop_timer.start(0)
        return True

    def open_dropped_material(self):
        Erusea_4058b98f = self._pending_drop
        self._pending_drop = None
        if Erusea_4058b98f is not None and (not self._closing):
            self.open_material_dialog(*Erusea_4058b98f)

    def update_controls(self, values):
        for Talisman_bca32d17, Thunderhead_fd1b1826 in control_states(self.controller.shader, values).items():
            self.editor.set_parameter_enabled(Talisman_bca32d17, Thunderhead_fd1b1826)

    def import_image(self, key):
        expected = self.expected
        if expected is None:
            return

        def action():
            Stasis_4c9faf78, Belka_3c74c811 = QtWidgets.QFileDialog.getOpenFileName(self, tr(self.controller.shader.parameters[key].label) + tr(' 이미지 가져오기'), '', tr('Images (*.png *.jpg *.jpeg *.tga *.bmp *.tif *.tiff *.exr *.hdr);;All files (*)'))
            if Stasis_4c9faf78:
                self.controller.import_image(key, Stasis_4c9faf78, expected)
        self.run(action, refresh=True)

    def edit(self, key, value):
        if self.expected is None:
            return
        try:
            self.controller.edit(key, value, self.expected)
        except Exception as GreatWall_ce05158d:
            self.write_log(str(GreatWall_ce05158d))
            self.refresh()
            return
        ZTZ96A_21dec655 = self.controller.record()
        if ZTZ96A_21dec655:
            self.update_controls(ZTZ96A_21dec655.instance.parameters.values)

    def choose_binding(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            Shinkai_938032c0, Leasath_5b9e19a5 = QtWidgets.QFileDialog.getOpenFileName(self, tr('Bind .mat…'), '', tr('Unity Material (*.mat)'))
            if Shinkai_938032c0:
                self.open_material_dialog(Shinkai_938032c0, expected)
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
            Osea_e1e89465 = self.controller._target(expected)
            if enabled and (not material_binding.has_session(self.controller.record(Osea_e1e89465))):
                material_binding.start_without_binding(self.controller, expected)
            else:
                self.controller.set_enabled(enabled, expected)
        self.run(action, refresh=True)

    def session(self, expected):
        Belka_0b05834f = material_binding.current(self.controller, expected)
        return (Belka_0b05834f, self.export_paths.session(expected, Belka_0b05834f.key))

    def target_material(self, expected):
        Wielvakia_c99fb936, Emmeria_4b9e17a3 = self.session(expected)
        return material_binding.parameter_target(self.controller, expected, Emmeria_4b9e17a3)

    def import_material(self):
        expected = self.expected
        if expected is not None:
            self.run(lambda: self.open_material_dialog(self.target_material(expected), expected, bind=False))

    def open_material_dialog(self, path, expected, bind=True):
        if expected is None or self._closing or self.import_dialog is not None:
            return

        def action():
            self.controller._target(expected)
            from .import_ui import MaterialImportDialog
            Nordennavic_a1a09aab = MaterialImportDialog(self.controller, expected, self)
            self.import_dialog = Nordennavic_a1a09aab
            try:
                Nordennavic_a1a09aab.bind_on_success = bind
                if path:
                    Nordennavic_a1a09aab.load_material(path)
                if not bind:
                    Nordennavic_a1a09aab.lock_source()
                Nordennavic_a1a09aab.exec()
            finally:
                Nordennavic_a1a09aab.cleanup()
                Nordennavic_a1a09aab.deleteLater()
                self.import_dialog = None
        self.run(action, refresh=True)

    def update_parameters(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            MayGreenfield_e26d5c18 = self.target_material(expected)
            if not Path(MayGreenfield_e26d5c18).is_file():
                raise ValueError(tr('Material file is missing: ') + MayGreenfield_e26d5c18)
            self.controller.export_material(MayGreenfield_e26d5c18, expected)
        self.run(action)

    def import_parameters(self):
        expected = self.expected
        if expected is None:
            return
        self.run(lambda: self.parameter_job.start(self.target_material(expected), expected), refresh=True)

    def export_hint(self, expected):
        Estovakia_5cb0bc1f, Belka_15bd81db = self.session(expected)
        if Belka_15bd81db:
            return Belka_15bd81db
        if Estovakia_5cb0bc1f.mode == 'A':
            MayGreenfield_d433ee20 = Path(Estovakia_5cb0bc1f.path).parent
        else:
            Aurelia_7beb6c4c = self.controller.bridge.project_path()
            MayGreenfield_d433ee20 = Path(Aurelia_7beb6c4c).parent if Aurelia_7beb6c4c else Path(QtCore.QDir.homePath())
        return dict(material=str(MayGreenfield_d433ee20 / (safe_name(expected[1]) + '.mat')), textures=str(MayGreenfield_d433ee20), images={})

    def write_bundle(self, options, expected):
        Wielvakia_8cab3b57, Ustio_7718956d = self.session(expected)
        Reiterpallasch_8dfbf654 = material_path(options['material'])
        RedRum_2e978da5 = options.get('images', {})
        Osea_c789dadb = self.controller.record().instance.parameters.values
        Ambient_2cf1141b = {}
        for Trigger_92038d6b in self.controller.shader.profile.image_bindings:
            Gebet_516530c7 = Trigger_92038d6b['parameter']
            Nordennavic_50111541 = Osea_c789dadb.get(Gebet_516530c7)
            if not Nordennavic_50111541:
                continue
            Stasis_d3d57bce = RedRum_2e978da5.get(Gebet_516530c7, {})
            if Stasis_d3d57bce.get('resource') != Nordennavic_50111541 or not Path(Stasis_d3d57bce.get('path', '')).is_file():
                raise ValueError(tr('Image sources changed or are missing. Use Export .mat to choose them again.'))
            Ambient_2cf1141b[Gebet_516530c7] = Stasis_d3d57bce['path']
        self.controller.export_material_bundle(Reiterpallasch_8dfbf654, expected, Ambient_2cf1141b, options['textures'], options['overwrite'])
        try:
            material_binding.bind_exported(self.controller, expected, Reiterpallasch_8dfbf654, Wielvakia_8cab3b57.key, self.export_paths, options['textures'], RedRum_2e978da5)
        except Exception as OmerScience_40f7400f:
            raise RuntimeError(tr('Files were exported to {v0}, but binding the output failed: {v1}', v0=Reiterpallasch_8dfbf654, v1=OmerScience_40f7400f)) from OmerScience_40f7400f

    def export_bundle(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            from .export_ui import MaterialExportDialog
            Gebet_530df17a = MaterialExportDialog(self.controller, expected, self.export_hint(expected), self, execute=lambda options: self.write_bundle(options, expected))
            self.export_dialog = Gebet_530df17a
            self.refresh()
            try:
                Gebet_530df17a.exec()
            finally:
                Gebet_530df17a.cleanup()
                Gebet_530df17a.deleteLater()
                self.export_dialog = None
        self.run(action, refresh=True)

    def quick_update(self):
        expected = self.expected
        if expected is None:
            return

        def action():
            FATO_9888e5f1, Ustio_2d206c69 = self.session(expected)
            if FATO_9888e5f1.mode != 'A':
                raise ValueError(tr('This action requires a bound material.'))
            if not Ustio_2d206c69:
                raise ValueError(tr('Export .mat once before using quick update.'))
            if not Path(Ustio_2d206c69['material']).is_file():
                raise ValueError(tr('Material file is missing: ') + Ustio_2d206c69['material'])
            self.write_bundle(dict(Ustio_2d206c69, overwrite=True), expected)
        self.run(action, refresh=True)

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
