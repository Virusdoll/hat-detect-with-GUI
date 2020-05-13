import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class picture(QWidget):
    def __init__(self):
        super(picture, self).__init__()

        self.resize(800, 600)
        self.setWindowTitle("label显示图片")
        
        self.label = QLabel(self)
        self.label.setText("   显示图片")
        self.label.setFixedSize(600, 400)
        self.label.move(100, 60)

        self.label.setStyleSheet("QLabel{background:white;}"
                                 "QLabel{color:black;font-size:20px;font-weight:bold;font-family:宋体;}"
                                 )

        chooseBtn = QPushButton(self)
        chooseBtn.setText("选择图片")
        chooseBtn.move(100, 500)
        chooseBtn.setStyleSheet("QPushButton:chooseBtn{background:#33D1FF;}")
        chooseBtn.clicked.connect(self.openimage)

        uploadBtn = QPushButton(self)
        uploadBtn.setText("上传图片")
        uploadBtn.move(500, 500)
        # uploadBtn.setStyleSheet("QPushButton{background:#33D1FF;}")
        uploadBtn.clicked.connect(self.uploadimage)

    def openimage(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        jpg = QtGui.QPixmap(imgName).scaled(self.label.width(), self.label.height())
        self.label.setPixmap(jpg)

    def uploadimage(self):
        button=QMessageBox.question(self,"Question",  
                                    self.tr("确认上传?"),  
                                    QMessageBox.Ok|QMessageBox.Cancel,  
                                    QMessageBox.Ok)  
        if button==QMessageBox.Ok:  
            self.label.setText("Question button/Ok")  
        elif button==QMessageBox.Cancel:  
            self.label.setText("Question button/Cancel")  
        else:  
            return  


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my = picture()
    my.show()
    sys.exit(app.exec_())
