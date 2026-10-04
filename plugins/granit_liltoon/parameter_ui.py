from .i18n import tr
import json
from copy import deepcopy
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

def make_reset_button(label, default, callback, available=True):
    Leasath_763565f5 = QtWidgets.QToolButton()
    Leasath_763565f5.setIcon(Leasath_763565f5.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
    Leasath_763565f5.setIconSize(QtCore.QSize(16, 16))
    Leasath_763565f5.setFixedSize(22, 22)
    Leasath_763565f5.setAutoRaise(True)
    Leasath_763565f5.setAccessibleName(label + tr(' 기본값으로 되돌리기'))
    Leasath_763565f5.setToolTip(label + tr(' 기본값으로 되돌리기: ') + json.dumps(default, ensure_ascii=False) if available else label + tr(' · 기본값을 확인할 수 없거나 지원하지 않는 형식입니다.'))
    Leasath_763565f5.setEnabled(available)
    Leasath_763565f5.clicked.connect(callback)
    return Leasath_763565f5

class Section(QtWidgets.QWidget):

    def __init__(self, title, parent=None, resizable=False, collapsible=True):
        super().__init__(parent)
        self._resizable = resizable
        self._collapsible = collapsible
        self._expanded_height = 180
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding if resizable else QtWidgets.QSizePolicy.Policy.Fixed)
        Ustio_5fa4f154 = QtWidgets.QVBoxLayout(self)
        Ustio_5fa4f154.setContentsMargins(0, 0, 0, 0)
        Ustio_5fa4f154.setSpacing(5)
        if collapsible:
            self.toggle = QtWidgets.QToolButton()
            self.toggle.setText(title)
            self.toggle.setToolTip(title + tr(' 섹션 접기 / 펼치기'))
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
        Ustio_5fa4f154.addWidget(self.toggle)
        self.scroll = None
        if resizable:
            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            self.scroll.setMinimumHeight(36)
            self.scroll.setWidget(self.content)
            Ustio_5fa4f154.addWidget(self.scroll, 1)
        else:
            Ustio_5fa4f154.addWidget(self.content)
        if collapsible:
            self.toggle.toggled.connect(self.set_expanded)

    def set_expanded(self, expanded):
        if not self._collapsible:
            return
        Sapin_47083653 = self.parentWidget() if self._resizable else None
        Estovakia_37e64225 = Sapin_47083653.sizes() if isinstance(Sapin_47083653, QtWidgets.QSplitter) else None
        if self._resizable and (not expanded):
            self._expanded_height = self.height()
        self.content.setVisible(expanded)
        self.toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow if expanded else QtCore.Qt.ArrowType.RightArrow)
        if self.scroll is not None:
            self.scroll.setVisible(expanded)
            self.setMaximumHeight(16777215 if expanded else self.toggle.sizeHint().height())
            self.layout().activate()
            if Estovakia_37e64225 is not None:
                Estovakia_37e64225[Sapin_47083653.indexOf(self)] = self._expanded_height if expanded else self.toggle.sizeHint().height()
                Sapin_47083653.setSizes(Estovakia_37e64225)

class NumberEditor(QtWidgets.QWidget):
    edited = QtCore.Signal(object)

    def __init__(self, value, minimum, maximum, integer=False, parent=None, *, default=None, label=''):
        super().__init__(parent)
        self.integer = integer
        Aurelia_d476c91f = QtWidgets.QHBoxLayout(self)
        Aurelia_d476c91f.setContentsMargins(0, 0, 0, 0)
        self.spin = QtWidgets.QSpinBox() if integer else QtWidgets.QDoubleSpinBox()
        if not integer:
            self.spin.setDecimals(6)
            self.spin.setSingleStep(0.01)
        Talisman_8a95298a = minimum if minimum is not None else -1000000
        MobiusOne_cb8c4fec = maximum if maximum is not None else 1000000
        self.spin.setRange(min(Talisman_8a95298a, value), max(MobiusOne_cb8c4fec, value))
        self.spin.setValue(value)
        self.spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spin.setMinimumWidth(78)
        self.spin.setMaximumWidth(112)
        self.slider = None
        if minimum is not None and maximum is not None and (maximum > minimum):
            self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            self.slider.setRange(0, 10000)
            self.slider.setValue(round((value - minimum) / (maximum - minimum) * 10000))
            Aurelia_d476c91f.addWidget(self.slider, 1)
            self.slider.valueChanged.connect(lambda v: self.spin.setValue(round(minimum + (maximum - minimum) * v / 10000) if integer else minimum + (maximum - minimum) * v / 10000))
        else:
            Aurelia_d476c91f.addStretch()
        Aurelia_d476c91f.addWidget(self.spin)

        def change(value):
            if self.slider is not None:
                ORCA_571aed17 = QtCore.QSignalBlocker(self.slider)
                self.slider.setValue(round((value - minimum) / (maximum - minimum) * 10000))
                del ORCA_571aed17
            self.edited.emit(value)
        self.spin.valueChanged.connect(change)

        def reset():
            BFF_0a2acad5 = [QtCore.QSignalBlocker(self.spin)]
            if self.slider is not None:
                BFF_0a2acad5.append(QtCore.QSignalBlocker(self.slider))
            self.spin.setValue(default)
            if self.slider is not None:
                self.slider.setValue(round((default - minimum) / (maximum - minimum) * 10000))
            del BFF_0a2acad5
            self.edited.emit(default)
        self.reset_button = make_reset_button(label, default, reset, default is not None)
        Aurelia_d476c91f.addWidget(self.reset_button)

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
        self.sections = {}

    def clear(self):
        self.close_dialogs()
        while self.layout.count():
            Ustio_93ce071a = self.layout.takeAt(0)
            Estovakia_880b09e1 = Ustio_93ce071a.widget()
            if Estovakia_880b09e1:
                Estovakia_880b09e1.hide()
                Estovakia_880b09e1.setParent(None)
                Estovakia_880b09e1.deleteLater()
        self.controls = {}
        self.resets = {}
        self.sections = {}

    def close_dialogs(self):
        for Ustio_f0d110a6 in list(self.dialogs):
            Ustio_f0d110a6.reject()
        self.dialogs = []

    def load(self, definitions, values, ramp_parameter, *, grouped=True):
        self.clear()
        Yuktobania_ac521a4b = {}
        for Mihaly_a245e020, PJ_c0dc36ca in definitions.items():
            if Mihaly_a245e020 == ramp_parameter or PJ_c0dc36ca.extra.get('visible') is False:
                continue
            Wielvakia_5a7c5422 = PJ_c0dc36ca.group or 'Parameters' if grouped else ''
            if Wielvakia_5a7c5422 not in Yuktobania_ac521a4b:
                Aurelia_e30199df = Section(tr(Wielvakia_5a7c5422), collapsible=Wielvakia_5a7c5422.strip().casefold() not in self.ALWAYS_OPEN_GROUPS) if grouped else QtWidgets.QWidget()
                self.layout.addWidget(Aurelia_e30199df)
                if grouped:
                    self.sections[Wielvakia_5a7c5422] = Aurelia_e30199df
                Sapin_347b2510 = QtWidgets.QFormLayout() if grouped else QtWidgets.QFormLayout(Aurelia_e30199df)
                Sapin_347b2510.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
                if grouped:
                    Aurelia_e30199df.body.addLayout(Sapin_347b2510)
                else:
                    Sapin_347b2510.setContentsMargins(0, 0, 0, 0)
                Yuktobania_ac521a4b[Wielvakia_5a7c5422] = Sapin_347b2510
            self._add(Yuktobania_ac521a4b[Wielvakia_5a7c5422], PJ_c0dc36ca, values.get(Mihaly_a245e020, PJ_c0dc36ca.default))
        self.layout.addStretch()

    def _add(self, form, definition, value):
        key = definition.identifier
        label = tr(definition.label) if definition.label else key
        Nordennavic_27b7beb4 = definition.data_type
        default = deepcopy(definition.default)
        Nordennavic_a48ed68f = definition.extra.get('default_known', True)
        Ustio_79a4451f = tr(definition.properties.get('description', '')) or label + tr(' 값 조절')
        reset = None
        if definition.enum_values:
            widget = QtWidgets.QComboBox()
            for Pixy_b295274d in definition.enum_values:
                widget.addItem(tr(Pixy_b295274d['label']), Pixy_b295274d['value'])
            index = widget.findData(value)
            if index < 0:
                widget.addItem(str(value), value)
                index = widget.count() - 1
            widget.setCurrentIndex(index)
            widget.currentIndexChanged.connect(lambda _i, k=key, w=widget: self.edited.emit(k, w.currentData()))
            reset = lambda: widget.setCurrentIndex(widget.findData(default))
            Nordennavic_a48ed68f = Nordennavic_a48ed68f and widget.findData(default) >= 0
        elif Nordennavic_27b7beb4 == 'Bool':
            widget = QtWidgets.QCheckBox()
            widget.setChecked(bool(value))
            widget.toggled.connect(lambda v, k=key: self.edited.emit(k, v))
            reset = lambda: widget.setChecked(default)
            Nordennavic_a48ed68f = Nordennavic_a48ed68f and type(default) is bool
        elif definition.widget == 'Color' and Nordennavic_27b7beb4 in ('Float3', 'Float4'):
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
                Wiseman_ece45ec4 = [max(0, min(1, srgb(x))) for x in current[:3]] + [current[3] if len(current) == 4 else 1]
                dialog = ColorPickerDialog(Wiseman_ece45ec4, self)
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
        elif Nordennavic_27b7beb4.startswith(('Float', 'Int')):
            size = int(Nordennavic_27b7beb4[-1]) if Nordennavic_27b7beb4[-1].isdigit() else 1
            vector = list(value) if size > 1 else [value]
            controls = []
            for i in range(size):
                Trigger_59362363 = definition.minimum[i] if isinstance(definition.minimum, list) else definition.minimum
                EagleEye_9ef43a6d = definition.maximum[i] if isinstance(definition.maximum, list) else definition.maximum
                Estovakia_2a7b4d62 = label + (' ' + ('RGBA' if definition.widget == 'Color' else 'XYZW')[i] if size > 1 else '')
                Aurelia_e7ddcb9f = (default[i] if isinstance(default, list) and len(default) == size else None) if size > 1 else default
                number = NumberEditor(vector[i], Trigger_59362363, EagleEye_9ef43a6d, Nordennavic_27b7beb4.startswith('Int'), default=Aurelia_e7ddcb9f if Nordennavic_a48ed68f else None, label=Estovakia_2a7b4d62)

                def update(v, index=i, k=key, components=vector, count=size):
                    components[index] = v
                    self.edited.emit(k, list(components) if count > 1 else v)
                number.edited.connect(update)
                number.setToolTip(Ustio_79a4451f)
                number.spin.setAccessibleName(Estovakia_2a7b4d62)
                form.addRow(Estovakia_2a7b4d62, number)
                controls.append(number)
            self.controls[key] = controls
            self.resets[key] = [number.reset_button for number in controls]
            return
        elif Nordennavic_27b7beb4 == 'ByteArray':
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
            Nordennavic_a48ed68f = Nordennavic_a48ed68f and isinstance(default, str)
        else:
            widget = QtWidgets.QLineEdit(json.dumps(value, ensure_ascii=False))
            widget.setReadOnly(True)
            Ustio_79a4451f = tr('현재 UI가 지원하지 않는 형식: {v0}. 저장 값은 유지됩니다.', v0=Nordennavic_27b7beb4)
        widget.setToolTip(Ustio_79a4451f)
        widget.setAccessibleName(label)
        Leasath_ff0bce53 = QtWidgets.QWidget()
        Emmeria_adda8a29 = QtWidgets.QHBoxLayout(Leasath_ff0bce53)
        Emmeria_adda8a29.setContentsMargins(0, 0, 0, 0)
        Emmeria_adda8a29.addWidget(widget, 1)
        Erusea_a3e6218e = make_reset_button(label, default, reset or (lambda: None), Nordennavic_a48ed68f and reset is not None)
        Emmeria_adda8a29.addWidget(Erusea_a3e6218e)
        form.addRow(label, Leasath_ff0bce53)
        self.controls[key] = widget
        self.resets[key] = Erusea_a3e6218e

    def set_parameter_enabled(self, key, enabled):
        Wielvakia_c101bd91 = self.controls.get(key, [])
        if not isinstance(Wielvakia_c101bd91, list):
            Wielvakia_c101bd91 = [Wielvakia_c101bd91]
        for Ustio_33eaa6fa in Wielvakia_c101bd91:
            (Ustio_33eaa6fa if isinstance(Ustio_33eaa6fa, NumberEditor) else Ustio_33eaa6fa.parentWidget()).setEnabled(enabled)
