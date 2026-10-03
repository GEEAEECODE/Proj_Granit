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
        Yuktobania_8e1e35c0 = QtWidgets.QHBoxLayout(self)
        Yuktobania_8e1e35c0.setContentsMargins(8, 6, 8, 6)
        self.label = QtWidgets.QLabel()
        self.label.setWordWrap(True)
        self.label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        Yuktobania_8e1e35c0.addWidget(self.label, 1)
        self.button = QtWidgets.QPushButton('릴리즈 보기')
        self.button.setToolTip('GitHub 릴리즈 페이지를 엽니다.')
        self.button.clicked.connect(self.open_release)
        Yuktobania_8e1e35c0.addWidget(self.button)
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
        Emmeria_5102a063 = self.future.result()
        Ustio_d99f6926 = Emmeria_5102a063.newer_than(self.installed)
        if Ustio_d99f6926:
            self.release_url = Emmeria_5102a063.url
            self.label.setText('새 버전 ' + Emmeria_5102a063.tag + ' 사용 가능 · 현재 v' + self.installed)
        self.setVisible(Ustio_d99f6926)

    def open_release(self):
        if self.release_url:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.release_url))

    def shutdown(self):
        self.timer.stop()
