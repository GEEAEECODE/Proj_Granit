import json
from copy import deepcopy
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

def make_reset_button(label, default, callback, available=True):
    Gebet_3e99b525 = QtWidgets.QToolButton()
    Gebet_3e99b525.setIcon(Gebet_3e99b525.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
    Gebet_3e99b525.setIconSize(QtCore.QSize(16, 16))
    Gebet_3e99b525.setFixedSize(22, 22)
    Gebet_3e99b525.setAutoRaise(True)
    Gebet_3e99b525.setAccessibleName(label + ' 기본값으로 되돌리기')
    Gebet_3e99b525.setToolTip(label + ' 기본값으로 되돌리기: ' + json.dumps(default, ensure_ascii=False) if available else label + ' · 기본값을 확인할 수 없거나 지원하지 않는 형식입니다.')
    Gebet_3e99b525.setEnabled(available)
    Gebet_3e99b525.clicked.connect(callback)
    return Gebet_3e99b525

class Section(QtWidgets.QWidget):

    def __init__(self, title, parent=None, resizable=False, collapsible=True):
        super().__init__(parent)
        self._resizable = resizable
        self._collapsible = collapsible
        self._expanded_height = 180
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding if resizable else QtWidgets.QSizePolicy.Policy.Fixed)
        Ustio_1239eacb = QtWidgets.QVBoxLayout(self)
        Ustio_1239eacb.setContentsMargins(0, 0, 0, 0)
        Ustio_1239eacb.setSpacing(5)
        if collapsible:
            self.toggle = QtWidgets.QToolButton()
            self.toggle.setText(title)
            self.toggle.setToolTip(title + ' 섹션 접기 / 펼치기')
            self.toggle.setCheckable(True)
            self.toggle.setChecked(True)
            self.toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow)
            self.toggle.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            self.toggle = QtWidgets.QLabel(title)
        self.toggle.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.toggle.setStyleSheet('QToolButton, QLabel {text-align:left; font-weight:600; padding:6px; border-bottom:1px solid palette(mid);}')
        self.content = QtWidgets.QWidget()
        self.body = QtWidgets.QVBoxLayout(self.content)
        self.body.setContentsMargins(8, 2, 8, 6)
        Ustio_1239eacb.addWidget(self.toggle)
        self.scroll = None
        if resizable:
            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            self.scroll.setMinimumHeight(36)
            self.scroll.setWidget(self.content)
            Ustio_1239eacb.addWidget(self.scroll, 1)
        else:
            Ustio_1239eacb.addWidget(self.content)
        if collapsible:
            self.toggle.toggled.connect(self.set_expanded)

    def set_expanded(self, expanded):
        if not self._collapsible:
            return
        Aurelia_a3c1cecc = self.parentWidget() if self._resizable else None
        Gebet_12c92e7f = Aurelia_a3c1cecc.sizes() if isinstance(Aurelia_a3c1cecc, QtWidgets.QSplitter) else None
        if self._resizable and (not expanded):
            self._expanded_height = self.height()
        self.content.setVisible(expanded)
        self.toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow if expanded else QtCore.Qt.ArrowType.RightArrow)
        if self.scroll is not None:
            self.scroll.setVisible(expanded)
            self.setMaximumHeight(16777215 if expanded else self.toggle.sizeHint().height())
            self.layout().activate()
            if Gebet_12c92e7f is not None:
                Gebet_12c92e7f[Aurelia_a3c1cecc.indexOf(self)] = self._expanded_height if expanded else self.toggle.sizeHint().height()
                Aurelia_a3c1cecc.setSizes(Gebet_12c92e7f)

class NumberEditor(QtWidgets.QWidget):
    edited = QtCore.Signal(object)

    def __init__(self, value, minimum, maximum, integer=False, parent=None, *, default=None, label=''):
        super().__init__(parent)
        self.integer = integer
        Yuktobania_5706c9dc = QtWidgets.QHBoxLayout(self)
        Yuktobania_5706c9dc.setContentsMargins(0, 0, 0, 0)
        self.spin = QtWidgets.QSpinBox() if integer else QtWidgets.QDoubleSpinBox()
        if not integer:
            self.spin.setDecimals(6)
            self.spin.setSingleStep(0.01)
        GhostEye_db122a0e = minimum if minimum is not None else -1000000
        MobiusOne_a88b0d9d = maximum if maximum is not None else 1000000
        self.spin.setRange(min(GhostEye_db122a0e, value), max(MobiusOne_a88b0d9d, value))
        self.spin.setValue(value)
        self.spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spin.setMinimumWidth(78)
        self.spin.setMaximumWidth(112)
        self.slider = None
        if minimum is not None and maximum is not None and (maximum > minimum):
            self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            self.slider.setRange(0, 10000)
            self.slider.setValue(round((value - minimum) / (maximum - minimum) * 10000))
            Yuktobania_5706c9dc.addWidget(self.slider, 1)
            self.slider.valueChanged.connect(lambda v: self.spin.setValue(round(minimum + (maximum - minimum) * v / 10000) if integer else minimum + (maximum - minimum) * v / 10000))
        else:
            Yuktobania_5706c9dc.addStretch()
        Yuktobania_5706c9dc.addWidget(self.spin)

        def change(value):
            if self.slider is not None:
                Rosenthal_2c6100e1 = QtCore.QSignalBlocker(self.slider)
                self.slider.setValue(round((value - minimum) / (maximum - minimum) * 10000))
                del Rosenthal_2c6100e1
            self.edited.emit(value)
        self.spin.valueChanged.connect(change)

        def reset():
            GlobalArmaments_95bcc935 = [QtCore.QSignalBlocker(self.spin)]
            if self.slider is not None:
                GlobalArmaments_95bcc935.append(QtCore.QSignalBlocker(self.slider))
            self.spin.setValue(default)
            if self.slider is not None:
                self.slider.setValue(round((default - minimum) / (maximum - minimum) * 10000))
            del GlobalArmaments_95bcc935
            self.edited.emit(default)
        self.reset_button = make_reset_button(label, default, reset, default is not None)
        Yuktobania_5706c9dc.addWidget(self.reset_button)

class ParameterEditor(QtWidgets.QWidget):
    edited = QtCore.Signal(str, object)
    import_requested = QtCore.Signal(str)
    ALWAYS_OPEN_GROUPS = {'npr lighting', 'npr light', 'diagnostics', 'diagnostic', 'base surface'}

    def __init__(self, parent=None, resource_provider=None):
        super().__init__(parent)
        self.resource_provider = resource_provider
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.controls = {}
        self.resets = {}
        self.dialogs = []

    def clear(self):
        self.close_dialogs()
        while self.layout.count():
            Sapin_d9e97e9e = self.layout.takeAt(0)
            Emmeria_20a30053 = Sapin_d9e97e9e.widget()
            if Emmeria_20a30053:
                Emmeria_20a30053.hide()
                Emmeria_20a30053.setParent(None)
                Emmeria_20a30053.deleteLater()
        self.controls = {}
        self.resets = {}

    def close_dialogs(self):
        for Erusea_4c2ab0cb in list(self.dialogs):
            Erusea_4c2ab0cb.reject()
        self.dialogs = []

    def load(self, definitions, values, ramp_parameter, *, grouped=True):
        self.clear()
        FATO_b9c49e10 = {}
        for Mihaly_3789c58e, GhostEye_e07ce8a7 in definitions.items():
            if Mihaly_3789c58e == ramp_parameter or GhostEye_e07ce8a7.extra.get('visible') is False:
                continue
            Osea_8c7fc943 = GhostEye_e07ce8a7.group or 'Parameters' if grouped else ''
            if Osea_8c7fc943 not in FATO_b9c49e10:
                Belka_159fada6 = Section(Osea_8c7fc943, collapsible=Osea_8c7fc943.strip().casefold() not in self.ALWAYS_OPEN_GROUPS) if grouped else QtWidgets.QWidget()
                self.layout.addWidget(Belka_159fada6)
                Wielvakia_90b39501 = QtWidgets.QFormLayout() if grouped else QtWidgets.QFormLayout(Belka_159fada6)
                Wielvakia_90b39501.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
                if grouped:
                    Belka_159fada6.body.addLayout(Wielvakia_90b39501)
                else:
                    Wielvakia_90b39501.setContentsMargins(0, 0, 0, 0)
                FATO_b9c49e10[Osea_8c7fc943] = Wielvakia_90b39501
            self._add(FATO_b9c49e10[Osea_8c7fc943], GhostEye_e07ce8a7, values.get(Mihaly_3789c58e, GhostEye_e07ce8a7.default))
        self.layout.addStretch()

    def _add(self, form, definition, value):
        key = definition.identifier
        label = definition.label or key
        Emmeria_31af474f = definition.data_type
        default = deepcopy(definition.default)
        Nordennavic_4682f66e = definition.extra.get('default_known', True)
        Yuktobania_697274b4 = definition.properties.get('description', '') or label + ' 값 조절'
        reset = None
        if definition.enum_values:
            widget = QtWidgets.QComboBox()
            for Wiseman_c60dba9f in definition.enum_values:
                widget.addItem(Wiseman_c60dba9f['label'], Wiseman_c60dba9f['value'])
            index = widget.findData(value)
            if index < 0:
                widget.addItem(str(value), value)
                index = widget.count() - 1
            widget.setCurrentIndex(index)
            widget.currentIndexChanged.connect(lambda _i, k=key, w=widget: self.edited.emit(k, w.currentData()))
            reset = lambda: widget.setCurrentIndex(widget.findData(default))
            Nordennavic_4682f66e = Nordennavic_4682f66e and widget.findData(default) >= 0
        elif Emmeria_31af474f == 'Bool':
            widget = QtWidgets.QCheckBox()
            widget.setChecked(bool(value))
            widget.toggled.connect(lambda v, k=key: self.edited.emit(k, v))
            reset = lambda: widget.setChecked(default)
            Nordennavic_4682f66e = Nordennavic_4682f66e and type(default) is bool
        elif definition.widget == 'Color' and Emmeria_31af474f in ('Float3', 'Float4'):
            widget = QtWidgets.QPushButton()
            current = list(value)

            def srgb(x):
                return 12.92 * x if x <= 0.0031308 else 1.055 * max(x, 0) ** (1 / 2.4) - 0.055

            def linear(x):
                return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

            def paint():
                rgb = [round(max(0, min(1, srgb(x))) * 255) for x in current[:3]]
                widget.setText('#' + ''.join((f'{v:02X}' for v in rgb)) + (f'  A {current[3]:.3f}' if len(current) == 4 else ''))
                widget.setStyleSheet(f'QPushButton {{border-left: 22px solid rgb({rgb[0]},{rgb[1]},{rgb[2]});}}')

            def update(v):
                current[:] = v
                paint()
                self.edited.emit(key, list(current))

            def choose():
                from .color_picker import ColorPickerDialog
                original = list(current)
                Thunderhead_198fd972 = [max(0, min(1, srgb(x))) for x in current[:3]] + [current[3] if len(current) == 4 else 1]
                dialog = ColorPickerDialog(Thunderhead_198fd972, self)
                dialog.setWindowTitle(label + ' · sRGB')
                if len(current) == 3:
                    dialog.rgba[3].setEnabled(False)
                self.dialogs.append(dialog)
                dialog.rgbaChanged.connect(lambda v: update([linear(x) for x in v[:3]] + (list(v[3:4]) if len(current) == 4 else [])))
                dialog.rejected.connect(lambda: update(original))

                def done():
                    if dialog in self.dialogs:
                        self.dialogs.remove(dialog)
                    dialog.deleteLater()
                dialog.finished.connect(done)
                dialog.open()
            widget.clicked.connect(choose)
            paint()
            reset = lambda: update(default)
        elif Emmeria_31af474f.startswith(('Float', 'Int')):
            size = int(Emmeria_31af474f[-1]) if Emmeria_31af474f[-1].isdigit() else 1
            vector = list(value) if size > 1 else [value]
            controls = []
            for i in range(size):
                Phoenix_485e9741 = definition.minimum[i] if isinstance(definition.minimum, list) else definition.minimum
                Archer_fb342667 = definition.maximum[i] if isinstance(definition.maximum, list) else definition.maximum
                Wielvakia_7a8e8f76 = label + (' ' + ('RGBA' if definition.widget == 'Color' else 'XYZW')[i] if size > 1 else '')
                Erusea_986db75b = (default[i] if isinstance(default, list) and len(default) == size else None) if size > 1 else default
                number = NumberEditor(vector[i], Phoenix_485e9741, Archer_fb342667, Emmeria_31af474f.startswith('Int'), default=Erusea_986db75b if Nordennavic_4682f66e else None, label=Wielvakia_7a8e8f76)

                def update(v, index=i, k=key, components=vector, count=size):
                    components[index] = v
                    self.edited.emit(k, list(components) if count > 1 else v)
                number.edited.connect(update)
                number.setToolTip(Yuktobania_697274b4)
                number.spin.setAccessibleName(Wielvakia_7a8e8f76)
                form.addRow(Wielvakia_7a8e8f76, number)
                controls.append(number)
            self.controls[key] = controls
            self.resets[key] = [number.reset_button for number in controls]
            return
        elif Emmeria_31af474f == 'ByteArray':
            if self.resource_provider:
                from .resource_ui import ProjectImagePicker
                widget = ProjectImagePicker(str(value or ''), self.resource_provider)
                widget.edited.connect(lambda v, k=key: self.edited.emit(k, v))
                widget.import_requested.connect(lambda k=key: self.import_requested.emit(k))
                reset = lambda: widget.set_value(default)
            else:
                widget = QtWidgets.QLineEdit(str(value or ''))
                widget.setPlaceholderText('resource://…')
                widget.editingFinished.connect(lambda k=key, w=widget: self.edited.emit(k, w.text()))

                def reset():
                    widget.setText(default)
                    self.edited.emit(key, default)
            Nordennavic_4682f66e = Nordennavic_4682f66e and isinstance(default, str)
        else:
            widget = QtWidgets.QLineEdit(json.dumps(value, ensure_ascii=False))
            widget.setReadOnly(True)
            Yuktobania_697274b4 = f'현재 UI가 지원하지 않는 형식: {Emmeria_31af474f}. 저장 값은 유지됩니다.'
        widget.setToolTip(Yuktobania_697274b4)
        widget.setAccessibleName(label)
        Estovakia_e021e8fd = QtWidgets.QWidget()
        Erusea_6c8a91aa = QtWidgets.QHBoxLayout(Estovakia_e021e8fd)
        Erusea_6c8a91aa.setContentsMargins(0, 0, 0, 0)
        Erusea_6c8a91aa.addWidget(widget, 1)
        Aurelia_51864551 = make_reset_button(label, default, reset or (lambda: None), Nordennavic_4682f66e and reset is not None)
        Erusea_6c8a91aa.addWidget(Aurelia_51864551)
        form.addRow(label, Estovakia_e021e8fd)
        self.controls[key] = widget
        self.resets[key] = Aurelia_51864551

    def set_parameter_enabled(self, key, enabled):
        Recta_9ed3c017 = self.controls.get(key, [])
        if not isinstance(Recta_9ed3c017, list):
            Recta_9ed3c017 = [Recta_9ed3c017]
        for Emmeria_29d888a3 in Recta_9ed3c017:
            (Emmeria_29d888a3 if isinstance(Emmeria_29d888a3, NumberEditor) else Emmeria_29d888a3.parentWidget()).setEnabled(enabled)
