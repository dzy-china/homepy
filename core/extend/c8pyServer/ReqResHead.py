import sys
from urllib.parse import urlparse


class ReqResHead:
    serverName = 'c8pyServer'

    # 初始化数据
    def __init__(self):
        self.env = {}
        self.response_head = b''

    # 封装请求头信息以及其它服务端信息，并且支持wsgi格式
    def request_head_assemble(self, request_head_dict, geoip2_Obj, request_ip, serverPort, hostname):
        # 1. 请求头封装为 env
        for key, val in request_head_dict.items():
            if key == 'request_line':  # 首行解析
                url_params = urlparse(val[1])
                self.env['REQUEST_METHOD'] = val[0]  # 请求方法：get post等
                self.env['REQUEST_URI'] = val[1]  # 请求url
                self.env['SERVER_PROTOCOL'] = val[2]  # 请求协议
                self.env['PATH_INFO'] = url_params.path  # 请求路径(不带域名和"url请求参数")
                self.env['QUERY_STRING'] = url_params.query  # url请求参数，没有请求参数返回空字符串''
            else:  # 请求头解析
                key = key.upper().replace('-', '_')
                if key in ('USER_AGENT', 'ACCEPT', 'ACCEPT_ENCODING', 'CONNECTION', 'HOST', 'COOKIE'):  # 追加前缀 'HTTP_'
                    self.env[f'HTTP_{key}'] = val
                else:
                    self.env[key] = val

        # 2. 追加封装 wsgi协议 要求下的基本变量
        self.env['wsgi.input'] = None  # 请求体(io流封装类型)
        self.env['wsgi.version'] = (1, 0)
        self.env['wsgi.errors'] = sys.stderr
        self.env['wsgi.run_once'] = False
        self.env['wsgi.multithread'] = True
        self.env['wsgi.multiprocess'] = False
        self.env['wsgi.url_scheme'] = 'http'

        # 3. 追加服务端信息
        self.env['SERVER_PROTOCOL'] = 'HTTP/1.1'
        self.env['SCRIPT_NAME'] = ''  # 站点虚拟目录(请求的 URL 的路径(path)的末尾部分)
        self.env['SERVER_NAME'] = hostname
        self.env['SERVER_PORT'] = serverPort
        self.env['server'] = self.serverName

        # 4. 追加ip地理位置信息
        geo_dict = {
            'ip': request_ip,
            'address': '',
            'longitude': '',
            'latitude': ''
        }
        if geoip2_Obj:
            geo_msg = ''
            if continent := geoip2_Obj.continent.names.get('zh-CN'):  # 国家位置
                geo_msg += continent
            if country := geoip2_Obj.country.names.get('zh-CN'):  # 国家
                geo_msg += '-' + country
            if geoip2_Obj.subdivisions and (subdivisions := geoip2_Obj.subdivisions[0].names.get('zh-CN')):  # 省份
                geo_msg += '-' + subdivisions
            if geoip2_Obj.city and (city := geoip2_Obj.city.names.get('zh-CN')):  # 城市
                geo_msg += '-' + city
            geo_dict = {
                'ip': request_ip,
                'address': geo_msg,
                'longitude': geoip2_Obj.location.longitude,
                'latitude': geoip2_Obj.location.latitude
            }

        self.env = {**self.env, 'geo': geo_dict}

    # 封装响应头
    def response_head_assemble(self, user_response_status, user_response_head):
        # 1.响应行
        data_line = f"HTTP/1.1 {user_response_status}\r\n"

        # 2.响应头
        data_head = f"server: {self.serverName}\r\n"
        if 'gzip' in self.env.get('HTTP_ACCEPT_ENCODING'):
            data_head += "Content-Encoding: gzip\r\n"
        for head_val in user_response_head:
            data_head += head_val[0] + ': ' + head_val[1] + '\r\n'

        # 3. 响应头结束标志
        data_blank = "\r\n"

        self.response_head = (data_line + data_head + data_blank).encode()
