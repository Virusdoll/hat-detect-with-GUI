import time
import sys


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *
from HatDetector import *
class VideoBox(QWidget):

    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2
    url_base = os.path.dirname(os.path.abspath(__file__))
    video_url = ""
    url=""
    new_url = ""

    def __init__(self, video_url="",url_base = url_base,video_type=VIDEO_TYPE_OFFLINE, auto_play=False):
        QWidget.__init__(self)
        
        self.hatDetector = HatDetector()

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

        self.new_url = ""
        # 组件展示
        self.pictureLabel = QLabel(self)
        self.pictureLabel.setText("    显示视频")
        init_image = QPixmap(self.url+"resource/hat.jpeg").scaled(self.width(), self.height())
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
            self.play_video()            
        elif button==QMessageBox.Cancel:  
             self.res.setText("上传失败。请重新选择视频！")   
        else:  
            return  

    # 上传文件进行检测并播放结果视频文件
    def play_video(self):
        v_type = str(self.video_url.split(".")[-1])
        time_now = time.strftime("%Y%m%d%H%M%S", time.localtime())
        # 新视频的url传给self.new_url
        self.new_url = self.url + "resource/public/" + time_now + v_type
        # 缓冲图片
        loading = QPixmap(self.url+"resource/loading.gif").scaled(self.width(), self.height())
        self.pictureLabel.setPixmap(loading)
        # 检测
        self.hatDetector.detectVideoFile(self.video_url, self.new_url)
        # 设置播放文件为测试结果文件
        self.set_video(self.new_url, VideoBox.VIDEO_TYPE_OFFLINE, False)

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

    # 设置播放文件
    def set_video(self, url, video_type=VIDEO_TYPE_OFFLINE, auto_play=False):
        self.reset()
        self.video_url = url
        self.video_type = video_type
        self.auto_play = auto_play
        self.set_timer_fps()
        if self.auto_play:
            self.switch_video()

    # 开始播放
    def play(self):
        if self.video_url == "" or self.video_url is None:
            return
        if not self.playCapture.isOpened():
            self.playCapture.open(self.video_url)
        self.timer.start()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.status = VideoBox.STATUS_PLAYING

    # 暂停播放
    def stop(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.playCapture.isOpened():
            self.timer.stop()
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.status = VideoBox.STATUS_PAUSE

    # 重新播放
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
    