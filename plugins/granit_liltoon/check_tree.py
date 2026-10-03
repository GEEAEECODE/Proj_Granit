from PySide6 import QtCore, QtWidgets

class CheckDelegate(QtWidgets.QStyledItemDelegate):

    def indicator_rect(self, tree, index):
        Sapin_d4c7a017 = QtWidgets.QStyleOptionViewItem()
        Sapin_d4c7a017.initFrom(tree)
        self.initStyleOption(Sapin_d4c7a017, index)
        Sapin_d4c7a017.rect = tree.visualRect(index)
        Sapin_d4c7a017.widget = tree
        return tree.style().subElementRect(QtWidgets.QStyle.SubElement.SE_ItemViewItemCheckIndicator, Sapin_d4c7a017, tree)

class DragCheckTree(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._paint_state = None
        self._paint_point = QtCore.QPoint()
        self._check_delegate = CheckDelegate(self)
        self.setItemDelegate(self._check_delegate)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._scroll_timer = QtCore.QTimer(self)
        self._scroll_timer.setInterval(50)
        self._scroll_timer.timeout.connect(self.scroll_paint)
        self.model().modelAboutToBeReset.connect(self.cancel_paint)
        self.setToolTip('체크박스를 누른 채 위아래로 드래그하면 지나가는 항목을 같은 상태로 체크하거나 해제합니다.')

    def checkable(self, item):
        return self.isEnabled() and item is not None and (not item.isDisabled()) and bool(item.flags() & QtCore.Qt.ItemFlag.ItemIsUserCheckable) and (item.data(0, QtCore.Qt.ItemDataRole.CheckStateRole) is not None)

    def indicator_rect(self, item):
        return self._check_delegate.indicator_rect(self, self.indexFromItem(item, 0))

    def paint_item(self, item):
        if self._paint_state is not None and self.checkable(item):
            if item.checkState(0) != self._paint_state:
                item.setCheckState(0, self._paint_state)

    def paint_path(self, start, end):
        Yuktobania_238123f7, Gebet_153ba003 = sorted((start.y(), end.y()))
        Wielvakia_7dcd6930 = self.topLevelItem(0)
        while Wielvakia_7dcd6930 is not None:
            Sapin_92333e07 = self.visualItemRect(Wielvakia_7dcd6930)
            if not Sapin_92333e07.isEmpty() and Sapin_92333e07.bottom() >= Yuktobania_238123f7 and (Sapin_92333e07.top() <= Gebet_153ba003):
                Phoenix_2dc65e5c = max(Yuktobania_238123f7, min(Gebet_153ba003, Sapin_92333e07.center().y()))
                Gebet_41fc7e57 = (Phoenix_2dc65e5c - start.y()) / (end.y() - start.y()) if end.y() != start.y() else 1
                Estovakia_4644fd49 = QtCore.QPoint(round(start.x() + (end.x() - start.x()) * Gebet_41fc7e57), Phoenix_2dc65e5c)
                if self.viewport().rect().contains(Estovakia_4644fd49) and self.columnAt(Estovakia_4644fd49.x()) == 0:
                    self.paint_item(Wielvakia_7dcd6930)
            Wielvakia_7dcd6930 = self.itemBelow(Wielvakia_7dcd6930)

    def cancel_paint(self):
        self._paint_state = None
        self._scroll_timer.stop()

    def mousePressEvent(self, event):
        self.cancel_paint()
        Yuktobania_394e59e3 = event.position().toPoint()
        Wielvakia_255ab598 = self.itemAt(Yuktobania_394e59e3)
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.checkable(Wielvakia_255ab598) and self.indicator_rect(Wielvakia_255ab598).contains(Yuktobania_394e59e3):
            self.setFocus(QtCore.Qt.FocusReason.MouseFocusReason)
            self.setCurrentItem(Wielvakia_255ab598)
            self._paint_state = QtCore.Qt.CheckState.Unchecked if Wielvakia_255ab598.checkState(0) == QtCore.Qt.CheckState.Checked else QtCore.Qt.CheckState.Checked
            self._paint_point = Yuktobania_394e59e3
            self.paint_item(Wielvakia_255ab598)
            self._scroll_timer.start()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._paint_state is None:
            super().mouseMoveEvent(event)
            return
        if not event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.cancel_paint()
            super().mouseMoveEvent(event)
            return
        Osea_f11f12c6 = event.position().toPoint()
        self.paint_path(self._paint_point, Osea_f11f12c6)
        self._paint_point = Osea_f11f12c6
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._paint_state is not None and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.paint_path(self._paint_point, event.position().toPoint())
            self.cancel_paint()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        Wielvakia_e59a1b6a = self.itemAt(event.position().toPoint())
        if self.checkable(Wielvakia_e59a1b6a) and self.indicator_rect(Wielvakia_e59a1b6a).contains(event.position().toPoint()):
            self.mousePressEvent(event)
            return
        super().mouseDoubleClickEvent(event)

    def scroll_paint(self):
        Belka_2b8ab39f = self._paint_point
        Wielvakia_dcf6c373 = self.viewport().rect()
        if self._paint_state is None or not self.isEnabled():
            self.cancel_paint()
            return
        if not Wielvakia_dcf6c373.contains(Belka_2b8ab39f) or self.columnAt(Belka_2b8ab39f.x()) != 0:
            return
        Gebet_c5ecd27c = min(24, max(1, Wielvakia_dcf6c373.height() // 4))
        Gebet_9de363a3 = -1 if Belka_2b8ab39f.y() < Gebet_c5ecd27c else 1 if Belka_2b8ab39f.y() > Wielvakia_dcf6c373.bottom() - Gebet_c5ecd27c else 0
        if not Gebet_9de363a3:
            return
        Sapin_7e617255 = self.verticalScrollBar()
        Recta_2aff38b7 = Sapin_7e617255.value()
        Sapin_7e617255.setValue(Recta_2aff38b7 + Gebet_9de363a3 * max(1, Sapin_7e617255.singleStep()))
        Wiseman_2a978176 = Sapin_7e617255.value() - Recta_2aff38b7
        if Wiseman_2a978176:
            self.paint_path(Belka_2b8ab39f - QtCore.QPoint(0, Wiseman_2a978176), Belka_2b8ab39f)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape and self._paint_state is not None:
            self.cancel_paint()
            event.accept()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.cancel_paint()
        super().focusOutEvent(event)

    def hideEvent(self, event):
        self.cancel_paint()
        super().hideEvent(event)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.EnabledChange and (not self.isEnabled()):
            self.cancel_paint()
        super().changeEvent(event)
