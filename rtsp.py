
class RTSP:

    def __init__(self):
        pass

    def generate_request(self, cmd, url, request_dict):
        request = cmd+' '+url+' '+'RTSP/1.0\r\n'
        for key, value in request_dict.items():
            line = str(key)+': '+str(value)+'\r\n'
            request += line
        request += '\r\n'
        return request

    def get_status_code(self, response):
        return int(response.split('\n')[0].split(' ')[1])

    def get_response_dict(self, response):
        response_dict = {}
        lines = response.split('\n')[1:]
        for line in lines:
            words = line.split(':')
            if len(words) != 2:
                continue
            words[0] = words[0].strip()
            words[1] = words[1].strip()
            response_dict[words[0]] = words[1]
        return response_dict


rtsp = RTSP()