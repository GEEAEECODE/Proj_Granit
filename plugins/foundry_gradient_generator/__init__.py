__version__ = '0.2.6'
_panel = None
_dock = None
_events = []
_show_action = None

def show_window():
    if _dock is None:
        return
    from PySide6 import QtGui
    if _dock.isFloating():
        screens = QtGui.QGuiApplication.screens()
        if screens and (not any((s.availableGeometry().intersects(_dock.frameGeometry()) for s in screens))):
            bounds = screens[0].availableGeometry()
            _dock.move(bounds.left() + 40, bounds.top() + 40)
    _dock.show()
    _dock.raise_()
    _dock.activateWindow()

def start_plugin():
    global _panel, _dock, _show_action
    if _panel is not None:
        show_window()
        return
    from PySide6 import QtCore, QtGui
    import substance_painter.ui as ui
    import substance_painter.event as event
    from .painter import PainterAssets
    from .painter_shaders import PainterShaders
    from .controller import ShaderController
    from .manager_ui import ShaderManagerPanel
    try:
        controller = ShaderController(PainterShaders(PainterAssets()))
        _panel = ShaderManagerPanel(controller)
        controller.setParent(_panel)
        modes = ui.UIMode.Edition | ui.UIMode.Visualisation | ui.UIMode.Baking
        _dock = ui.add_dock_widget(_panel, ui_modes=modes)
        _dock.setWindowTitle('GrAnit-Shader')
        _dock.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, False)
        _show_action = QtGui.QAction('GrAnit-Shader', _dock)
        _show_action.setObjectName('FoundryGradientGeneratorShow')
        _show_action.triggered.connect(show_window)
        ui.add_action(ui.ApplicationMenu.Window, _show_action)
        for event_type, callback in ((event.ProjectEditionEntered, controller.load_project), (event.ProjectAboutToClose, project_closing), (event.ProjectAboutToSave, project_saving), (event.LayerStacksModelDataChanged, controller.sync_active_texture_set)):
            event.DISPATCHER.connect(event_type, callback)
            _events.append((event_type, callback))
        show_window()
        controller.load_project()
    except Exception:
        close_plugin()
        raise

def project_saving(_event=None):
    if _panel is not None:
        controller = _panel.controller
        if controller.loaded and controller.bridge.ready():
            try:
                controller.save()
            except Exception as exc:
                _panel.write_log(str(exc))

def project_closing(_event=None):
    if _panel is not None:
        _panel.gradient.close_editors()
        project_saving()
        _panel.controller.clear_project()

def close_plugin():
    global _panel, _dock, _show_action
    import substance_painter.ui as ui
    import substance_painter.event as event
    if _panel is not None:
        _panel.shutdown()
    try:
        for event_type, callback in _events:
            event.DISPATCHER.disconnect(event_type, callback)
    finally:
        _events.clear()
        try:
            if _show_action is not None:
                ui.delete_ui_element(_show_action)
            if _dock is not None:
                ui.delete_ui_element(_dock)
            elif _panel is not None:
                _panel.deleteLater()
        finally:
            _panel, _dock = (None, None)
            _show_action = None

def reload_plugin():
    import importlib
    import sys
    for name in ('gradient', 'presets', 'sources', 'models', 'definitions', 'painter', 'diagnostics', 'painter_shaders', 'jobs', 'controller', 'color_picker', 'ui', 'parameter_ui', 'manager_ui'):
        module = sys.modules.get(f'{__name__}.{name}')
        if module is not None:
            importlib.reload(module)
