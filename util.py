import re


def parse_url(string):
    url_pattern = r'rtsp://(?P<ip>(\d{1,3}\.){3}\d{1,3})\:(?P<port>\d{1,5})/(?P<path>\w*)'
    res = re.search(url_pattern, string)
    if not res:
        return None
    res_dict = res.groupdict()
    ip = res_dict.get('ip')
    port = res_dict.get('port')
    path = res_dict.get('path')
    return ip, port, path


def match_rtp_port(response):
    res = re.search(r'm=video\s*(?P<rtp_port>\d+)\s*', response)
    if not res:
        return None
    return int(res.groupdict().get('rtp_port'))


def match_media_time(response):
    res = re.search(r'npt=(?P<cur_time>(\d*\.?\d*)|now)-(?P<end_time>\d*\.?\d*)', response)
    if not res:
        return None, None
    res_dict = res.groupdict()
    return int(float(res_dict['cur_time'])), int(float(res_dict['end_time']))


