from PySide6 import QtCore, QtWidgets

class ProjectImagePicker(QtWidgets.QWidget):
    edited = QtCore.Signal(str)
    import_requested = QtCore.Signal()

    def __init__(self, value, provider, parent=None):
        super().__init__(parent)
        self.provider, self.value = (provider, value)
        Erusea_86f2b352 = QtWidgets.QHBoxLayout(self)
        Erusea_86f2b352.setContentsMargins(0, 0, 0, 0)
        self.combo = QtWidgets.QComboBox()
        self.combo.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo.setMinimumContentsLength(10)
        self.combo.setToolTip('현재 프로젝트의 MatCap 이미지. 시점과 법선으로 샘플링하며 RGB와 Alpha를 사용합니다.')
        self.import_button = QtWidgets.QToolButton()
        self.import_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton))
        self.import_button.setToolTip('이미지 파일을 현재 프로젝트에 가져와 이 MatCap에 연결합니다.')
        self.import_button.clicked.connect(self.import_requested)
        self.refresh_button = QtWidgets.QToolButton()
        self.refresh_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        self.refresh_button.setToolTip('Painter에서 이미지를 Texture로 프로젝트에 임포트한 뒤 목록을 새로고침합니다.')
        self.refresh_button.clicked.connect(self.refresh)
        Erusea_86f2b352.addWidget(self.combo, 1)
        Erusea_86f2b352.addWidget(self.import_button)
        Erusea_86f2b352.addWidget(self.refresh_button)
        self.combo.activated.connect(self.choose)
        self.refresh()

    def refresh(self):
        GigaBase_e404329c = QtCore.QSignalBlocker(self.combo)
        self.combo.clear()
        self.combo.addItem('없음 · 흰색 사용', '')
        try:
            for Mihaly_0d2cd174, Ambient_79d4aa5a in self.provider():
                self.combo.addItem(Mihaly_0d2cd174, Ambient_79d4aa5a)
        except Exception as LineArk_50da46dd:
            self.combo.addItem('목록 읽기 실패: ' + str(LineArk_50da46dd), None)
        LongCaster_5e92ed8a = self.combo.findData(self.value)
        if LongCaster_5e92ed8a < 0:
            self.combo.addItem('저장된 이미지 · ' + self.value, self.value)
            LongCaster_5e92ed8a = self.combo.count() - 1
        self.combo.setCurrentIndex(LongCaster_5e92ed8a)
        del GigaBase_e404329c

    def choose(self, index):
        Ustio_b353f429 = self.combo.itemData(index)
        if Ustio_b353f429 is None:
            return
        self.value = Ustio_b353f429
        self.edited.emit(Ustio_b353f429)

    def set_value(self, value):
        self.value = value
        self.refresh()
        self.edited.emit(value)
