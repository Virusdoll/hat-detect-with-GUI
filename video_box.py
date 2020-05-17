import time
import sys


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *
from HatDetector import HatDetector

class VideoBox(QWidget):

    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2
    url_base = os.path.dirname(os.path.abspath(__file__))
    video_url = ""
    url=""

    def __init__(self, video_url="",url_base = url_base,video_type=VIDEO_TYPE_OFFLINE, auto_play=False):
        QWidget.__init__(self)
        # self.resize(900, 600)
        self.video_url = video_url
        self.res = QLabel(self)
        self.res.setText("")
        self.res.setFixedSize(600, 15)

        self.video_type = video_type  # 0: offline  1: realTime
        self.auto_play = auto_play
        self.status = self.STATUS_INIT  # 0: init 1:playing 2: pause
        
        self.url = url_base
        for i in url_base:
            if(i == "\\"):
                self.url = self.url + "/"

        # 组件展示
        self.pictureLabel = QLabel(self)
        self.pictureLabel.setText("    显示视频")
        # self.pictureLabel.setFixedSize(1000, 600)
        # self.pictureLabel.setFixedSize(self.width(), self.height())
        init_image = QPixmap("resource/hat.jpeg").scaled(self.width(), self.height())
        self.pictureLabel.setPixmap(init_image)

        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.switch_video)

        chooseBtn = QPushButton(self)
        chooseBtn.setText("选择视频")
        chooseBtn.move(10, 10)
        chooseBtn.setStyleSheet("QPushButton:chooseBtn{background:#33D1FF;}")
        chooseBtn.clicked.connect(self.openimage)

        uploadBtn = QPushButton(self)
        uploadBtn.setText("上传并测试")
        uploadBtn.move(10, 50)
        # uploadBtn.setStyleSheet("QPushButton{background:#33D1FF;}")
        uploadBtn.clicked.connect(self.uploadimage)

        control_box = QHBoxLayout()
        control_box.setContentsMargins(0, 0, 0, 0)
        control_box.addWidget(self.playButton)

        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)

        self.setLayout(layout)
        # timer 设置
        self.timer = VideoTimer()
        self.timer.timeSignal.signal[str].connect(self.show_video_images)

        # video 初始设置
        self.playCapture = VideoCapture()
        if self.video_url != "":
            self.set_timer_fps()
            if self.auto_play:
                self.switch_video()
            # self.videoWriter = VideoWriter('*.mp4', VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, size)
    
    def openimage(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开视频", "", "*.mp4;;All Files(*)")
        init_video = QtGui.QPixmap(imgName).scaled(self.pictureLabel.width(), self.pictureLabel.height())
        self.pictureLabel.setPixmap(init_video)
        self.set_video(imgName, VideoBox.VIDEO_TYPE_OFFLINE, False)
        self.video_url = imgName

    def uploadimage(self):
        button=QMessageBox.question(self,"Question",  
                                    self.tr("确认上传?"),  
                                    QMessageBox.Ok|QMessageBox.Cancel,  
                                    QMessageBox.Ok)  
        if button==QMessageBox.Ok:  
            self.res.setText("上传成功！请等待检测结果！")             
            # 调用检测函数,上传的图片地址为video_url
            # time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())
            # new_url = self.url+"resource/"+time_now+".mp4"
            # hatDetector = HatDetector()
            # hatDetector.detectVideoFile(self.video_url, new_url)
            # resPic = QtGui.QPixmap(self.video_url).scaled(self.label.width(), self.label.height())
            # self.label.setPixmap(resPic) 
        elif button==QMessageBox.Cancel:  
             self.res.setText("上传失败。请重新选择视频！")   
        else:  
            return  

    def reset(self):
        self.timer.stop()
        self.playCapture.release()
        self.status = VideoBox.STATUS_INIT
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def set_timer_fps(self):
        self.playCapture.open(self.video_url)
        print('url',self.video_url)
        fps = self.playCapture.get(CAP_PROP_FPS)
        print('fps',fps)
        self.timer.set_fps(fps)
        self.playCapture.release()

    def set_video(self, url, video_type=VIDEO_TYPE_OFFLINE, auto_play=False):
        self.reset()
        self.video_url = url
        self.video_type = video_type
        self.auto_play = auto_play
        self.set_timer_fps()
        if self.auto_play:
            self.switch_video()

    def play(self):
        if self.video_url == "" or self.video_url is None:
            return
        if not self.playCapture.isOpened():
            self.playCapture.open(self.video_url)
        self.timer.start()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.status = VideoBox.STATUS_PLAYING

    def stop(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.playCapture.isOpened():
            self.timer.stop()
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.status = VideoBox.STATUS_PAUSE

    def re_play(self):
        if self.video_url == "" or self.video_url is None:
            return
        self.playCapture.release()
        self.playCapture.open(self.video_url)
        self.timer.start()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.status = VideoBox.STATUS_PLAYING

    def show_video_images(self):
        if self.playCapture.isOpened():
            success, frame = self.playCapture.read()
            if success:
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cvtColor(frame, COLOR_BGR2RGB)
                elif frame.ndim == 2:
                    rgb = cvtColor(frame, COLOR_GRAY2BGR)

                temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
                temp_pixmap = QPixmap.fromImage(temp_image)
                self.pictureLabel.setPixmap(temp_pixmap)
            else:
                print("read failed, no frame data")
                success, frame = self.playCapture.read()
                if not success and self.video_type is VideoBox.VIDEO_TYPE_OFFLINE:
                    print("play finished")  # 判断本地文件播放完毕
                    self.reset()
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                return
        else:
            print("open file or capturing device error, init again")
            self.reset()

    def switch_video(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.status is VideoBox.STATUS_INIT:
            self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        elif self.status is VideoBox.STATUS_PLAYING:
            self.timer.stop()
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        elif self.status is VideoBox.STATUS_PAUSE:
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        self.status = (VideoBox.STATUS_PLAYING,
                       VideoBox.STATUS_PAUSE,
                       VideoBox.STATUS_PLAYING)[self.status]


class Communicate(QObject):

    signal = pyqtSignal(str)


class VideoTimer(QThread):

    def __init__(self, frequent=20.0):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            print(self.frequent)
            time.sleep(1.0 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps

if __name__ == "__main__":
    mapp = QApplication(sys.argv)
    mw = VideoBox()
    mw.show()
    sys.exit(mapp.exec_())
    