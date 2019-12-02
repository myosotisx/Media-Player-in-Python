TS_PACKET_SIZE = 188


class TS:

    def __init__(self):
        pass

    def get_pcr_value1(self, data):
        if not (data[3] & 0x20):
            # print('no field')
            return -1
        length = data[4]
        if length == 0:
            # print('length is 0')
            return -1
        if not (data[5] & 0x10):
            # print('no pcr')
            return -1

        pref = data[6:6 + 4]
        v_ref = int.from_bytes(pref, 'big')
        v_ref = v_ref << 1
        v_ref += data[10] / 128
        v_ext = (data[10] % 2) * 256 + data[11]
        res = (v_ref * 300 + v_ext) // 27000
        return res

    def get_pcr_value(self, payload):
        if len(payload) % 188:
            return -1
        cnt = len(payload) // 188
        for i in range(cnt):
            data = payload[i * 188:i * 188 + 188]
            if not (data[3] & 0x20):
                # print('no field')
                continue
            length = data[4]
            if length == 0:
                # print('length is 0')
                continue
            if not (data[5] & 0x10):
                # print('no pcr')
                continue

            pref = data[6:6 + 4]
            v_ref = int.from_bytes(pref, 'big')
            v_ref = v_ref << 1
            v_ref += data[10] / 128
            v_ext = (data[10] % 2) * 256 + data[11]
            res = (v_ref * 300 + v_ext) // 27000
            return res
        return -1


ts = TS()