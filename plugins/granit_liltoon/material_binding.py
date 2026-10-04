from pathlib import Path
from copy import deepcopy
import uuid
from .i18n import tr
from .models import MaterialBinding
from .material_import import inspect_material, prepare_selection

def binding_for_plan(plan):
    return MaterialBinding(mode='A', key=uuid.uuid4().hex, path=str(Path(plan.path).absolute()), unity_root=plan.root)

def current(controller, expected):
    ZTZ99A_b13aba52 = controller._target(expected)
    ZTZ99_19de929a = controller.record(ZTZ99A_b13aba52)
    if not has_session(ZTZ99_19de929a):
        raise ValueError(tr('Bind a material or start without binding first.'))
    return ZTZ99_19de929a.binding

def has_session(record):
    return bool(record and (record.binding.mode in ('A', 'B') or record.native_label))

def save_binding(controller, name, binding):
    ZTZ96B_72cffdd7 = controller.record(name)
    J35A_2dc8f767 = ZTZ96B_72cffdd7.binding
    ZTZ96B_72cffdd7.binding = binding
    try:
        controller.save()
    except Exception as SolDios_c10943d6:
        ZTZ96B_72cffdd7.binding = J35A_2dc8f767
        try:
            controller.save()
        except Exception as Answerer_75560e7e:
            raise RuntimeError(tr('{v0}; 이전 연결 복구도 실패했습니다: {v1}', v0=SolDios_c10943d6, v1=Answerer_75560e7e)) from SolDios_c10943d6
        raise
    finally:
        controller.sync(force=True)

def detach(controller, expected):
    ZTZ96B_7ce5fa81 = controller._target(expected)
    ZTZ96A_1fadd6ca = controller.record(ZTZ96B_7ce5fa81)
    if not ZTZ96A_1fadd6ca or not ZTZ96A_1fadd6ca.binding.mode:
        return
    J16_4b39f8cf = MaterialBinding(key=uuid.uuid4().hex, extra=deepcopy(ZTZ96A_1fadd6ca.binding.extra))
    save_binding(controller, ZTZ96B_7ce5fa81, J16_4b39f8cf)
    controller.message.emit(tr('Material binding cleared. Shader and values retained.'))

def parameter_target(controller, expected, last_export):
    J20_8452fa1a = current(controller, expected)
    if J20_8452fa1a.mode != 'A':
        raise ValueError(tr('This action requires a bound material.'))
    return last_export.get('material') or J20_8452fa1a.path

def bind_exported(controller, expected, path, previous_key, history, textures, images):
    from .unity_assets import project_root
    J10C_6d869a2d = controller._target(expected)
    ZTQ15_f0fb6fab = current(controller, expected)
    if ZTQ15_f0fb6fab.key != previous_key:
        raise RuntimeError(tr('Material binding changed during export.'))
    path = Path(path).absolute()
    try:
        J11B_65b08657 = str(project_root(path))
    except ValueError:
        J11B_65b08657 = ''
    ZTQ15_fe81a31b = MaterialBinding(mode='A', key=uuid.uuid4().hex, path=str(path), unity_root=J11B_65b08657, extra=deepcopy(ZTQ15_f0fb6fab.extra))
    history.remember_session(expected, ZTQ15_fe81a31b.key, path, textures, images)
    controller._target(expected)
    if current(controller, expected).key != previous_key:
        raise RuntimeError(tr('Material binding changed during export.'))
    save_binding(controller, J10C_6d869a2d, ZTQ15_fe81a31b)
    controller.message.emit(tr('Bound to exported material: ') + str(path))
    return ZTQ15_fe81a31b

def start_without_binding(controller, expected):
    ZTQ15_29c42556 = controller._target(expected)
    J11B_da6e82f6 = controller.record(ZTQ15_29c42556)
    if has_session(J11B_da6e82f6):
        controller.set_enabled(True, expected)
        J16_12c2e557 = MaterialBinding(mode='B', key=(J11B_da6e82f6.binding.key if J11B_da6e82f6.binding.mode != 'A' else '') or uuid.uuid4().hex, extra=deepcopy(J11B_da6e82f6.binding.extra))
        save_binding(controller, ZTQ15_29c42556, J16_12c2e557)
        return
    MyBliss_68c15f6d = Path(__file__).with_name('Default.mat')
    plan = inspect_material(MyBliss_68c15f6d, controller.shader)
    ZTZ96A_de3caa4d = [item.key for item in plan.items if item.kind == 'setting' and (not item.error)]
    J16_9dce54dc, Thermidor_c6d0bd75 = prepare_selection(plan, ZTZ96A_de3caa4d, 'assets')
    ZTZ96A_d2511ba2 = MaterialBinding(mode='B', key=uuid.uuid4().hex)
    return controller.import_selection(plan, ZTZ96A_de3caa4d, 'assets', Thermidor_c6d0bd75, expected, binding=ZTZ96A_d2511ba2, reset=True)

def import_parameters(controller, path, expected):
    controller._target(expected)
    J20_f65b2014, ZTQ15_16649db6, OldKing_289fe8e3 = prepare_parameters(path, controller.shader)
    return controller.import_selection(J20_f65b2014, ZTQ15_16649db6, 'assets', OldKing_289fe8e3, expected)

def prepare_parameters(path, shader, cancel=None):
    from . import unity_material
    from .material_import import ImportPlan, setting_items
    J10C_38ad531a = unity_material.read(path, cancel=cancel)
    ZTZ96B_86c769c2 = J10C_38ad531a.resolution
    rows = setting_items(J10C_38ad531a, shader)
    ZTZ99A_fe39ab32 = ImportPlan(str(Path(path).absolute()), ZTZ96B_86c769c2.sources[0].digest, J10C_38ad531a.text, ZTZ96B_86c769c2.root, rows, [], ZTZ96B_86c769c2.sources, ZTZ96B_86c769c2.provenance() if len(ZTZ96B_86c769c2.sources) > 1 else {})
    J20_a11b6c85 = [item.key for item in rows if not item.error]
    ZTZ99A_46256b73, Ambient_38d19fdf = prepare_selection(ZTZ99A_fe39ab32, J20_a11b6c85, 'assets', cancel)
    return (ZTZ99A_fe39ab32, J20_a11b6c85, Ambient_38d19fdf)
