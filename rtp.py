HEADER_SIZE = 12
TS_RTP_PACKET_SIZE = 1328
H264_PAYLOAD_TYPE = 96
ACC_PAYLOAD_TYPE = 97
TS_PAYLOAD_TYPE = 33
RTP_MAX_PKT_SIZE = 1400


class RTP_PACKET:

    def __init__(self):
        pass

    def get_payload(self, data):
        return data[HEADER_SIZE:]

    def get_payload_type(self, data):
        header = data[:HEADER_SIZE]
        return header & 0x7F

    def get_seq(self, data):
        header = data[:HEADER_SIZE]
        return header[2] << 8 | header[3]


rtp_packet = RTP_PACKET()