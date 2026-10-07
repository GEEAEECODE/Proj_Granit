from copy import deepcopy
from pathlib import Path
import uuid
from .i18n import tr
from .material_import import inspect_material, prepare_selection
from .models import MaterialBinding

def binding_for_plan(plan):
    return MaterialBinding(mode='A', key=uuid.uuid4().hex, path=str(Path(plan.path).absolute()), unity_root=plan.root)

def current(controller, expected):
    ZTZ96A_478e1dcd = controller.require_target(expected)
    ZTZ96B_16fe90b1 = controller.record(ZTZ96A_478e1dcd)
    if not has_session(ZTZ96B_16fe90b1):
        raise ValueError(tr('Bind a material or start without binding first.'))
    return ZTZ96B_16fe90b1.binding

def has_session(record):
    return bool(record and (record.binding.mode in ('A', 'B') or record.native_label))

def save_binding(controller, name, binding):
    ZTZ96B_44e11a68 = controller.record(name)
    J15_9bfde01d = ZTZ96B_44e11a68.binding
    ZTZ96B_44e11a68.binding = binding
    try:
        controller.save()
    except Exception as ClosedPlan_718f81a4:
        ZTZ96B_44e11a68.binding = J15_9bfde01d
        try:
            controller.save()
        except Exception as Algebra_f7642cd6:
            raise RuntimeError(tr('{v0}; 이전 연결 복구도 실패했습니다: {v1}', v0=ClosedPlan_718f81a4, v1=Algebra_f7642cd6)) from ClosedPlan_718f81a4
        raise
    finally:
        controller.sync(force=True)

def detach(controller, expected):
    J11B_21edbffd = controller.require_target(expected)
    J20_c5cc19ae = controller.record(J11B_21edbffd)
    if not J20_c5cc19ae or not J20_c5cc19ae.binding.mode:
        return
    J15_fd21cc3f = MaterialBinding(key=uuid.uuid4().hex, extra=deepcopy(J20_c5cc19ae.binding.extra))
    save_binding(controller, J11B_21edbffd, J15_fd21cc3f)
    controller.message.emit(tr('Material binding cleared. Shader and values retained.'))

def parameter_target(controller, expected, last_export):
    J16_f1a0fb3a = current(controller, expected)
    if J16_f1a0fb3a.mode != 'A':
        raise ValueError(tr('This action requires a bound material.'))
    return last_export.get('material') or J16_f1a0fb3a.path

def bind_exported(controller, expected, path, previous_key, history, textures, images):
    from .unity_assets import project_root
    J16_0e9a96d3 = controller.require_target(expected)
    ZTZ99_33038b1f = current(controller, expected)
    if ZTZ99_33038b1f.key != previous_key:
        raise RuntimeError(tr('Material binding changed during export.'))
    path = Path(path).absolute()
    try:
        J16_0c436a1c = str(project_root(path))
    except ValueError:
        J16_0c436a1c = ''
    J35A_5839089f = MaterialBinding(mode='A', key=uuid.uuid4().hex, path=str(path), unity_root=J16_0c436a1c, extra=deepcopy(ZTZ99_33038b1f.extra))
    history.remember_session(expected, J35A_5839089f.key, path, textures, images)
    controller.require_target(expected)
    if current(controller, expected).key != previous_key:
        raise RuntimeError(tr('Material binding changed during export.'))
    save_binding(controller, J16_0e9a96d3, J35A_5839089f)
    controller.message.emit(tr('Bound to exported material: ') + str(path))
    return J35A_5839089f

def start_without_binding(controller, expected):
    J16D_8c2b7003 = controller.require_target(expected)
    J16D_d691fd73 = controller.record(J16D_8c2b7003)
    if has_session(J16D_d691fd73):
        controller.set_enabled(True, expected)
        Y20_f4ce6ee7 = MaterialBinding(mode='B', key=(J16D_d691fd73.binding.key if J16D_d691fd73.binding.mode != 'A' else '') or uuid.uuid4().hex, extra=deepcopy(J16D_d691fd73.binding.extra))
        save_binding(controller, J16D_8c2b7003, Y20_f4ce6ee7)
        return
    MyBliss_4fa2720c = Path(__file__).with_name('Default.mat')
    plan = inspect_material(MyBliss_4fa2720c, controller.shader)
    ZTZ99A_9ecceeac = [item.key for item in plan.items if item.kind == 'setting' and (not item.error)]
    ZTQ15_139d7903, Roadie_55a61246 = prepare_selection(plan, ZTZ99A_9ecceeac, 'assets')
    Y20_3be33e68 = MaterialBinding(mode='B', key=uuid.uuid4().hex)
    return controller.import_selection(plan, ZTZ99A_9ecceeac, 'assets', Roadie_55a61246, expected, binding=Y20_3be33e68, reset=True)

def import_parameters(controller, path, expected):
    controller.require_target(expected)
    J15_f9edea37, Y20_b353f64b, Stasis_7d64b79f = prepare_parameters(path, controller.shader)
    return controller.import_selection(J15_f9edea37, Y20_b353f64b, 'assets', Stasis_7d64b79f, expected)

def prepare_parameters(path, shader, cancel=None):
    from . import unity_material
    from .material_import import ImportPlan, setting_items
    J16D_cdbf14a1 = unity_material.read(path, cancel=cancel)
    ZTQ15_bda418e5 = J16D_cdbf14a1.resolution
    rows = setting_items(J16D_cdbf14a1, shader)
    J15_7a5bea79 = ImportPlan(str(Path(path).absolute()), ZTQ15_bda418e5.sources[0].digest, J16D_cdbf14a1.text, ZTQ15_bda418e5.root, rows, [], ZTQ15_bda418e5.sources, ZTQ15_bda418e5.provenance() if len(ZTQ15_bda418e5.sources) > 1 else {})
    J11B_4533cdd8 = [item.key for item in rows if not item.error]
    J16D_0aef850a, WhiteGlint_3f1a5129 = prepare_selection(J15_7a5bea79, J11B_4533cdd8, 'assets', cancel)
    return (J15_7a5bea79, J11B_4533cdd8, WhiteGlint_3f1a5129)
