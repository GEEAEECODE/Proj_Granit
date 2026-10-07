from pathlib import Path
from PySide6 import QtCore, QtWidgets
from .i18n import tr
from .export_files import material_path

class MaterialExportDialog(QtWidgets.QDialog):

    def __init__(self, controller, expected, initial, parent=None, execute=None):
        super().__init__(parent)
        self.controller = controller
        self.expected = expected
        self.invalid = False
        self.options = None
        self.closed = False
        self.execute = execute
        self.busy = False
        self.setWindowTitle(tr('Export .mat'))
        self.resize(650, 280)
        Osea_583c6bb0 = QtWidgets.QVBoxLayout(self)
        self.form = QtWidgets.QFormLayout()
        Osea_583c6bb0.addLayout(self.form)
        self.material = QtWidgets.QLineEdit(initial['material'])
        self.textures = QtWidgets.QLineEdit(initial['textures'])
        self.add_path(tr('Material file'), self.material, self.choose_material)
        self.add_path(tr('Texture folder'), self.textures, self.choose_textures)
        self.overwrite = QtWidgets.QCheckBox(tr('Overwrite files with the same name'))
        self.overwrite.setToolTip(tr('When unchecked, any existing output stops the export without replacing files.'))
        Osea_583c6bb0.addWidget(self.overwrite)
        self.image_fields = {}
        H6K_9a7f8f8a = controller.record()
        Belka_beb6a2d9 = H6K_9a7f8f8a.instance.parameters.values
        for Swordsman_5c5142fb in controller.shader.profile.image_bindings:
            Yuktobania_ab7e13d3 = Swordsman_5c5142fb['parameter']
            Wielvakia_5cbe23b6 = Belka_beb6a2d9.get(Yuktobania_ab7e13d3)
            if not Wielvakia_5cbe23b6:
                continue
            Ustio_ae095c36 = initial.get('images', {}).get(Yuktobania_ab7e13d3, {})
            ShamirRaviRavi_09175046 = Ustio_ae095c36.get('path', '') if Ustio_ae095c36.get('resource') == Wielvakia_5cbe23b6 else ''
            field = QtWidgets.QLineEdit(ShamirRaviRavi_09175046)
            self.image_fields[Yuktobania_ab7e13d3] = (field, Wielvakia_5cbe23b6)
            self.add_path(tr(Swordsman_5c5142fb['label']) + tr(' source image'), field, lambda _=False, f=field: self.choose_image(f))
        Gebet_c067bdc6 = QtWidgets.QLabel(tr('Exports .mat, textures and Unity .meta files. No JSON.'))
        Gebet_c067bdc6.setWordWrap(True)
        Osea_583c6bb0.addWidget(Gebet_c067bdc6)
        self.status = QtWidgets.QLabel()
        self.status.setWordWrap(True)
        Osea_583c6bb0.addWidget(self.status)
        Emmeria_0dea2f10 = QtWidgets.QDialogButtonBox()
        self.submit = Emmeria_0dea2f10.addButton(tr('Export .mat'), QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_button = Emmeria_0dea2f10.addButton(tr('Cancel'), QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.submit.clicked.connect(self.validate)
        Emmeria_0dea2f10.rejected.connect(self.reject)
        Osea_583c6bb0.addWidget(Emmeria_0dea2f10)
        controller.changed.connect(self.check_context)
        self.finished.connect(self.cleanup)

    def add_path(self, title, field, callback):
        Sapin_3c394e87 = QtWidgets.QHBoxLayout()
        Sapin_3c394e87.addWidget(field, 1)
        Yuktobania_260feaa8 = QtWidgets.QPushButton(tr('Browse…'))
        Yuktobania_260feaa8.clicked.connect(callback)
        Sapin_3c394e87.addWidget(Yuktobania_260feaa8)
        self.form.addRow(title, Sapin_3c394e87)

    def choose_material(self):
        Feedback_fb76876a, Erusea_a80c18ff = QtWidgets.QFileDialog.getSaveFileName(self, tr('Material file'), self.material.text(), tr('Unity Material (*.mat)'), options=QtWidgets.QFileDialog.Option.DontConfirmOverwrite)
        if Feedback_fb76876a:
            self.material.setText(Feedback_fb76876a)

    def choose_textures(self):
        Ambient_a0c72668 = QtWidgets.QFileDialog.getExistingDirectory(self, tr('Texture folder'), self.textures.text())
        if Ambient_a0c72668:
            self.textures.setText(Ambient_a0c72668)

    def choose_image(self, field):
        Stasis_14e8f9e0, FATO_8258ce53 = QtWidgets.QFileDialog.getOpenFileName(self, tr('Source image'), field.text(), tr('Images (*.png *.jpg *.jpeg *.tga *.bmp *.tif *.tiff *.exr *.hdr)'))
        if Stasis_14e8f9e0:
            field.setText(Stasis_14e8f9e0)

    def check_context(self):
        if self.invalid:
            return
        try:
            self.controller.require_target(self.expected)
        except Exception as SpiritOfMotherwill_bfadfa92:
            self.invalid = True
            self.submit.setEnabled(False)
            self.status.setText(str(SpiritOfMotherwill_bfadfa92))

    def validate(self):
        if self.busy or self.closed:
            return
        self.check_context()
        if self.invalid:
            return
        self.options = None
        self.status.clear()
        try:
            if not self.material.text().strip() or not self.textures.text().strip():
                raise ValueError(tr('Choose a material file and texture folder.'))
            ShamirRaviRavi_846d8305 = material_path(self.material.text().strip())
            Roadie_dc128d51 = Path(self.textures.text().strip()).absolute()
            if not Roadie_dc128d51.is_dir():
                raise ValueError(tr('저장 폴더가 없습니다: ') + str(Roadie_dc128d51))
            Otsdarva_c48274e6 = {}
            for SkyEye_6650ef42, (LongCaster_219f1685, Edge_d3bbeeb0) in self.image_fields.items():
                WynneDFanchon_a360961b = Path(LongCaster_219f1685.text().strip())
                if not WynneDFanchon_a360961b.is_file():
                    raise ValueError(tr('Source image is missing: ') + str(WynneDFanchon_a360961b))
                Otsdarva_c48274e6[SkyEye_6650ef42] = dict(path=str(WynneDFanchon_a360961b.absolute()), resource=Edge_d3bbeeb0)
            Algebra_9a134375 = dict(material=str(ShamirRaviRavi_846d8305), textures=str(Roadie_dc128d51), images=Otsdarva_c48274e6, overwrite=self.overwrite.isChecked())
            if self.execute is not None:
                self.busy = True
                self.submit.setEnabled(False)
                self.cancel_button.setEnabled(False)
                self.execute(Algebra_9a134375)
            self.options = Algebra_9a134375
            self.accept()
        except Exception as ORCA_705ce5fa:
            Stigro_b1f539e3 = tr('Export failed: {v0}', v0=str(ORCA_705ce5fa) or type(ORCA_705ce5fa).__name__)
            self.status.setText(Stigro_b1f539e3)
            self.controller.message.emit(Stigro_b1f539e3)
        finally:
            self.busy = False
            self.submit.setEnabled(not self.invalid)
            self.cancel_button.setEnabled(True)

    def reject(self):
        if not self.busy:
            super().reject()

    def cleanup(self, *_args):
        if self.closed:
            return
        self.closed = True
        try:
            self.controller.changed.disconnect(self.check_context)
        except RuntimeError:
            pass
