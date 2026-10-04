from .i18n import tr
from PySide6 import QtCore, QtGui, QtWidgets
from . import updates

class UpdateNotice(QtWidgets.QWidget):

    def __init__(self, installed, parent=None):
        super().__init__(parent)
        self.installed = installed
        self.future = None
        self.release_url = ''
        self.setObjectName('GranitUpdateNotice')
        self.setStyleSheet('#GranitUpdateNotice { background-color: #443a24; border: 1px solid #897343; border-radius: 3px; }')
        Erusea_a6857961 = QtWidgets.QHBoxLayout(self)
        Erusea_a6857961.setContentsMargins(8, 6, 8, 6)
        self.label = QtWidgets.QLabel()
        self.label.setWordWrap(True)
        self.label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        Erusea_a6857961.addWidget(self.label, 1)
        self.button = QtWidgets.QPushButton(tr('릴리즈 보기'))
        self.button.setToolTip(tr('GitHub 릴리즈 페이지를 엽니다.'))
        self.button.clicked.connect(self.open_release)
        Erusea_a6857961.addWidget(self.button)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self.poll)
        self.hide()

    def start(self):
        if self.future is not None:
            return
        self.future = updates.start_once()
        if self.future.done():
            self.poll()
        else:
            self.timer.start()

    def poll(self):
        if self.future is None or not self.future.done():
            return
        self.timer.stop()
        Wielvakia_5aedda5b = self.future.result()
        Sapin_cafbbf61 = Wielvakia_5aedda5b.newer_than(self.installed)
        if Sapin_cafbbf61:
            self.release_url = Wielvakia_5aedda5b.url
            self.label.setText(tr('새 버전 ') + Wielvakia_5aedda5b.tag + tr(' 사용 가능 · 현재 v') + self.installed)
        self.setVisible(Sapin_cafbbf61)

    def open_release(self):
        if self.release_url:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.release_url))

    def retranslate(self):
        self.button.setText(tr('릴리즈 보기'))
        self.button.setToolTip(tr('GitHub 릴리즈 페이지를 엽니다.'))
        self.poll()

    def shutdown(self):
        self.timer.stop()
