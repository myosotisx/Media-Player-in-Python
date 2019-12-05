import sys
import socket
import threading
import os

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, pyqtSignal, QTimer

from mainwindow import Ui_MainWindow

import util
import rtp
from rtp import rtp_packet
from rtsp import rtsp
from ts import ts


class Player(QMainWindow, Ui_MainWindow):
    play_signal = pyqtSignal(object)
    IDLE = 0
    READY = 1
    PLAY = 2

    def __init__(self):
        super(Player, self).__init__()
        # init UI
        self.setupUi(self)
        self.media_player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)
        self.centralwidget.layout().insertWidget(0, self.video_widget)
        self.playBtn.clicked.connect(self.play_media)
        self.pauseBtn.clicked.connect(self.pause_media)
        self.stopBtn.clicked.connect(self.stop_media)
        self.progressSlider.originMouseMoveEvent = self.progressSlider.mouseMoveEvent
        self.progressSlider.mouseMoveEvent = self.progressSlider_mouse_move
        self.progressSlider.sliderReleased.connect(self.reposition_media)
        self.progressSlider.setDisabled(True)

        self.urlLineEdit.setText('rtsp://127.0.0.1:57501/1')

        # init component
        self.timer = QTimer(self)

        # init sockets
        self.client_rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_rtsp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.client_rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_rtp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.client_rtcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_rtcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # init thread
        self.client_rtp_thread = None
        self.play_event = None

        # init client parameters
        self.seq = 0
        self.client_rtp_port = None
        self.client_rtcp_port = None
        self.client_session_id = None
        self.url = None
        self.status = self.IDLE
        self.media_duration = 0
        self.current_time = 0
        self.init_end_time_label()
        self.set_play_time()

        # init cache file
        self.client_root = os.path.split(os.path.abspath(__file__))[0]
        self.cache_filename = os.path.join(self.client_root, 'Cache/tmp.ts')
        self.file = None

    def setup_play(self, url):
        url_tup = util.parse_url(url)
        if not url_tup:
            QMessageBox.warning(self, 'Warning', 'Invalid URL.')
            return -1
        ip = url_tup[0]
        port = int(url_tup[1])
        path = url_tup[2]
        try:
            self.client_rtsp_socket.connect((ip, port))
        except Exception as e:
            QMessageBox.warning(self, 'Warning', 'Error: connect to media server failed.')
            return -1

        # send OPTIONS
        request_dict = {'CSeq': str(self.seq)}
        request = rtsp.generate_request('OPTIONS', url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.seq += 1
        # send DESCRIBE
        request_dict = {'CSeq': str(self.seq), 'Accept': 'application/sdp'}
        request = rtsp.generate_request('DESCRIBE', url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.client_rtp_port = util.match_rtp_port(response)
        if not self.client_rtp_port:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: can not specify RTP port.')
            return -1
        self.client_rtcp_port = self.client_rtp_port+1
        self.seq += 1
        # setup RTP and RTCP socket
        self.client_rtp_socket.bind(('127.0.0.1', self.client_rtp_port))
        self.client_rtcp_socket.bind(('127.0.0.1', self.client_rtcp_port))
        self.status = self.READY
        # send SETUP
        request_dict = {'CSeq': str(self.seq), 'Transport': 'RTP/AVP;unicast;client_port=%d-%d' % (self.client_rtp_port,
                                                                                                   self.client_rtcp_port)}
        request = rtsp.generate_request('SETUP', url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.client_session_id = int(response_dict.get('Session'))
        self.seq += 1
        self.status = self.READY
        # send PLAY
        request_dict = {'CSeq': str(self.seq), 'Session': self.client_session_id, 'Range': 'npt=0.000-'}
        request = rtsp.generate_request('PLAY', url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.seq += 1
        self.current_time, self.media_duration = util.match_media_time(response)
        return 0

    def recv_stream(self, cache_filename):
        cur_seq = 0
        self.file = open(cache_filename, 'wb')
        while True:
            if self.status == self.READY:
                self.play_event.wait()
            if self.status == self.IDLE:
                break
            try:
                data = self.client_rtp_socket.recv(rtp.TS_RTP_PACKET_SIZE)
            except:
                continue
            seq = rtp_packet.get_seq(data)
            if seq and seq < cur_seq:
                continue
            cur_seq = seq
            payload = rtp_packet.get_payload(data)
            self.file.write(payload)
        if self.file:
            self.file.close()

    def start_play(self):
        self.init_progress_slider()
        self.init_end_time_label()
        self.timer.stop()
        self.timer.disconnect()
        self.timer.timeout.connect(self.update_play_time)
        self.timer.start(1000)
        self.progressSlider.setDisabled(False)
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.cache_filename)))
        self.media_player.play()

    def progressSlider_mouse_move(self, event):
        self.progressSlider.originMouseMoveEvent(event)
        self.current_time = self.progressSlider.value()
        self.set_play_time()

    def init_progress_slider(self):
        self.progressSlider.setMinimum(0)
        self.progressSlider.setMaximum(self.media_duration)

    def init_end_time_label(self):
        self.endTimeLabel.setText('%d:%02d' % (self.media_duration // 60, self.media_duration % 60))

    def set_play_time(self):
        if self.current_time >= self.media_duration:
            self.stop_media()
        self.progressSlider.setValue(self.current_time)
        current_time = self.current_time
        self.curTimeLabel.setText('%d:%02d' % (current_time // 60, current_time % 60))

    def update_play_time(self):
        self.current_time += 1
        self.set_play_time()

    def closeEvent(self, event):
        if self.status != self.IDLE:
            self.stop_media()

    def play_media(self):
        if self.status == self.IDLE:
            # setup and play
            url = self.urlLineEdit.text()
            res = self.setup_play(url)
            if res != -1:
                # remove cache file
                if os.path.exists(self.cache_filename):
                    os.remove(self.cache_filename)
                self.url = url
                self.client_rtp_thread = threading.Thread(target=self.recv_stream, args=(self.cache_filename,))
                self.status = self.PLAY
                self.play_event = threading.Event()
                self.client_rtp_thread.start()
                self.timer.timeout.connect(self.start_play)
                self.timer.start(3000)
        elif self.status == self.READY:
            # send PLAY
            request_dict = {'CSeq': str(self.seq), 'Session': self.client_session_id, 'Range': 'npt=now-'}
            request = rtsp.generate_request('PLAY', self.url, request_dict)
            self.client_rtsp_socket.send(request.encode())
            response = self.client_rtsp_socket.recv(1024).decode()
            if rtsp.get_status_code(response) != 200:
                # self.close_rtsp_connection()
                self.destroy_connection()
                QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
                return
            response_dict = rtsp.get_response_dict(response)
            if int(response_dict.get('CSeq')) != self.seq:
                # self.close_rtsp_connection()
                self.destroy_connection()
                QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
                return
            self.seq += 1
            # resume
            self.status = self.PLAY
            self.play_event.set()
            self.media_player.play()
            self.timer.start(1000)
        else:
            return

    def pause_media(self):
        if self.status != self.PLAY:
            return
        self.media_player.pause()
        self.timer.stop()
        self.play_event.clear()
        self.status = self.READY
        # send PAUSE
        request_dict = {'CSeq': str(self.seq), 'Session': self.client_session_id}
        request = rtsp.generate_request('PAUSE', self.url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.seq += 1

    def stop_media(self):
        if self.status == self.IDLE:
            return
        request_dict = {'CSeq': str(self.seq), 'Session': self.client_session_id}
        request = rtsp.generate_request('TEARDOWN', self.url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            # self.close_rtsp_connection()
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return
        self.seq += 1
        self.destroy_connection()

    def reposition_media(self):
        if self.status == self.IDLE:
            return
        self.pause_media()
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())
        self.timer.stop()
        self.timer.disconnect()
        self.play_event.clear()
        self.status = self.READY
        self.current_time = self.progressSlider.value()
        self.set_play_time()

        # reset socket
        self.client_rtp_socket.shutdown(socket.SHUT_RDWR)
        self.client_rtp_socket.close()
        self.client_rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_rtp_socket.bind(('127.0.0.1', self.client_rtp_port))

        # send PLAY
        request_dict = {'CSeq': str(self.seq), 'Session': self.client_session_id, 'Range': 'npt=%.3f-%.3f' %
                                                                                           (self.current_time,
                                                                                            self.media_duration)}
        request = rtsp.generate_request('PLAY', self.url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            self.destroy_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return
        self.seq += 1
        self.current_time, self.media_duration = util.match_media_time(response)

        # reset cache file
        self.file.close()
        os.remove(self.cache_filename)
        self.file = open(self.cache_filename, 'wb')
        # resume
        self.status = self.PLAY
        self.play_event.set()
        self.timer.timeout.connect(self.start_play)
        self.timer.start(3000)

    def destroy_connection(self):
        # reset status
        self.status = self.IDLE

        # reset player
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())

        # reset RTSP socket
        self.client_rtsp_socket.shutdown(socket.SHUT_RDWR)
        self.client_rtsp_socket.close()
        self.client_rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_rtsp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # reset RTP socket
        self.client_rtp_socket.shutdown(socket.SHUT_RDWR)
        self.client_rtp_socket.close()
        self.client_rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_rtp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # reset RTCP socket
        self.client_rtcp_socket.shutdown(socket.SHUT_RDWR)
        self.client_rtcp_socket.close()
        self.client_rtcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_rtcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # reset thread
        self.client_rtp_thread = None
        self.play_event = None

        # reset timer
        self.timer.stop()
        self.timer.disconnect()

        # reset client parameters
        self.seq = 0
        self.client_rtp_port = None
        self.client_rtcp_port = None
        self.client_session_id = None
        self.url = None
        self.media_duration = 0
        self.current_time = 0
        self.init_end_time_label()
        self.set_play_time()

        # reset UI
        self.progressSlider.setDisabled(True)

        # reset cache file
        self.file = None


if __name__ == "__main__":

    app = QApplication(sys.argv)
    font = QFont('Microsoft YaHei', 10)
    app.setFont(font)
    player = Player()
    player.show()
    sys.exit(app.exec_())
