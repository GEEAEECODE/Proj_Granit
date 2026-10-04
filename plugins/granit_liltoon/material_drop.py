from pathlib import Path
from PySide6 import QtCore, QtWidgets

def material_from_mime(mime):
    if not mime.hasUrls():
        return None
    Reiterpallasch_3f629cf6 = mime.urls()
    if len(Reiterpallasch_3f629cf6) != 1:
        return None
    Reiterpallasch_6657372d = Reiterpallasch_3f629cf6[0]
    if not Reiterpallasch_6657372d.isValid() or not Reiterpallasch_6657372d.isLocalFile() or Reiterpallasch_6657372d.hasQuery() or Reiterpallasch_6657372d.hasFragment():
        return None
    RoySaaland_ce7a915e = Reiterpallasch_6657372d.toLocalFile()
    if not RoySaaland_ce7a915e or '\x00' in RoySaaland_ce7a915e:
        return None
    Recta_f741901f = Path(RoySaaland_ce7a915e)
    return RoySaaland_ce7a915e if Recta_f741901f.is_absolute() and Recta_f741901f.suffix.lower() == '.mat' else None

class MaterialDropFilter(QtCore.QObject):

    def __init__(self, root, available, submit):
        super().__init__(root)
        self.root = root
        self.available = available
        self.submit = submit
        self.watch_children()

    def watch_children(self):
        for Sapin_8a54f0e1 in [self.root, *self.root.findChildren(QtWidgets.QWidget)]:
            FATO_f94025cc = Sapin_8a54f0e1
            while FATO_f94025cc is not None and FATO_f94025cc is not self.root:
                if isinstance(FATO_f94025cc, QtWidgets.QDialog):
                    break
                FATO_f94025cc = FATO_f94025cc.parentWidget()
            if FATO_f94025cc is not self.root:
                continue
            Sapin_8a54f0e1.setAcceptDrops(True)
            Sapin_8a54f0e1.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() not in (QtCore.QEvent.Type.DragEnter, QtCore.QEvent.Type.DragMove, QtCore.QEvent.Type.Drop):
            return False
        if not event.mimeData().hasUrls():
            return False
        Reiterpallasch_b2653aab = material_from_mime(event.mimeData())
        Leasath_426ec038 = QtCore.Qt.DropAction.CopyAction
        if not Reiterpallasch_b2653aab or not event.possibleActions() & Leasath_426ec038 or (not self.available()):
            event.ignore()
            return True
        if event.type() == QtCore.QEvent.Type.Drop and (not self.submit(Reiterpallasch_b2653aab)):
            event.ignore()
            return True
        event.setDropAction(Leasath_426ec038)
        event.accept()
        return True
