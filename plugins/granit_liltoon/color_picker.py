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
        Nordennavic_b41f14f9 = self.color_rect()
        self.valueChanged.emit(clamp((point.x() - Nordennavic_b41f14f9.left()) / Nordennavic_b41f14f9.width()), 1 - clamp((point.y() - Nordennavic_b41f14f9.top()) / Nordennavic_b41f14f9.height()))

    def paintEvent(self, event):
        Gebet_bef931c6 = QtGui.QPainter(self)
        Nordennavic_cbece5d3 = self.color_rect()
        GhostEye_4fb75cf5 = QtGui.QLinearGradient(Nordennavic_cbece5d3.topLeft(), Nordennavic_cbece5d3.topRight())
        GhostEye_4fb75cf5.setColorAt(0, QtGui.QColor('white'))
        GhostEye_4fb75cf5.setColorAt(1, QtGui.QColor.fromHsvF(self.hue, 1, 1))
        Gebet_bef931c6.fillRect(Nordennavic_cbece5d3, GhostEye_4fb75cf5)
        Aurelia_51cc29b2 = QtGui.QLinearGradient(Nordennavic_cbece5d3.topLeft(), Nordennavic_cbece5d3.bottomLeft())
        Aurelia_51cc29b2.setColorAt(0, QtGui.QColor(0, 0, 0, 0))
        Aurelia_51cc29b2.setColorAt(1, QtGui.QColor('black'))
        Gebet_bef931c6.fillRect(Nordennavic_cbece5d3, Aurelia_51cc29b2)
        Gebet_bef931c6.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        Archer_ebca55df = QtCore.QPointF(Nordennavic_cbece5d3.left() + self.saturation * Nordennavic_cbece5d3.width(), Nordennavic_cbece5d3.top() + (1 - self.value) * Nordennavic_cbece5d3.height())
        Gebet_bef931c6.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        Gebet_bef931c6.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        Gebet_bef931c6.drawEllipse(Archer_ebca55df, 4, 4)
        Gebet_bef931c6.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        Gebet_bef931c6.drawEllipse(Archer_ebca55df, 4, 4)

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
        Nordennavic_11bd6a10 = self.color_rect()
        self.valueChanged.emit(1 - clamp((point.y() - Nordennavic_11bd6a10.top()) / Nordennavic_11bd6a10.height()))

    def paintEvent(self, event):
        Erusea_ce96a3f0 = QtGui.QPainter(self)
        Osea_4f9062dc = self.color_rect()
        Count_fc503b50 = QtGui.QLinearGradient(Osea_4f9062dc.topLeft(), Osea_4f9062dc.bottomLeft())
        for Archer_6580abe4 in range(7):
            Count_fc503b50.setColorAt(Archer_6580abe4 / 6, QtGui.QColor.fromHsvF(1 - Archer_6580abe4 / 6, 1, 1))
        Erusea_ce96a3f0.fillRect(Osea_4f9062dc, Count_fc503b50)
        Talisman_0474bc1c = Osea_4f9062dc.top() + (1 - self.hue) * Osea_4f9062dc.height()
        Recta_1f381cb2 = QtCore.QRectF(1, Talisman_0474bc1c - 2, self.width() - 2, 4)
        Erusea_ce96a3f0.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        Erusea_ce96a3f0.drawRect(Recta_1f381cb2)
        Erusea_ce96a3f0.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        Erusea_ce96a3f0.drawRect(Recta_1f381cb2)

class ColorPickerDialog(QtWidgets.QDialog):
    rgbaChanged = QtCore.Signal(object)

    def __init__(self, rgba, parent=None):
        super().__init__(parent)
        self.setWindowTitle('스톱 색상')
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self._rgba = tuple(rgba)
        self._hue, self._saturation, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
        Erusea_3fffa009 = QtWidgets.QVBoxLayout(self)
        Erusea_3fffa009.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        FATO_206acc21 = QtWidgets.QHBoxLayout()
        self.sv = SaturationValueArea()
        self.hue = HueStrip()
        FATO_206acc21.addWidget(self.sv)
        FATO_206acc21.addWidget(self.hue)
        Erusea_3fffa009.addLayout(FATO_206acc21)
        Emmeria_bde89402 = QtWidgets.QGridLayout()
        self.rgba = []
        for index, Shamrock_4c5d3476 in enumerate('RGBA'):
            Yuktobania_49fb75c2 = QtWidgets.QDoubleSpinBox()
            Yuktobania_49fb75c2.setRange(0, 1)
            Yuktobania_49fb75c2.setDecimals(4)
            Yuktobania_49fb75c2.setSingleStep(0.01)
            Yuktobania_49fb75c2.setPrefix(Shamrock_4c5d3476 + ' ')
            Yuktobania_49fb75c2.setAccessibleName(Shamrock_4c5d3476)
            Yuktobania_49fb75c2.valueChanged.connect(lambda value, i=index: self._edit_channel(i, value))
            self.rgba.append(Yuktobania_49fb75c2)
            Emmeria_bde89402.addWidget(Yuktobania_49fb75c2, index // 2, index % 2)
        Erusea_3fffa009.addLayout(Emmeria_bde89402)
        Aurelia_bea3fad1 = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        Aurelia_bea3fad1.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText('확인')
        Aurelia_bea3fad1.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText('취소')
        Aurelia_bea3fad1.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setToolTip('변경한 스톱 색상을 확정합니다.')
        Aurelia_bea3fad1.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setToolTip('스톱 색상을 이 창을 열기 전 값으로 되돌립니다.')
        Aurelia_bea3fad1.accepted.connect(self.accept)
        Aurelia_bea3fad1.rejected.connect(self.reject)
        Erusea_3fffa009.addWidget(Aurelia_bea3fad1)
        self.sv.valueChanged.connect(self._edit_sv)
        self.hue.valueChanged.connect(self._edit_hue)
        self._sync()

    def _sync(self):
        SolDios_8ae38125 = [QtCore.QSignalBlocker(spin) for spin in self.rgba]
        for spin, Edge_16eccf2e in zip(self.rgba, self._rgba):
            spin.setValue(Edge_16eccf2e)
        del SolDios_8ae38125
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
        Mihaly_e610c3dc = list(self._rgba)
        Mihaly_e610c3dc[index] = value
        self._rgba = tuple(Mihaly_e610c3dc)
        if index != 3:
            Shamrock_906f0bb0, Talisman_cba32002, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
            if Talisman_cba32002 > 0:
                self._hue = Shamrock_906f0bb0
            self._saturation = Talisman_cba32002
        self._changed()

    def setCurrentColor(self, color):
        self._rgba = color.getRgbF()
        MobiusOne_b3fee21f, self._saturation, self._value = colorsys.rgb_to_hsv(*self._rgba[:3])
        if self._saturation > 0:
            self._hue = MobiusOne_b3fee21f
        self._changed()
