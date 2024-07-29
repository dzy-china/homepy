import datetime
import gzip
import re
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
import socket
import tempfile
from io import BytesIO, BufferedReader
import geoip2.database
from pathlib import Path
from .ReqResHead import ReqResHead

class HttpServer:
    # 实例
    _instance = None

    # 读取请求体时缓冲区大小
    socket_makefile_buf = 512
    # http请求方式
    request_method_list = ['POST', 'GET', 'HEAD', 'PUT', 'PATCH', 'OPTIONS', 'DELETE', 'CONNECT', 'TRACE']
    # GeoLite2数据库文件路径：D:\project\python\homepy\core\extend\c8pyServer\GeoLite2-City.mmdb
    GeoLite2_path = Path(__file__).parent / 'GeoLite2-City.mmdb'  # /为路径拼接符

    # 单例模式
    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    # 构造函数
    def __init__(self):
        self.host = ""  # 主机地址(空字符串代表不限制具体ip，满足访问主机ip即可)
        self.port = None  # 端口号
        self.hostname = socket.gethostname()  # 主机名： DESKTOP-7JIB6KH
        self.server_socket = None  # 服务端socket
        self.callback = None  # 处理请求响应回调函数名称

    def run(self, host="", port=5111, callback=None):
        self.host = host
        self.port = port
        self.callback = callback
        self.__create_server_socket()
        self._start_socket()

    # 创建 server_socket
    def __create_server_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # 最多5个排队socket

    # 启动多线程处理请求
    def _start_socket(self):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{cur_time} 服务器启动！')

        if self.host == '':
            print(f'请求地址：http://127.0.0.1:{self.port}')
        else:
            print(f'请求地址：http://{self.host}:{self.port}')
        print()

        # 创建线程池对象，指定线程池中线程数
        pool = ThreadPoolExecutor(max_workers=cpu_count())

        # 获取国家级ip数据库数据
        reader_geoip2 = geoip2.database.Reader(self.GeoLite2_path)

        # 接收客户端连接
        while True:
            # 等待新客户端连接
            client_socket, client_addr = self.server_socket.accept()

            cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'新访客：', client_addr, cur_time)

            # 排除局域网 ip检测
            geoip2_Obj = None
            if client_addr[0] != '127.0.0.1' and not client_addr[0].startswith('192.168'):
                # 获取ip地理位置对象
                geoip2_Obj = reader_geoip2.city(client_addr[0])

                # ***境外ip拦截***
                country_iso_code = geoip2_Obj.country.iso_code
                if 'CN' != country_iso_code:
                    print(f'新访客被拦截：', client_addr, cur_time)
                    client_socket.close()
                    continue

            # 调用线程池中线程去执行函数
            future = pool.submit(self.handle_client_socket, client_socket, geoip2_Obj, client_addr[0])

            # 线程执行结果回调(包括异常栈信息)
            future.add_done_callback(self.__thread_done_callback)

    # ***任务线程执行结果回调函数***
    def __thread_done_callback(self, future):
        if result := future.result():
            print(result)

    # 处理客户端连接
    def handle_client_socket(self, client_socket, geoip2_Obj, request_ip):
        # 定义流对象
        fp = client_socket.makefile('rb')  # 与socket绑定的文件流
        temporary_file = None  # 临时文件流

        # 1. 读取请求头
        # 1.1 先读取首行
        # 针对url请求到请求头发送延迟1分钟情况
        # 注：如页面favicon图标的请求，如果第一次请求响应404，第二次再次请求就会出现请求到请求头发送延迟1分钟情况
        line_head = fp.readline()
        print(f'请求头：{line_head}' + '\n', end='')
        print()

        # 关闭请求
        if not line_head:  # 遇到空字符串请求头，直接关闭连接
            self.__close(client_socket, fp)
            return
        else:  # 非空字符串请求头，合法性判断
            # 判断是否是标准格式的请求头，如果不是，关闭当前连接
            # GET /demo?name=dzy HTTP/1.1
            # 匹配不到返回None
            first_line_match_obj = re.search(r'^([a-z]+)\s.+\sHTTP/\d\.\d$', line_head.strip().decode(errors="ignore"),
                                             re.I)
            if not first_line_match_obj or not first_line_match_obj.group(1) in self.request_method_list:
                self.__close(client_socket, fp)
                return

        # 1.2 继续读取请求头
        request_head_list = [line_head]
        while True:
            line_head = fp.readline()
            request_head_list.append(line_head)
            if line_head == b'\r\n':  # 第一个换行符代表请求头结束
                break

        # 2. 解析请求头
        request_head_dict = self.__head_parse(request_head_list)

        # 3. 响应类对象
        reqResHead = ReqResHead()  # 实例化响应体
        # 封装 wsgi environ
        reqResHead.request_head_assemble(request_head_dict, geoip2_Obj, request_ip, self.port, self.hostname)

        # 4. 继续读取请求体，重置 reqResHead.env['wsgi.input']
        if (content_length := int(request_head_dict.get('content-length', '0'))) > 0:
            # 'multipart/form-data'请求类型
            if 'multipart/form-data' in request_head_dict.get('content-type'):
                # 读取请求体
                temporary_file = tempfile.TemporaryFile('w+b')
                all_read_len = 0
                while True:
                    read_max_len = min(content_length - all_read_len, self.socket_makefile_buf)
                    read_data = fp.read(read_max_len)
                    temporary_file.write(read_data)
                    all_read_len += len(read_data)
                    if all_read_len >= content_length:
                        break

                # 初始化文件指针
                temporary_file.seek(0)

                # 赋值给 wsgi.input
                reqResHead.env['wsgi.input'] = BufferedReader(temporary_file)
            else:  # 其它请求类型
                request_body = fp.read(content_length)
                reqResHead.env['wsgi.input'] = BytesIO(request_body)

        # 5.调用处理响应的回调函数
        response_body = self.callback(reqResHead.env, reqResHead.response_head_assemble)

        # 6.发送响应内容(响应头和响应体)
        if 'gzip' in reqResHead.env.get('HTTP_ACCEPT_ENCODING'):
            response_body[0] = gzip.compress(response_body[0])
        client_socket.sendall(reqResHead.response_head + response_body[0])

        # 7. 关流
        self.__close(client_socket, fp, temporary_file)

    # 关流
    def __close(self, client_socket, fp, temporary_file=None):
        client_socket.close()
        del client_socket
        fp.close()
        del fp
        if temporary_file:
            temporary_file.close()
            del temporary_file

    # 解析请求头
    def __head_parse(self, request_head_list):
        request_head_dict = {}
        for val in request_head_list:
            val_str = val.decode().strip()
            if val_str:
                split_val = val_str.split(":", 1)
                if len(split_val) == 1:  # 请求行
                    request_head_dict['request_line'] = val_str.split(" ")
                else:  # 请求体
                    request_head_dict[split_val[0].lower()] = split_val[1].strip()
        return request_head_dict


# 单例
httpServer = HttpServer()
