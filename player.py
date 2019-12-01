import sys
import socket
import threading
import time

from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import QUrl, Qt, pyqtSignal

from mainwindow import Ui_MainWindow

import util
import rtp
from rtp import rtp_packet
from rtsp import rtsp


class Player(QMainWindow, Ui_MainWindow):
    play_signal = pyqtSignal(object)

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

        # init sockets
        self.client_rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_rtsp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.client_rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_rtp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.client_rtcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_rtcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # init client parameters
        self.seq = 0
        self.client_rtp_port = None
        self.client_rtcp_port = None
        self.client_session_id = None
        self.client_rtp_thread = None

    def close_rtsp_connection(self):
        self.client_rtsp_socket.shutdown(2)
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
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.seq += 1
        # send DESCRIBE
        request_dict = {'CSeq': str(self.seq), 'Accept': 'application/sdp'}
        request = rtsp.generate_request('DESCRIBE', url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.client_rtp_port = util.match_rtp_port(response)
        if not self.client_rtp_port:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: can not specify RTP port.')
            return -1
        self.client_rtcp_port = self.client_rtp_port+1
        self.seq += 1
        # setup RTP and RTCP socket
        self.client_rtp_socket.bind(('127.0.0.1', self.client_rtp_port))
        self.client_rtcp_socket.bind(('127.0.0.1', self.client_rtcp_port))
        # send SETUP
        request_dict = {'CSeq': str(self.seq), 'Transport': 'RTP/AVP;unicast;client_port=%d-%d' % (self.client_rtp_port,
                                                                                                   self.client_rtcp_port)}
        request = rtsp.generate_request('SETUP', url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        self.client_session_id = int(response_dict.get('Session'))
        self.seq += 1
        # send PLAY
        request_dict = {'CSeq': str(self.seq), 'Session': self.client_session_id, 'Range': 'npt=0.000-'}
        request = rtsp.generate_request('PLAY', url, request_dict)
        self.client_rtsp_socket.send(request.encode())
        response = self.client_rtsp_socket.recv(1024).decode()
        if rtsp.get_status_code(response) != 200:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response code.')
            return -1
        response_dict = rtsp.get_response_dict(response)
        if int(response_dict.get('CSeq')) != self.seq:
            self.close_rtsp_connection()
            QMessageBox.warning(self, 'Warning', 'Error: unexpected server response SN.')
            return -1
        return 0

    def recv_stream(self, cache_filename):
        cur_seq = 0
        file = open(cache_filename, 'wb')
        bytes_cnt = 0
        while True:
            data = self.client_rtp_socket.recv(rtp.TS_RTP_PACKET_SIZE)
            seq = rtp_packet.get_seq(data)
            if cur_seq and cur_seq >= seq:
                continue
            cur_seq = seq
            payload = rtp_packet.get_payload(data)
            bytes_cnt += file.write(payload)
            print(bytes_cnt)

    def play_media(self):
        res = self.setup_play(self.urlLineEdit.text())
        if res != -1:
            cache_file = r'C:\Users\Myosotis\PycharmProjects\Player\tmp.ts'
            self.client_rtp_thread = threading.Thread(target=self.recv_stream, args=(cache_file,))
            self.client_rtp_thread.start()
            time.sleep(1)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(cache_file)))
            self.media_player.play()




    def pause_media(self):
        pass

    def stop_media(self):
        pass

app = QApplication(sys.argv)
demo = Player()
demo.show()
sys.exit(app.exec_())
