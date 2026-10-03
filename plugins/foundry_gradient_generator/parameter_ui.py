import json
from copy import deepcopy
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

def make_reset_button(label, default, callback, available=True):
    button = QtWidgets.QToolButton()
    button.setIcon(QtGui.QIcon(str(Path(__file__).with_name('icons') / 'refresh.png')))
    button.setIconSize(QtCore.QSize(16, 16))
    button.setFixedSize(22, 22)
    button.setAutoRaise(True)
    button.setAccessibleName(label + ' 기본값으로 되돌리기')
    button.setToolTip(label + ' 기본값으로 되돌리기: ' + json.dumps(default, ensure_ascii=False) if available else label + ' · 기본값을 확인할 수 없거나 지원하지 않는 형식입니다.')
    button.setEnabled(available)
    button.clicked.connect(callback)
    return button

class Section(QtWidgets.QWidget):

    def __init__(self, title, parent=None, resizable=False):
        super().__init__(parent)
        self._resizable = resizable
        self._expanded_height = 180
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding if resizable else QtWidgets.QSizePolicy.Policy.Fixed)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.toggle = QtWidgets.QToolButton()
        self.toggle.setText(title)
        self.toggle.setToolTip(title + ' 섹션 접기 / 펼치기')
        self.toggle.setCheckable(True)
        self.toggle.setChecked(True)
        self.toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow)
        self.toggle.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.toggle.setStyleSheet('QToolButton {text-align:left; font-weight:600; padding:6px; border-bottom:1px solid palette(mid);}')
        self.content = QtWidgets.QWidget()
        self.body = QtWidgets.QVBoxLayout(self.content)
        self.body.setContentsMargins(8, 2, 8, 6)
        layout.addWidget(self.toggle)
        self.scroll = None
        if resizable:
            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            self.scroll.setMinimumHeight(36)
            self.scroll.setWidget(self.content)
            layout.addWidget(self.scroll, 1)
        else:
            layout.addWidget(self.content)
        self.toggle.toggled.connect(self.set_expanded)

    def set_expanded(self, expanded):
        splitter = self.parentWidget() if self._resizable else None
        sizes = splitter.sizes() if isinstance(splitter, QtWidgets.QSplitter) else None
        if self._resizable and (not expanded):
            self._expanded_height = self.height()
        self.content.setVisible(expanded)
        self.toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow if expanded else QtCore.Qt.ArrowType.RightArrow)
        if self.scroll is not None:
            self.scroll.setVisible(expanded)
            self.setMaximumHeight(16777215 if expanded else self.toggle.sizeHint().height())
            self.layout().activate()
            if sizes is not None:
                sizes[splitter.indexOf(self)] = self._expanded_height if expanded else self.toggle.sizeHint().height()
                splitter.setSizes(sizes)

class NumberEditor(QtWidgets.QWidget):
    edited = QtCore.Signal(object)

    def __init__(self, value, minimum, maximum, integer=False, parent=None, *, default=None, label=''):
        super().__init__(parent)
        self.integer = integer
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.spin = QtWidgets.QSpinBox() if integer else QtWidgets.QDoubleSpinBox()
        if not integer:
            self.spin.setDecimals(6)
            self.spin.setSingleStep(0.01)
        lo = minimum if minimum is not None else -1000000
        hi = maximum if maximum is not None else 1000000
        self.spin.setRange(min(lo, value), max(hi, value))
        self.spin.setValue(value)
        self.spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spin.setMinimumWidth(78)
        self.spin.setMaximumWidth(112)
        self.slider = None
        if minimum is not None and maximum is not None and (maximum > minimum):
            self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            self.slider.setRange(0, 10000)
            self.slider.setValue(round((value - minimum) / (maximum - minimum) * 10000))
            layout.addWidget(self.slider, 1)
            self.slider.valueChanged.connect(lambda v: self.spin.setValue(round(minimum + (maximum - minimum) * v / 10000) if integer else minimum + (maximum - minimum) * v / 10000))
        else:
            layout.addStretch()
        layout.addWidget(self.spin)

        def change(value):
            if self.slider is not None:
                blocker = QtCore.QSignalBlocker(self.slider)
                self.slider.setValue(round((value - minimum) / (maximum - minimum) * 10000))
                del blocker
            self.edited.emit(value)
        self.spin.valueChanged.connect(change)

        def reset():
            blockers = [QtCore.QSignalBlocker(self.spin)]
            if self.slider is not None:
                blockers.append(QtCore.QSignalBlocker(self.slider))
            self.spin.setValue(default)
            if self.slider is not None:
                self.slider.setValue(round((default - minimum) / (maximum - minimum) * 10000))
            del blockers
            self.edited.emit(default)
        self.reset_button = make_reset_button(label, default, reset, default is not None)
        layout.addWidget(self.reset_button)

class ParameterEditor(QtWidgets.QWidget):
    edited = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.controls = {}
        self.resets = {}

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        self.controls = {}
        self.resets = {}

    def load(self, definitions, values, ramp_parameter):
        self.clear()
        groups = {}
        for identifier, definition in definitions.items():
            if identifier == ramp_parameter or definition.extra.get('visible') is False:
                continue
            group = definition.group or 'Parameters'
            if group not in groups:
                section = Section(group)
                self.layout.addWidget(section)
                form = QtWidgets.QFormLayout()
                form.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
                section.body.addLayout(form)
                groups[group] = form
            self._add(groups[group], definition, values.get(identifier, definition.default))
        self.layout.addStretch()

    def _add(self, form, definition, value):
        key = definition.identifier
        label = definition.label or key
        kind = definition.data_type
        default = deepcopy(definition.default)
        known = definition.extra.get('default_known', True)
        tooltip = definition.properties.get('description', '') or label + ' 값 조절'
        reset = None
        if definition.enum_values:
            widget = QtWidgets.QComboBox()
            for option in definition.enum_values:
                widget.addItem(option['label'], option['value'])
            index = widget.findData(value)
            if index < 0:
                widget.addItem(str(value), value)
                index = widget.count() - 1
            widget.setCurrentIndex(index)
            widget.currentIndexChanged.connect(lambda _i, k=key, w=widget: self.edited.emit(k, w.currentData()))
            reset = lambda: widget.setCurrentIndex(widget.findData(default))
            known = known and widget.findData(default) >= 0
        elif kind == 'Bool':
            widget = QtWidgets.QCheckBox()
            widget.setChecked(bool(value))
            widget.toggled.connect(lambda v, k=key: self.edited.emit(k, v))
            reset = lambda: widget.setChecked(default)
            known = known and type(default) is bool
        elif kind.startswith(('Float', 'Int')):
            size = int(kind[-1]) if kind[-1].isdigit() else 1
            vector = list(value) if size > 1 else [value]
            controls = []
            for i in range(size):
                lo = definition.minimum[i] if isinstance(definition.minimum, list) else definition.minimum
                hi = definition.maximum[i] if isinstance(definition.maximum, list) else definition.maximum
                row_label = label + (' ' + ('RGBA' if definition.widget == 'Color' else 'XYZW')[i] if size > 1 else '')
                component_default = (default[i] if isinstance(default, list) and len(default) == size else None) if size > 1 else default
                number = NumberEditor(vector[i], lo, hi, kind.startswith('Int'), default=component_default if known else None, label=row_label)

                def update(v, index=i, k=key, components=vector, count=size):
                    components[index] = v
                    self.edited.emit(k, list(components) if count > 1 else v)
                number.edited.connect(update)
                number.setToolTip(tooltip)
                number.spin.setAccessibleName(row_label)
                form.addRow(row_label, number)
                controls.append(number)
            self.controls[key] = controls
            self.resets[key] = [number.reset_button for number in controls]
            return
        elif kind == 'ByteArray':
            widget = QtWidgets.QLineEdit(str(value or ''))
            widget.setPlaceholderText('resource://…')
            widget.editingFinished.connect(lambda k=key, w=widget: self.edited.emit(k, w.text()))

            def reset():
                widget.setText(default)
                self.edited.emit(key, default)
            known = known and isinstance(default, str)
        else:
            widget = QtWidgets.QLineEdit(json.dumps(value, ensure_ascii=False))
            widget.setReadOnly(True)
            tooltip = f'현재 UI가 지원하지 않는 형식: {kind}. 저장 값은 유지됩니다.'
        widget.setToolTip(tooltip)
        widget.setAccessibleName(label)
        row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget, 1)
        button = make_reset_button(label, default, reset or (lambda: None), known and reset is not None)
        layout.addWidget(button)
        form.addRow(label, row)
        self.controls[key] = widget
        self.resets[key] = button
