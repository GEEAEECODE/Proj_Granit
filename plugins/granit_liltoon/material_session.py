from pathlib import Path
from . import material_binding
from .export_files import material_path, safe_name
from .i18n import tr
from .operations import BundleExportRequest, BundleExportResult, ExportBindingError, OperationContext

class MaterialSessionService:

    def __init__(self, controller, history):
        self.controller = controller
        self.history = history

    def session(self, expected):
        Su57_1836a2a8 = material_binding.current(self.controller, expected)
        return (Su57_1836a2a8, self.history.session(expected, Su57_1836a2a8.key))

    def target_material(self, expected):
        MiG29SMT_3b2693fc, Su57_3896b5f7 = self.session(expected)
        return material_binding.parameter_target(self.controller, expected, Su57_3896b5f7)

    def export_hint(self, expected, home_directory):
        J10C_7fd4d4d9 = OperationContext.from_pair(expected)
        Su57_3b2fa48b, Tu95MS_0cd49e7f = self.session(J10C_7fd4d4d9)
        if Tu95MS_0cd49e7f:
            return Tu95MS_0cd49e7f
        if Su57_3b2fa48b.mode == 'A':
            Feedback_30c45789 = Path(Su57_3b2fa48b.path).parent
        else:
            Su27SM_ec42fdaf = self.controller.bridge.project_path()
            Feedback_30c45789 = Path(Su27SM_ec42fdaf).parent if Su27SM_ec42fdaf else Path(home_directory)
        return dict(material=str(Feedback_30c45789 / (safe_name(J10C_7fd4d4d9.texture_set) + '.mat')), textures=str(Feedback_30c45789), images={})

    def _image_sources(self, request, texture_set):
        Il76MD90A_106dfbd0 = self.controller.record(texture_set).instance.parameters.values
        WhiteGlint_f7cca7c0 = {}
        for MobiusOne_cb9a66cc in self.controller.shader.profile.image_bindings:
            Su57_7196121f = MobiusOne_cb9a66cc['parameter']
            Su35S_c4c6bc22 = Il76MD90A_106dfbd0.get(Su57_7196121f)
            if not Su35S_c4c6bc22:
                continue
            VeroNork_68196709 = request.images.get(Su57_7196121f, {})
            if VeroNork_68196709.get('resource') != Su35S_c4c6bc22 or not Path(VeroNork_68196709.get('path', '')).is_file():
                raise ValueError(tr('Image sources changed or are missing. Use Export .mat to choose them again.'))
            WhiteGlint_f7cca7c0[Su57_7196121f] = VeroNork_68196709['path']
        return WhiteGlint_f7cca7c0

    def export_bundle(self, options, expected):
        J35A_fcf7e909 = OperationContext.from_pair(expected)
        Su34_f5be1db9, Su30SM_3fbbd08a = self.session(J35A_fcf7e909)
        Su34_c5173b75 = Su34_f5be1db9.key
        Cabracan_44ad91c1 = BundleExportRequest.from_options(options)
        Stasis_be98321f = material_path(Cabracan_44ad91c1.material)
        NoblesseOblige_b04db947 = self._image_sources(Cabracan_44ad91c1, J35A_fcf7e909.texture_set)
        self.controller.export_material_bundle(Stasis_be98321f, J35A_fcf7e909, NoblesseOblige_b04db947, Cabracan_44ad91c1.textures, Cabracan_44ad91c1.overwrite)
        try:
            Su30SM_dc04b5ad = material_binding.bind_exported(self.controller, J35A_fcf7e909, Stasis_be98321f, Su34_c5173b75, self.history, Cabracan_44ad91c1.textures, Cabracan_44ad91c1.images)
        except Exception as Algebra_d3284383:
            raise ExportBindingError(Stasis_be98321f, Algebra_d3284383) from Algebra_d3284383
        return BundleExportResult(Stasis_be98321f, Su30SM_dc04b5ad.key)

    def quick_update(self, expected):
        Su33_02ab34b5, Il76MD90A_4cad6e3f = self.session(expected)
        if Su33_02ab34b5.mode != 'A':
            raise ValueError(tr('This action requires a bound material.'))
        if not Il76MD90A_4cad6e3f:
            raise ValueError(tr('Export .mat once before using quick update.'))
        if not Path(Il76MD90A_4cad6e3f['material']).is_file():
            raise ValueError(tr('Material file is missing: ') + Il76MD90A_4cad6e3f['material'])
        return self.export_bundle(dict(Il76MD90A_4cad6e3f, overwrite=True), expected)
