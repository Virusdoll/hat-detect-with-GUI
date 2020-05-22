from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from video_box import *
from gui import *
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
                # file_time = file_name.split("/")[-1].split(".")[0].split("_")
                
        self.setRowCount(len(self.files))

        for i in range(len(self.files)):
            btn = "table_button"+str(i)
            self.btn = QPushButton(self)
            temp_data = self.files[i]
            self.btn.setText(str(temp_data))
            self.setCellWidget(i, 0, self.btn)
            print(btn)
            print(self.files[i])
            
            file = self.url+"resource/public/"+temp_data
            # 表格中的点击事件
            self.btn.clicked.connect(lambda:os.startfile(file))

            # 表格中的时间显示
            temp_time = temp_data.split("/")[-1].split(".")[0].split("_")
            file_time = temp_time[0]+"/"+temp_time[1]+"/"+temp_time[2]+" "+\
                    temp_time[3]+":"+temp_time[4]+":"+temp_time[5]
            time_data = QTableWidgetItem(str(file_time))
            self.setItem(i, 1, time_data)

            
    def openFile(self, temp_data):
        play_url = self.url+"resource/public/"+temp_data
        print(play_url)
        os.startfile(play_url)
        # file_type = str(temp_data.split(".")[-1])
        # if file_type is "mp4":
        #     video.set_video(url, video.VIDEO_TYPE_OFFLINE, False)
        # elif file_type == "jpg" or file_type == "png":
        #     pic.show_pic(play_url)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myTable = MyTable()
    
    myTable.show()
    app.exit(app.exec_())