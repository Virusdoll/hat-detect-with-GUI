from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os

class MyButton(QPushButton):
    def __init__(self, traget_dir, button_name):
        QPushButton.__init__(self)
        self.__traget_dir = traget_dir
        self.__button_name = button_name
        self.setText(self.__button_name)
        self.clicked.connect(lambda:self.openFile(self.__traget_dir))
    
    def openFile(self, file):
        print(file)
        if sys.platform == "win32":
            os.startfile(file)
        else:
            subprocess.call(["xdg-open", file])


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
            temp_data = self.files[i]
            file = self.url+"resource/logs/"+temp_data
            tmp_button = MyButton(file, str(temp_data))
            self.setCellWidget(i, 0, tmp_button)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myLog = MyLog()
    myLog.show()
    app.exit(app.exec_())