import sys
import qdarkstyle
import os
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import json




class LandUI(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

        self.selectedVariables = ""

    def initUI(self):

        self.filepath1 = ""
        self.filepath2 = ""

        self.totalVLayout = QVBoxLayout(self)
        self.totalVLayout.setObjectName(u"totalVLayout")
        self.totalVLayout.setContentsMargins(20, 20, 20, 20)
        self.totalVLayout.setSpacing(15)

        self.logoTitleHLayout = QHBoxLayout()
        self.logoTitleHLayout.setSpacing(10)
        self.logoTitleHLayout.setContentsMargins(20, 20, 20, 20)
        self.logoTitleHLayout.setObjectName(u"fileBrowse1HLayout")

        self.lblLogo = QLabel(self)
        pixmap = QPixmap("static/resources/logo_white.png")
        self.lblLogo.setPixmap(pixmap)
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setMaximumHeight(50)
        self.lblLogo.setMaximumWidth(300)
        self.logoTitleHLayout.addWidget(self.lblLogo)

        self.lblTitle = QLabel(self)
        self.lblTitle.setText("Characterization\nof Health Conditions\nfor Electrical Assets")
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.lblTitle.setFont(QFont("Arial", 24))
        self.logoTitleHLayout.addWidget(self.lblTitle)

        self.totalVLayout.addLayout(self.logoTitleHLayout)

        self.btnsHLayout = QHBoxLayout()
        self.btnsHLayout.setObjectName(u"totalVLayout")
        self.btnsHLayout.setContentsMargins(20, 20, 20, 20)
        self.btnsHLayout.setSpacing(15)

        self.btn1 = QPushButton()
        self.btn1.setObjectName(u"btn1")
        self.btn1.setFixedHeight(90)
        self.btn1.setText("Condition Characterization")
        self.btn1.clicked.connect(self.btn1_clicked)
        self.btnsHLayout.addWidget(self.btn1)

        self.btn2 = QPushButton()
        self.btn2.setObjectName(u"btn2")
        self.btn2.setFixedHeight(90)
        self.btn2.setText("Condition Monitoring for Transformers")
        self.btn2.clicked.connect(self.btn2_clicked)
        self.btnsHLayout.addWidget(self.btn2)
        self.totalVLayout.addLayout(self.btnsHLayout)

        spacerItem = QtWidgets.QSpacerItem(32, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.manualHLayout = QHBoxLayout()
        self.manualHLayout.setContentsMargins(0, 0, 20, 20)
        self.manualLabel = QLabel("User Manual")
        self.manualLabel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.manualLabel.setStyleSheet("QLabel{font-size:20px; font-weight:bold;}")
        self.manualHLayout.addItem(spacerItem)
        self.manualHLayout.addWidget(self.manualLabel)
        self.manualLabel.mousePressEvent  = self.manual_clicked

        self.totalVLayout.addLayout(self.manualHLayout)


        self.setGeometry(0, 0, 800, 340)
        self.setWindowTitle('ATTEST Toolbox')
        self.show()


    @pyqtSlot()
    def btn1_clicked(self):
        import Scripts.Condition_characterization_app as wp1
        print("btn1")
        form1 = wp1.Example()
        form1.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        form1.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        form1.exec_()

    @pyqtSlot()
    def btn2_clicked(self):
        import Scripts.Condition_monitoring_app as wp2
        print("btn2")
        form2 = wp2.Example()
        form2.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        form2.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        form2.exec_()

    @pyqtSlot()
    def manual_clicked(self, event):
        os.system("start ../../Manual.pdf")

def main():
    app = QApplication(sys.argv)
    ex = LandUI()
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
