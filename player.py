import sys
import socket
import threading
import time
import os

from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QTimer

from mainwindow import Ui_MainWindow

import util
import rtp
from rtp import rtp_packet
from rtsp import rtsp


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
        self.video_window = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_window)
        self.verticalLayout.insertWidget(0, self.video_window)
        self.playBtn.clicked.connect(self.play_media)
        self.pauseBtn.clicked.connect(self.pause_media)
        self.stopBtn.clicked.connect(self.stop_media)

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

        # init cache file
        self.cache_filename = r'C:\Users\Myosotis\Videos\tmp.ts'

    def close_rtsp_connection(self):
        self.client_rtsp_socket.shutdown(socket.SHUT_RDWR)
        self.client_rtsp_socket.close()

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
            print(e)
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
        return 0

    def recv_stream(self, cache_filename):
        cur_seq = 0
        file = open(cache_filename, 'wb')
        while True:
            try:
                data = self.client_rtp_socket.recv(rtp.TS_RTP_PACKET_SIZE)
            except:
                break
            seq = rtp_packet.get_seq(data)
            if seq and seq < cur_seq:
                print('Packet loss.')
                continue
            cur_seq = seq
            payload = rtp_packet.get_payload(data)
            if self.status == self.READY:
                self.play_event.wait()
            if self.status == self.IDLE:
                break
            file.write(payload)
        print('Exit RTP thread.')
        file.close()

    def start_play(self):
        self.timer.disconnect()
        self.media_player.play()

    def closeEvent(self, event):
        self.media_player.stop()
        self.status = self.IDLE

    def play_media(self):
        if self.status == self.IDLE:
            # setup and play
            url = self.urlLineEdit.text()
            res = self.setup_play(url)
            if res != -1:
                # remove cache file
                os.remove(self.cache_filename)
                self.url = url
                self.client_rtp_thread = threading.Thread(target=self.recv_stream, args=(self.cache_filename,))
                self.status = self.PLAY
                self.play_event = threading.Event()
                self.client_rtp_thread.start()
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.cache_filename)))
                self.timer.timeout.connect(self.start_play)
                self.timer.start(5000)
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
        else:
            return

    def pause_media(self):
        if self.status != self.PLAY:
            return
        self.media_player.pause()
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

        # reset client parameters
        self.seq = 0
        self.client_rtp_port = None
        self.client_rtcp_port = None
        self.client_session_id = None
        self.url = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = Player()
    player.show()
    sys.exit(app.exec_())
