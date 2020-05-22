from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from log import MyButton
import sys
import os

class MyTable(QTableWidget):
    url_base = os.path.dirname(os.path.abspath(__file__))
    files = []

    def __init__(self,parent=None,url_base = url_base,files = files):
        super(MyTable, self).__init__(parent)

        url = url_base
        for i in url_base:
            if(i == "\\"):
                url = url + "/"
        self.url = url
        self.files = files
        self.clickItem = None
        self.setWindowTitle("测试结果")
        self.resize(800, 600)

        #设置表格有2列
        self.setColumnCount(2)

        # 设置2列宽度和表头名称
        self.setColumnWidth(1, 350)
        self.setColumnWidth(0, 415)
        self.setHorizontalHeaderLabels(["视频/图片", "测试时间"])
        self.table_sitting()

    def table_sitting(self):

        g = os.walk(r""+self.url+"resource/public/")  

        for path,dir_list,file_list in g:  
            for file_name in file_list:  
                file_name = file_name.split("/")[-1]
                self.files.append(file_name)
                
        self.setRowCount(len(self.files))

        for i in range(len(self.files)):
            temp_data = self.files[i]
            file = self.url+"resource/public/"+temp_data
            tmp_button = MyButton(file, str(temp_data))
            self.setCellWidget(i, 0, tmp_button)


            # 表格中的时间显示
            temp_time = temp_data.split("/")[-1].split(".")[0].split("_")
            file_time = temp_time[0]+"/"+temp_time[1]+"/"+temp_time[2]+" "+\
                    temp_time[3]+":"+temp_time[4]+":"+temp_time[5]
            time_data = QTableWidgetItem(str(file_time))
            self.setItem(i, 1, time_data)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myTable = MyTable()
    myTable.show()
    app.exit(app.exec_())