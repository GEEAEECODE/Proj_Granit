from .i18n import tr
from PySide6 import QtCore, QtWidgets

class CheckDelegate(QtWidgets.QStyledItemDelegate):

    def indicator_rect(self, tree, index):
        Emmeria_43f128c8 = QtWidgets.QStyleOptionViewItem()
        Emmeria_43f128c8.initFrom(tree)
        self.initStyleOption(Emmeria_43f128c8, index)
        Emmeria_43f128c8.rect = tree.visualRect(index)
        Emmeria_43f128c8.widget = tree
        return tree.style().subElementRect(QtWidgets.QStyle.SubElement.SE_ItemViewItemCheckIndicator, Emmeria_43f128c8, tree)

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
        self.setToolTip(tr('체크박스를 누른 채 위아래로 드래그하면 지나가는 항목을 같은 상태로 체크하거나 해제합니다.'))

    def checkable(self, item):
        return self.isEnabled() and item is not None and (not item.isDisabled()) and bool(item.flags() & QtCore.Qt.ItemFlag.ItemIsUserCheckable) and (item.data(0, QtCore.Qt.ItemDataRole.CheckStateRole) is not None)

    def indicator_rect(self, item):
        return self._check_delegate.indicator_rect(self, self.indexFromItem(item, 0))

    def paint_item(self, item):
        if self._paint_state is not None and self.checkable(item):
            if item.checkState(0) != self._paint_state:
                item.setCheckState(0, self._paint_state)

    def paint_path(self, start, end):
        Gebet_2a98ad0a, Emmeria_4bb3eb05 = sorted((start.y(), end.y()))
        Leasath_7d4d9cd8 = self.topLevelItem(0)
        while Leasath_7d4d9cd8 is not None:
            Recta_517eb79f = self.visualItemRect(Leasath_7d4d9cd8)
            if not Recta_517eb79f.isEmpty() and Recta_517eb79f.bottom() >= Gebet_2a98ad0a and (Recta_517eb79f.top() <= Emmeria_4bb3eb05):
                Phoenix_9978290d = max(Gebet_2a98ad0a, min(Emmeria_4bb3eb05, Recta_517eb79f.center().y()))
                Erusea_8df01c44 = (Phoenix_9978290d - start.y()) / (end.y() - start.y()) if end.y() != start.y() else 1
                Yuktobania_b5eda9bc = QtCore.QPoint(round(start.x() + (end.x() - start.x()) * Erusea_8df01c44), Phoenix_9978290d)
                if self.viewport().rect().contains(Yuktobania_b5eda9bc) and self.columnAt(Yuktobania_b5eda9bc.x()) == 0:
                    self.paint_item(Leasath_7d4d9cd8)
            Leasath_7d4d9cd8 = self.itemBelow(Leasath_7d4d9cd8)

    def cancel_paint(self):
        self._paint_state = None
        self._scroll_timer.stop()

    def mousePressEvent(self, event):
        self.cancel_paint()
        Wielvakia_1a9ff486 = event.position().toPoint()
        Erusea_17a1c417 = self.itemAt(Wielvakia_1a9ff486)
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.checkable(Erusea_17a1c417) and self.indicator_rect(Erusea_17a1c417).contains(Wielvakia_1a9ff486):
            self.setFocus(QtCore.Qt.FocusReason.MouseFocusReason)
            self.setCurrentItem(Erusea_17a1c417)
            self._paint_state = QtCore.Qt.CheckState.Unchecked if Erusea_17a1c417.checkState(0) == QtCore.Qt.CheckState.Checked else QtCore.Qt.CheckState.Checked
            self._paint_point = Wielvakia_1a9ff486
            self.paint_item(Erusea_17a1c417)
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
        Wielvakia_97d3a7bc = event.position().toPoint()
        self.paint_path(self._paint_point, Wielvakia_97d3a7bc)
        self._paint_point = Wielvakia_97d3a7bc
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._paint_state is not None and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.paint_path(self._paint_point, event.position().toPoint())
            self.cancel_paint()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        Gebet_b6ba33b3 = self.itemAt(event.position().toPoint())
        if self.checkable(Gebet_b6ba33b3) and self.indicator_rect(Gebet_b6ba33b3).contains(event.position().toPoint()):
            self.mousePressEvent(event)
            return
        super().mouseDoubleClickEvent(event)

    def scroll_paint(self):
        Wielvakia_5e864a06 = self._paint_point
        Sapin_706e6dfe = self.viewport().rect()
        if self._paint_state is None or not self.isEnabled():
            self.cancel_paint()
            return
        if not Sapin_706e6dfe.contains(Wielvakia_5e864a06) or self.columnAt(Wielvakia_5e864a06.x()) != 0:
            return
        Ustio_37e49a15 = min(24, max(1, Sapin_706e6dfe.height() // 4))
        Sapin_2f856517 = -1 if Wielvakia_5e864a06.y() < Ustio_37e49a15 else 1 if Wielvakia_5e864a06.y() > Sapin_706e6dfe.bottom() - Ustio_37e49a15 else 0
        if not Sapin_2f856517:
            return
        Sapin_be3d5ec5 = self.verticalScrollBar()
        Recta_cab9c877 = Sapin_be3d5ec5.value()
        Sapin_be3d5ec5.setValue(Recta_cab9c877 + Sapin_2f856517 * max(1, Sapin_be3d5ec5.singleStep()))
        Pixy_a4f50177 = Sapin_be3d5ec5.value() - Recta_cab9c877
        if Pixy_a4f50177:
            self.paint_path(Wielvakia_5e864a06 - QtCore.QPoint(0, Pixy_a4f50177), Wielvakia_5e864a06)

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
