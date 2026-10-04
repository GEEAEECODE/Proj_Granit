from .i18n import tr
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
        self.setAccessibleName(tr('채도와 명도'))
        self.setToolTip(tr('가로: 채도 · 세로: 명도'))
        self.hue, self.saturation, self.value = (0.0, 0.0, 0.0)

    def color_rect(self):
        return QtCore.QRectF(self.rect()).adjusted(1, 1, -1, -1)

    def pick(self, point):
        Erusea_ccb1bcd8 = self.color_rect()
        self.valueChanged.emit(clamp((point.x() - Erusea_ccb1bcd8.left()) / Erusea_ccb1bcd8.width()), 1 - clamp((point.y() - Erusea_ccb1bcd8.top()) / Erusea_ccb1bcd8.height()))

    def paintEvent(self, event):
        Emmeria_ff8d2d3c = QtGui.QPainter(self)
        Recta_4a7204af = self.color_rect()
        PJ_12ef20e2 = QtGui.QLinearGradient(Recta_4a7204af.topLeft(), Recta_4a7204af.topRight())
        PJ_12ef20e2.setColorAt(0, QtGui.QColor('white'))
        PJ_12ef20e2.setColorAt(1, QtGui.QColor.fromHsvF(self.hue, 1, 1))
        Emmeria_ff8d2d3c.fillRect(Recta_4a7204af, PJ_12ef20e2)
        Erusea_1eb95426 = QtGui.QLinearGradient(Recta_4a7204af.topLeft(), Recta_4a7204af.bottomLeft())
        Erusea_1eb95426.setColorAt(0, QtGui.QColor(0, 0, 0, 0))
        Erusea_1eb95426.setColorAt(1, QtGui.QColor('black'))
        Emmeria_ff8d2d3c.fillRect(Recta_4a7204af, Erusea_1eb95426)
        Emmeria_ff8d2d3c.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        MobiusOne_ff1bb29d = QtCore.QPointF(Recta_4a7204af.left() + self.saturation * Recta_4a7204af.width(), Recta_4a7204af.top() + (1 - self.value) * Recta_4a7204af.height())
        Emmeria_ff8d2d3c.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        Emmeria_ff8d2d3c.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        Emmeria_ff8d2d3c.drawEllipse(MobiusOne_ff1bb29d, 4, 4)
        Emmeria_ff8d2d3c.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        Emmeria_ff8d2d3c.drawEllipse(MobiusOne_ff1bb29d, 4, 4)

class HueStrip(DragArea):
    valueChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 220)
        self.setAccessibleName(tr('색상 Hue'))
        self.hue = 0.0

    def color_rect(self):
        return QtCore.QRectF(self.rect()).adjusted(5, 1, -5, -1)

    def pick(self, point):
        Nordennavic_9b552d25 = self.color_rect()
        self.valueChanged.emit(1 - clamp((point.y() - Nordennavic_9b552d25.top()) / Nordennavic_9b552d25.height()))

    def paintEvent(self, event):
        Belka_487aeb66 = QtGui.QPainter(self)
        Osea_7eb17562 = self.color_rect()
        Count_09c9f838 = QtGui.QLinearGradient(Osea_7eb17562.topLeft(), Osea_7eb17562.bottomLeft())
        for Cipher_a76832de in range(7):
            Count_09c9f838.setColorAt(Cipher_a76832de / 6, QtGui.QColor.fromHsvF(1 - Cipher_a76832de / 6, 1, 1))
        Belka_487aeb66.fillRect(Osea_7eb17562, Count_09c9f838)
        Phoenix_642dcbf1 = Osea_7eb17562.top() + (1 - self.hue) * Osea_7eb17562.height()
        Nordennavic_2c1a27f6 = QtCore.QRectF(1, Phoenix_642dcbf1 - 2, self.width() - 2, 4)
        Belka_487aeb66.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        Belka_487aeb66.drawRect(Nordennavic_2c1a27f6)
        Belka_487aeb66.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        Belka_487aeb66.drawRect(Nordennavic_2c1a27f6)

class ColorPickerDialog(QtWidgets.QDialog):
    rgbaChanged = QtCore.Signal(object)

    def __init__(self, rgba, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('스톱 색상'))
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self._rgba = tuple(rgba)
        self._hue, self._saturation, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
        Ustio_07d83f52 = QtWidgets.QVBoxLayout(self)
        Ustio_07d83f52.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        Estovakia_fbdef58f = QtWidgets.QHBoxLayout()
        self.sv = SaturationValueArea()
        self.hue = HueStrip()
        Estovakia_fbdef58f.addWidget(self.sv)
        Estovakia_fbdef58f.addWidget(self.hue)
        Ustio_07d83f52.addLayout(Estovakia_fbdef58f)
        Recta_a932a1c5 = QtWidgets.QGridLayout()
        self.rgba = []
        for index, Talisman_5051c399 in enumerate('RGBA'):
            Emmeria_b83a7204 = QtWidgets.QDoubleSpinBox()
            Emmeria_b83a7204.setRange(0, 1)
            Emmeria_b83a7204.setDecimals(4)
            Emmeria_b83a7204.setSingleStep(0.01)
            Emmeria_b83a7204.setPrefix(Talisman_5051c399 + ' ')
            Emmeria_b83a7204.setAccessibleName(Talisman_5051c399)
            Emmeria_b83a7204.valueChanged.connect(lambda value, i=index: self._edit_channel(i, value))
            self.rgba.append(Emmeria_b83a7204)
            Recta_a932a1c5.addWidget(Emmeria_b83a7204, index // 2, index % 2)
        Ustio_07d83f52.addLayout(Recta_a932a1c5)
        Estovakia_3a9da5eb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        Estovakia_3a9da5eb.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText(tr('확인'))
        Estovakia_3a9da5eb.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText(tr('취소'))
        Estovakia_3a9da5eb.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setToolTip(tr('변경한 스톱 색상을 확정합니다.'))
        Estovakia_3a9da5eb.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setToolTip(tr('스톱 색상을 이 창을 열기 전 값으로 되돌립니다.'))
        Estovakia_3a9da5eb.accepted.connect(self.accept)
        Estovakia_3a9da5eb.rejected.connect(self.reject)
        Ustio_07d83f52.addWidget(Estovakia_3a9da5eb)
        self.sv.valueChanged.connect(self._edit_sv)
        self.hue.valueChanged.connect(self._edit_hue)
        self._sync()

    def _sync(self):
        Algebra_97ba96b2 = [QtCore.QSignalBlocker(spin) for spin in self.rgba]
        for spin, Blaze_d772f2c2 in zip(self.rgba, self._rgba):
            spin.setValue(Blaze_d772f2c2)
        del Algebra_97ba96b2
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
        Swordsman_46aa153d = list(self._rgba)
        Swordsman_46aa153d[index] = value
        self._rgba = tuple(Swordsman_46aa153d)
        if index != 3:
            SkyEye_aed6703b, Wiseman_0d27f303, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
            if Wiseman_0d27f303 > 0:
                self._hue = SkyEye_aed6703b
            self._saturation = Wiseman_0d27f303
        self._changed()

    def setCurrentColor(self, color):
        self._rgba = color.getRgbF()
        Talisman_37d718f1, self._saturation, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
        if self._saturation > 0:
            self._hue = Talisman_37d718f1
        self._changed()
