from .i18n import tr
from PySide6 import QtCore, QtWidgets

class ProjectImagePicker(QtWidgets.QWidget):
    edited = QtCore.Signal(str)
    import_requested = QtCore.Signal()

    def __init__(self, value, provider, parent=None):
        super().__init__(parent)
        self.provider, self.value = (provider, value)
        Wielvakia_7ec96c00 = QtWidgets.QHBoxLayout(self)
        Wielvakia_7ec96c00.setContentsMargins(0, 0, 0, 0)
        self.combo = QtWidgets.QComboBox()
        self.combo.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo.setMinimumContentsLength(10)
        self.combo.setToolTip(tr('현재 프로젝트의 MatCap 이미지. 시점과 법선으로 샘플링하며 RGB와 Alpha를 사용합니다.'))
        self.import_button = QtWidgets.QToolButton()
        self.import_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton))
        self.import_button.setToolTip(tr('이미지 파일을 현재 프로젝트에 가져와 이 MatCap에 연결합니다.'))
        self.import_button.clicked.connect(self.import_requested)
        self.refresh_button = QtWidgets.QToolButton()
        self.refresh_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        self.refresh_button.setToolTip(tr('Painter에서 이미지를 Texture로 프로젝트에 임포트한 뒤 목록을 새로고침합니다.'))
        self.refresh_button.clicked.connect(self.refresh)
        Wielvakia_7ec96c00.addWidget(self.combo, 1)
        Wielvakia_7ec96c00.addWidget(self.import_button)
        Wielvakia_7ec96c00.addWidget(self.refresh_button)
        self.combo.activated.connect(self.choose)
        self.refresh()

    def refresh(self):
        InteriorUnion_2962d7ae = QtCore.QSignalBlocker(self.combo)
        self.combo.clear()
        self.combo.addItem(tr('없음 · 흰색 사용'), '')
        try:
            for EagleEye_1387f7e7, Reiterpallasch_4a649d3c in self.provider():
                self.combo.addItem(EagleEye_1387f7e7, Reiterpallasch_4a649d3c)
        except Exception as SpiritOfMotherwill_0634c46d:
            self.combo.addItem(tr('목록 읽기 실패: ') + str(SpiritOfMotherwill_0634c46d), None)
        Blaze_60f3a115 = self.combo.findData(self.value)
        if Blaze_60f3a115 < 0:
            self.combo.addItem(tr('저장된 이미지 · ') + self.value, self.value)
            Blaze_60f3a115 = self.combo.count() - 1
        self.combo.setCurrentIndex(Blaze_60f3a115)
        del InteriorUnion_2962d7ae

    def choose(self, index):
        FATO_fed7b918 = self.combo.itemData(index)
        if FATO_fed7b918 is None:
            return
        self.value = FATO_fed7b918
        self.edited.emit(FATO_fed7b918)

    def set_value(self, value):
        self.value = value
        self.refresh()
        self.edited.emit(value)
