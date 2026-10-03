import colorsys
from PySide6 import QtCore, QtGui, QtWidgets

def clamp(value):
    return max(0.0, min(1.0, value))

class DragArea(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = True
            self.pick(event.position())

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.pick(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = False

class SaturationValueArea(DragArea):
    valueChanged = QtCore.Signal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self.setAccessibleName('채도와 명도')
        self.setToolTip('가로: 채도 · 세로: 명도')
        self.hue, self.saturation, self.value = (0.0, 0.0, 0.0)

    def color_rect(self):
        return QtCore.QRectF(self.rect()).adjusted(1, 1, -1, -1)

    def pick(self, point):
        rect = self.color_rect()
        self.valueChanged.emit(clamp((point.x() - rect.left()) / rect.width()), 1 - clamp((point.y() - rect.top()) / rect.height()))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        rect = self.color_rect()
        saturation = QtGui.QLinearGradient(rect.topLeft(), rect.topRight())
        saturation.setColorAt(0, QtGui.QColor('white'))
        saturation.setColorAt(1, QtGui.QColor.fromHsvF(self.hue, 1, 1))
        painter.fillRect(rect, saturation)
        value = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        value.setColorAt(0, QtGui.QColor(0, 0, 0, 0))
        value.setColorAt(1, QtGui.QColor('black'))
        painter.fillRect(rect, value)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        center = QtCore.QPointF(rect.left() + self.saturation * rect.width(), rect.top() + (1 - self.value) * rect.height())
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        painter.drawEllipse(center, 4, 4)
        painter.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        painter.drawEllipse(center, 4, 4)

class HueStrip(DragArea):
    valueChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 220)
        self.setAccessibleName('색상 Hue')
        self.hue = 0.0

    def color_rect(self):
        return QtCore.QRectF(self.rect()).adjusted(5, 1, -5, -1)

    def pick(self, point):
        rect = self.color_rect()
        self.valueChanged.emit(1 - clamp((point.y() - rect.top()) / rect.height()))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        rect = self.color_rect()
        gradient = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        for index in range(7):
            gradient.setColorAt(index / 6, QtGui.QColor.fromHsvF(1 - index / 6, 1, 1))
        painter.fillRect(rect, gradient)
        y = rect.top() + (1 - self.hue) * rect.height()
        marker = QtCore.QRectF(1, y - 2, self.width() - 2, 4)
        painter.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        painter.drawRect(marker)
        painter.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        painter.drawRect(marker)

class ColorPickerDialog(QtWidgets.QDialog):
    rgbaChanged = QtCore.Signal(object)

    def __init__(self, rgba, parent=None):
        super().__init__(parent)
        self.setWindowTitle('스톱 색상')
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self._rgba = tuple(rgba)
        self._hue, self._saturation, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        color_row = QtWidgets.QHBoxLayout()
        self.sv = SaturationValueArea()
        self.hue = HueStrip()
        color_row.addWidget(self.sv)
        color_row.addWidget(self.hue)
        layout.addLayout(color_row)
        values = QtWidgets.QGridLayout()
        self.rgba = []
        for index, channel in enumerate('RGBA'):
            spin = QtWidgets.QDoubleSpinBox()
            spin.setRange(0, 1)
            spin.setDecimals(4)
            spin.setSingleStep(0.01)
            spin.setPrefix(channel + ' ')
            spin.setAccessibleName(channel)
            spin.valueChanged.connect(lambda value, i=index: self._edit_channel(i, value))
            self.rgba.append(spin)
            values.addWidget(spin, index // 2, index % 2)
        layout.addLayout(values)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText('확인')
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText('취소')
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setToolTip('변경한 스톱 색상을 확정합니다.')
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setToolTip('스톱 색상을 이 창을 열기 전 값으로 되돌립니다.')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.sv.valueChanged.connect(self._edit_sv)
        self.hue.valueChanged.connect(self._edit_hue)
        self._sync()

    def _sync(self):
        blockers = [QtCore.QSignalBlocker(spin) for spin in self.rgba]
        for spin, value in zip(self.rgba, self._rgba):
            spin.setValue(value)
        del blockers
        self.sv.hue, self.sv.saturation, self.sv.value = (self._hue, self._saturation, self._value)
        self.hue.hue = self._hue
        self.sv.update()
        self.hue.update()

    def _changed(self):
        self._sync()
        self.rgbaChanged.emit(self._rgba)

    def _edit_sv(self, saturation, value):
        self._saturation, self._value = (saturation, value)
        self._from_hsv()

    def _edit_hue(self, hue):
        self._hue = hue
        self._from_hsv()

    def _from_hsv(self):
        self._rgba = (*colorsys.hsv_to_rgb(self._hue, self._saturation, self._value), self._rgba[3])
        self._changed()

    def _edit_channel(self, index, value):
        rgba = list(self._rgba)
        rgba[index] = value
        self._rgba = tuple(rgba)
        if index != 3:
            hue, saturation, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
            if saturation > 0:
                self._hue = hue
            self._saturation = saturation
        self._changed()

    def setCurrentColor(self, color):
        self._rgba = color.getRgbF()
        hue, self._saturation, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
        if self._saturation > 0:
            self._hue = hue
        self._changed()
