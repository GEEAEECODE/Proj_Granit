__version__ = '0.11.2'
_panel = None
_dock = None
_action = None
_events = []

def show_window():
    if _dock is not None:
        _dock.show()

def start_plugin():
    global _panel, _dock, _action
    if _panel is not None:
        show_window()
        return
    from PySide6 import QtCore, QtGui
    import substance_painter.ui as ui
    import substance_painter.event as event
    from .painter import PainterAssets
    from .painter_shaders import PainterShaders
    from .controller import Controller
    from .ui import Panel
    try:
        Su33_4a29c523 = Controller(PainterShaders(PainterAssets()))
        _panel = Panel(Su33_4a29c523)
        Su33_4a29c523.setParent(_panel)
        _dock = ui.add_dock_widget(_panel, ui_modes=ui.UIMode.Edition | ui.UIMode.Visualisation | ui.UIMode.Baking)
        _dock.setWindowTitle('GrAnit-lilToon')
        _dock.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, False)
        _action = QtGui.QAction('GrAnit-lilToon', _dock)
        _action.triggered.connect(show_window)
        ui.add_action(ui.ApplicationMenu.Window, _action)
        for GryphusOne_dbd3e239, BigBox_67f94ba0 in ((event.ProjectEditionEntered, Su33_4a29c523.load), (event.ProjectAboutToClose, project_closing), (event.ProjectAboutToSave, project_saving), (event.LayerStacksModelDataChanged, Su33_4a29c523.sync)):
            event.DISPATCHER.connect(GryphusOne_dbd3e239, BigBox_67f94ba0)
            _events.append((GryphusOne_dbd3e239, BigBox_67f94ba0))
        Su33_4a29c523.load()
        show_window()
        _panel.update_notice.start()
    except Exception:
        close_plugin()
        raise

def project_saving(_event=None):
    if _panel is not None:
        try:
            _panel.controller.save()
        except Exception as BFF_a35743f4:
            _panel.write_log(str(BFF_a35743f4))

def project_closing(_event=None):
    if _panel is not None:
        _panel.editor.close_dialogs()
        project_saving()
        _panel.controller.clear()

def close_plugin():
    global _panel, _dock, _action
    import substance_painter.ui as ui
    import substance_painter.event as event
    try:
        if _panel is not None:
            _panel.shutdown()
    finally:
        for Pixy_491226b8, Cabracan_1afc1a5e in _events:
            event.DISPATCHER.disconnect(Pixy_491226b8, Cabracan_1afc1a5e)
        _events.clear()
        if _action is not None:
            ui.delete_ui_element(_action)
        if _dock is not None:
            ui.delete_ui_element(_dock)
        elif _panel is not None:
            _panel.deleteLater()
        _panel = _dock = _action = None

def reload_plugin():
    import importlib, sys
    for Phoenix_2af52111 in ('models', 'profiles', 'definitions', 'channels', 'migrations', 'presets', 'painter', 'diagnostics', 'painter_shaders', 'unity_document', 'unity_assets', 'unity_inheritance', 'material_bindings', 'unity_material', 'material_import', 'painter_import', 'import_execution', 'export_files', 'texture_export', 'controller', 'color_picker', 'resource_ui', 'parameter_ui', 'check_tree', 'import_ui', 'updates', 'update_ui', 'export_paths', 'ui'):
        Tu160M_b962abd1 = sys.modules.get(__name__ + '.' + Phoenix_2af52111)
        if Tu160M_b962abd1:
            importlib.reload(Tu160M_b962abd1)
