from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from video_box import *
from gui import *
import sys
import os

class MyLog(QTableWidget):
    url_base = os.path.dirname(os.path.abspath(__file__))
    files = []

    def __init__(self,parent=None,url_base = url_base,files = files):
        super(MyLog, self).__init__(parent)

        url = url_base
        for i in url_base:
            if(i == "\\"):
                url = url + "/"
        self.url = url
        self.files = files
        self.clickItem = None
        self.setWindowTitle("测试日志")
        self.resize(800, 600)

        #设置表格有1列
        self.setColumnCount(1)

        # 设置表头名称
        # self.setColumnWidth(1, 350)
        self.setColumnWidth(0, 780)
        self.setHorizontalHeaderLabels(["日志"])
        self.table_sitting()

    def table_sitting(self):

        g = os.walk(r""+self.url+"resource/logs/")  

        for path,dir_list,file_list in g:  
            for file_name in file_list:  
                file_name = file_name.split("/")[-1]
                self.files.append(file_name)
                
        self.setRowCount(len(self.files))

        for i in range(len(self.files)):
            btn = "table_button"+str(i)
            self.btn = QPushButton(self)
            temp_data = self.files[i]
            self.btn.setText(str(temp_data))
            self.setCellWidget(i, 0, self.btn)
            file = self.url+"resource/logs/"+temp_data
            # 表格中的点击事件
            self.btn.clicked.connect(lambda:os.startfile(file)) 
            

    def openFile(self, temp_data):
        file = self.url+"resource/logs/"+temp_data
        os.startfile(file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myLog = MyLog()
    myLog.show()
    app.exit(app.exec_())