from dataclasses import replace
from PySide6 import QtCore, QtGui, QtWidgets
from .color_picker import ColorPickerDialog
from .gradient import Gradient, MAX_STOPS

class GradientBar(QtWidgets.QWidget):
    selectionChanged = QtCore.Signal(str)
    positionEdited = QtCore.Signal(str, float)
    addRequested = QtCore.Signal(float)
    colorRequested = QtCore.Signal()
    positionRequested = QtCore.Signal()
    deleteRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)
        self.setFixedHeight(84)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setToolTip('위·아래 빈 곳 클릭: 추가 · 드래그: 함께 이동 · 위 더블클릭: 색상 · 아래 더블클릭: 위치 · 우클릭: 삭제 (최소 2개)')
        self.gradient = Gradient.default()
        self.selected = self.gradient.stops[0].key
        self._dragging = False
        self._image = QtGui.QImage()
        self._refresh = QtCore.QTimer(self)
        self._refresh.setSingleShot(True)
        self._refresh.setInterval(33)
        self._refresh.timeout.connect(self._render_preview)
        self._render_preview()

    def set_gradient(self, gradient, selected):
        self.gradient, self.selected = (gradient, selected)
        if not self._refresh.isActive():
            self._refresh.start()
        self.update()

    def _render_preview(self):
        data = self.gradient.row_bytes(512)
        self._image = QtGui.QImage(data, 512, 1, 512 * 4, QtGui.QImage.Format.Format_RGBA8888).copy()
        self.update()

    def bar_rect(self):
        return QtCore.QRectF(12, 26, max(1, self.width() - 24), 32)

    def value_at(self, x):
        rect = self.bar_rect()
        return min(1.0, max(0.0, (x - rect.left()) / rect.width()))

    def marker(self, stop, upper=False):
        rect = self.bar_rect()
        x = rect.left() + stop.position * rect.width()
        y, direction = (rect.top() - 2, -1) if upper else (rect.bottom() + 2, 1)
        return QtGui.QPolygonF([QtCore.QPointF(x, y), QtCore.QPointF(x - 6, y + direction * 7), QtCore.QPointF(x - 6, y + direction * 18), QtCore.QPointF(x + 6, y + direction * 18), QtCore.QPointF(x + 6, y + direction * 7)])

    def stop_at(self, point):
        for stop in reversed(sorted(self.gradient.stops, key=lambda s: s.key == self.selected)):
            if any((self.marker(stop, upper).containsPoint(point, QtCore.Qt.FillRule.OddEvenFill) for upper in (True, False))):
                return stop
        return None

    def stop_row(self, upper=False):
        rect = self.bar_rect()
        y = rect.top() - 22 if upper else rect.bottom() + 2
        return QtCore.QRectF(rect.left(), y, rect.width(), 20)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.bar_rect()
        painter.save()
        painter.setClipRect(rect)
        for y in range(int(rect.top()), int(rect.bottom()) + 8, 8):
            for x in range(int(rect.left()), int(rect.right()) + 8, 8):
                shade = 95 if ((x - int(rect.left())) // 8 + (y - int(rect.top())) // 8) % 2 else 145
                painter.fillRect(x, y, 8, 8, QtGui.QColor(shade, shade, shade))
        painter.drawImage(rect, self._image)
        painter.restore()
        painter.setPen(QtGui.QPen(QtGui.QColor('#111111'), 1))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRect(rect)
        for stop in sorted(self.gradient.stops, key=lambda s: s.key == self.selected):
            painter.setPen(QtGui.QPen(QtGui.QColor('#ffffff' if stop.key == self.selected else '#151515'), 2 if stop.key == self.selected else 1))
            painter.setBrush(QtGui.QColor.fromRgbF(*stop.color[:3]))
            painter.drawPolygon(self.marker(stop, upper=True))
            painter.setBrush(self.palette().color(QtGui.QPalette.ColorRole.Button))
            painter.drawPolygon(self.marker(stop))

    def mousePressEvent(self, event):
        self._dragging = False
        if event.button() not in (QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton):
            return
        self.setFocus()
        stop = self.stop_at(event.position())
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            if stop is not None:
                self.selectionChanged.emit(stop.key)
                if len(self.gradient.stops) > 2:
                    self.deleteRequested.emit()
            return
        if stop is not None:
            self.selectionChanged.emit(stop.key)
            self._dragging = True
        elif any((self.stop_row(upper).contains(event.position()) for upper in (True, False))) and len(self.gradient.stops) < MAX_STOPS:
            self.addRequested.emit(self.value_at(event.position().x()))
            self._dragging = True

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.positionEdited.emit(self.selected, self.value_at(event.position().x()))

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = False

    def mouseDoubleClickEvent(self, event):
        self._dragging = False
        stop = self.stop_at(event.position())
        if event.button() == QtCore.Qt.MouseButton.LeftButton and stop is not None:
            self.selectionChanged.emit(stop.key)
            if event.position().y() < self.bar_rect().top():
                self.colorRequested.emit()
            else:
                self.positionRequested.emit()

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key.Key_Delete, QtCore.Qt.Key.Key_Backspace):
            self.deleteRequested.emit()
        else:
            super().keyPressEvent(event)

class PositionDialog(QtWidgets.QDialog):
    positionEdited = QtCore.Signal(float)

    def __init__(self, position, parent=None):
        super().__init__(parent)
        self.setWindowTitle('스톱 위치')
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.position = QtWidgets.QDoubleSpinBox()
        self.position.setAccessibleName('스톱 위치 0~1')
        self.position.setRange(0, 1)
        self.position.setDecimals(6)
        self.position.setSingleStep(0.01)
        self.position.setValue(position)
        self.position.setMinimumWidth(160)
        self.position.selectAll()
        self.position.valueChanged.connect(self.positionEdited.emit)
        layout.addWidget(self.position)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText('확인')
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText('취소')
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setToolTip('변경한 스톱 위치를 확정합니다.')
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setToolTip('스톱 위치를 이 창을 열기 전 값으로 되돌립니다.')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class GradientPanel(QtWidgets.QWidget):
    gradientEdited = QtCore.Signal(object)

    def __init__(self, parent=None, options_above=False):
        super().__init__(parent)
        self.setObjectName('FoundryGradientGeneratorPanel')
        self.setWindowTitle('Foundry Gradient Generator')
        self.setMinimumWidth(340)
        self.gradient = Gradient.default()
        self.selected = self.gradient.stops[0].key
        self._color_dialog = None
        self._position_dialog = None
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.bar = GradientBar()
        if not options_above:
            layout.addWidget(self.bar)
        row = QtWidgets.QHBoxLayout()
        self.flip = QtWidgets.QPushButton('반전')
        self.flip.setToolTip('모든 스톱의 위치를 좌우 반전합니다.')
        self.mode = QtWidgets.QComboBox()
        self.mode.setAccessibleName('색 보간 공간')
        self.mode.setToolTip('색 보간 공간')
        for value in ('RGB', 'HSV', 'HSL'):
            self.mode.addItem(value, value)
        self.interpolation = QtWidgets.QComboBox()
        self.interpolation.setAccessibleName('RGB 보간')
        self.interpolation.setToolTip('RGB 보간 방식')
        for label, value in [('Linear', 'LINEAR'), ('Constant', 'CONSTANT'), ('Ease', 'EASE'), ('Cardinal', 'CARDINAL'), ('B-Spline', 'B_SPLINE')]:
            self.interpolation.addItem(label, value)
        self.hue = QtWidgets.QComboBox()
        self.hue.setAccessibleName('Hue 방향')
        self.hue.setToolTip('Hue 보간 방향 · CW: 시계 · CCW: 반시계')
        for label, value in [('Near', 'NEAR'), ('Far', 'FAR'), ('CW', 'CW'), ('CCW', 'CCW')]:
            self.hue.addItem(label, value)
        self.blend_options = QtWidgets.QStackedWidget()
        self.blend_options.addWidget(self.interpolation)
        self.blend_options.addWidget(self.hue)
        self.blend_options.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        row.addWidget(self.flip)
        row.addWidget(self.mode)
        row.addWidget(self.blend_options, 1)
        layout.addLayout(row)
        if options_above:
            layout.addWidget(self.bar)
        layout.addStretch()
        self.bar.selectionChanged.connect(self.select)
        self.bar.positionEdited.connect(self.move_stop)
        self.bar.addRequested.connect(self.add_stop)
        self.bar.colorRequested.connect(self.open_color)
        self.bar.positionRequested.connect(self.open_position)
        self.bar.deleteRequested.connect(self.remove_stop)
        self.flip.clicked.connect(self.flip_stops)
        self.mode.currentIndexChanged.connect(self.edit_options)
        self.interpolation.currentIndexChanged.connect(self.edit_options)
        self.hue.currentIndexChanged.connect(self.edit_options)
        self.refresh_controls()

    def current_stop(self):
        return next((s for s in self.gradient.stops if s.key == self.selected))

    def refresh_controls(self):
        widgets = [self.mode, self.interpolation, self.hue]
        blockers = [QtCore.QSignalBlocker(w) for w in widgets]
        for combo, value in ((self.mode, self.gradient.color_mode), (self.interpolation, self.gradient.interpolation), (self.hue, self.gradient.hue_mode)):
            combo.setCurrentIndex(combo.findData(value))
        del blockers
        self.blend_options.setCurrentWidget(self.interpolation if self.gradient.color_mode == 'RGB' else self.hue)
        self.bar.set_gradient(self.gradient, self.selected)

    def update_gradient(self, gradient):
        self.gradient = gradient
        self.refresh_controls()
        self.gradientEdited.emit(gradient)

    def load_gradient(self, gradient):
        self.close_editors()
        self.gradient = gradient
        if self.selected not in {s.key for s in gradient.stops}:
            self.selected = gradient.stops[0].key
        self.refresh_controls()

    def select(self, key):
        self.selected = key
        self.refresh_controls()

    def move_stop(self, key, value):
        self.update_gradient(self.gradient.change_stop(key, position=value))

    def add_stop(self, position):
        if len(self.gradient.stops) >= MAX_STOPS:
            return
        gradient, self.selected = self.gradient.add_stop(position)
        self.update_gradient(gradient)

    def remove_stop(self):
        if len(self.gradient.stops) <= 2:
            return
        gradient = self.gradient.remove_stop(self.selected)
        self.selected = gradient.stops[0].key
        self.update_gradient(gradient)

    def flip_stops(self):
        stops = tuple((replace(s, position=1 - s.position) for s in reversed(self.gradient.stops)))
        self.update_gradient(replace(self.gradient, stops=stops))

    def edit_options(self, *_args):
        self.update_gradient(replace(self.gradient, interpolation=self.interpolation.currentData(), color_mode=self.mode.currentData(), hue_mode=self.hue.currentData()))

    def _raise_editor(self):
        for dialog in (self._color_dialog, self._position_dialog):
            if dialog is not None:
                dialog.raise_()
                dialog.activateWindow()
                return True
        return False

    def open_color(self):
        if self._raise_editor():
            return
        stop = self.current_stop()
        original = stop.color
        dialog = ColorPickerDialog(original, self)
        self._color_dialog = dialog

        def change(rgba):
            self.update_gradient(self.gradient.change_stop(stop.key, color=rgba))

        def finish(result):
            if result == QtWidgets.QDialog.DialogCode.Rejected:
                self.update_gradient(self.gradient.change_stop(stop.key, color=original))
            self._color_dialog = None
            dialog.deleteLater()
        dialog.rgbaChanged.connect(change)
        dialog.finished.connect(finish)
        dialog.open()

    def open_position(self):
        if self._raise_editor():
            return
        stop = self.current_stop()
        original = stop.position
        dialog = PositionDialog(original, self)
        self._position_dialog = dialog
        dialog.positionEdited.connect(lambda value: self.move_stop(stop.key, value))

        def finish(result):
            if result == QtWidgets.QDialog.DialogCode.Rejected:
                self.move_stop(stop.key, original)
            self._position_dialog = None
            dialog.deleteLater()
        dialog.finished.connect(finish)
        dialog.open()
        dialog.position.setFocus()

    def close_editors(self):
        if self._color_dialog:
            self._color_dialog.reject()
        if self._position_dialog:
            self._position_dialog.reject()

    def shutdown(self):
        self.close_editors()
        self.bar._refresh.stop()
