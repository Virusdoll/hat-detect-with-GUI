import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui import *
from video_box import *
from result import *

class indexPage(QWidget):
    url_base = os.path.dirname(os.path.abspath(__file__))
    # show_sub_win_signal = pyqtSignal()
    
    def __init__(self, url_base = url_base):
        QWidget.__init__(self)

        # 相对路径一直报错，所以获取绝对路径
        url = url_base
        for i in url_base:
            if(i == "\\"):
                url = url + "/"

        # 主窗口属性设置
        self.url = url;
        self.resize(800, 600)
        self.setWindowTitle("WKD安全帽识别")

        # 主窗口背景图片设置
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap(url+"/resource/back.png")))  
        self.setPalette(palette)

        # 图片上传按钮
        self.pic_win = QPushButton(self)
        self.pic_win.setText("图片上传")
        self.pic_win.setFixedSize(175, 125)
        self.pic_win.move(150, 125)

        # 透明度设置
        op1 = QtWidgets.QGraphicsOpacityEffect()
        op1.setOpacity(0.96)               
        self.pic_win.setGraphicsEffect(op1)

        # 视频上传按钮
        self.video_win = QPushButton(self)
        self.video_win.setText("视频上传")
        self.video_win.setFixedSize(175, 125)
        self.video_win.move(475, 125)
        op2 = QtWidgets.QGraphicsOpacityEffect()
        op2.setOpacity(0.9)               
        self.video_win.setGraphicsEffect(op2)
        
        # 测试结果按钮
        self.res_win = QPushButton(self)
        self.res_win.setText("结果记录")
        self.res_win.setFixedSize(175, 125)
        self.res_win.move(150, 350)
        op3 = QtWidgets.QGraphicsOpacityEffect()
        op3.setOpacity(0.8)               
        self.res_win.setGraphicsEffect(op3)
        
        # 历史日志按钮
        self.log_win = QPushButton(self)
        self.log_win.setText("历史日志")
        self.log_win.setFixedSize(175, 125)
        self.log_win.move(475, 350)
        op4 = QtWidgets.QGraphicsOpacityEffect()
        op4.setOpacity(0.8) 
        self.log_win.setGraphicsEffect(op4)
        
        # 统一设置按钮样式
        self.setStyleSheet("QPushButton{font-size:20px;font-weight:bold;font-family:宋体;}\
            QPushButton:hover{background-color:#6BDEFF;}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my = indexPage()
    v_win = VideoBox()
    p_win = picture() 
    r_win = MyTable()
    l_win = MyLog()
    # 图片上传按钮的点击函数，跳转至图片上传页 
    my.pic_win.clicked.connect(p_win.show)
    # 视频上传按钮的点击函数，跳转至视频上传页
    my.video_win.clicked.connect(v_win.show)
    # 测试结果按钮的点击函数，跳转至测试结果页
    my.res_win.clicked.connect(r_win.show)
    # 历史日志按钮的点击函数，跳转至历史日志页
    my.log_win.clicked.connect(l_win.show)
    my.show()
    sys.exit(app.exec_())
