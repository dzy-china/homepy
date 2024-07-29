import mimetypes
import os
import time
import urllib.request
import urllib.parse
import uuid
from typing import final
from config.UploadConfig import UploadConfig
from core.ComtrollerBase import ComtrollerBase
from core.common.password import md5
from core.common.file import get_file_info
from core.extend.multipart_form_data.InputParse import InputParse
import json


class Request(ComtrollerBase):
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

        # 所有请求参数(会在每次请求第一次获取时赋值)
        self.__request_params = None

    # 模拟客户端发送请求
    # 支持文件上传(文件上传需传入二进制表示的文件路径)
    """
        示例参考：
            # 请求url
            url = 'http://127.0.0.1:5111/index'
            # 请求头
            header = {
                'phone': '13688888888',
                'key': '4afadf937d033a286d2127e64f44db63',
            }
            # url参数
            params = {
                'type': 'newsmedia'
            }
            # 请求体
            # 注：文件上传需传入二进制表示的路径
            data = {
                'name': 'zhangsan',
                'age': 18,
                'pic': b'E:\\project\\python\\test\\tum6.png',  
            }
            result = self.client(url=url, params=params, data=data, header=header, timeout=None)
            # 输出响应信息
            print(result.text) # 返回响应内容
            print(result.response_header) # 以列表元祖对的形式返回响应头信息
            print(result.version) # 返回版本信息
            print(result.status) # 返回状态码200 成功，404 代表网页未找到
            print(result.closed) # 返回对象是否关闭布尔值 False
            print(result.url) # 返回检索的URL http://127.0.0.1:5111/index?type=newsmedia
            print(result.code) # 返回响应的HTTP状态码 200
            print(result.msg) # 访问成功则返回 ok
    """

    @final
    def client(self, url: str, params: dict = {}, data: dict = {}, header: dict = {}, method='GET', timeout=None):
        # 1.请求头
        default_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'homepyClient author 1129881228@qq.com'
            # 'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        header = {**default_headers, **header}

        # 2.请求url参数
        params_str = ''
        if params:
            params_str = urllib.parse.urlencode(params)  # 字典 转 url参数字符串

        # 3.对请求类型处理
        content_type = header.get('Content-Type') or header.get('content-type')

        separation_flag = ''
        if 'multipart/form-data' in content_type:
            separation_flag = md5(str(uuid.uuid1()))
            separation_flag = separation_flag.rjust(50, '-')
            header['Content-Type'] = f'multipart/form-data; boundary={separation_flag}'

        # 4.请求体信息
        bypes_data = None
        if data:
            if 'application/x-www-form-urlencoded' in content_type:
                bypes_data = urllib.parse.urlencode(data).encode('utf8')  # 字典 转 url参数字符串
            elif 'application/json' in content_type:
                bypes_data = json.dumps(data).encode('utf8')  # python字典数据转字符串格式
            elif 'multipart/form-data' in content_type:  # python字典数据转 'multipart/form-data' 格式
                bypes_data = b''
                for key, val in data.items():
                    # (1). 每行字段分隔符
                    bypes_data += ('--' + separation_flag + '\r\n').encode('utf8')

                    # (2). 每行字段摘要
                    if isinstance(val, bytes):
                        # 获取文件信息
                        file_info = get_file_info(val.decode('utf-8'))
                        basename = file_info.basename

                        # 拼接文件字段摘要
                        temp_file_str = f'Content-Disposition: form-data; name="{key}"; filename="{basename}"\r\n'
                        mimetype, _ = mimetypes.guess_type(val.decode('utf-8'))  # 获取文件类型mimetype
                        temp_file_str += f'Content-Type: {mimetype}' + '\r\n'
                        bypes_data += temp_file_str.encode('utf8')
                    else:
                        bypes_data += (f'Content-Disposition: form-data; name="{key}"' + '\r\n').encode('utf8')

                    #  (3). 每行字段摘要和请求体之间空行
                    bypes_data += b'\r\n'

                    # (4).  每行字段请求体
                    if isinstance(val, bytes):  # 读取二进制数据
                        with open(val.decode('utf-8'), 'rb') as fo:
                            while file_data := fo.read(512):
                                bypes_data += file_data + b'\r\n'
                    else:
                        bypes_data += (json.dumps(val) + '\r\n').encode('utf8')  # 每行字段请求体
                # 结束标志字符串
                bypes_data += ('--' + separation_flag + '--\r\n').encode('utf8')

        # 5.调用 urllib.request 请求url
        # url：url 地址。
        # data：发送到服务器的其他数据对象，默认为 None。
        # headers：HTTP 请求的头部信息，字典格式。
        # method：请求方法， 如 GET、POST、DELETE、PUT等。
        request_url = url + '&' + params_str if '?' in url else url + '?' + params_str
        request_obj = urllib.request.Request(url=request_url, data=bypes_data, headers=header, method=method)
        response_obj = urllib.request.urlopen(request_obj, timeout=timeout)

        # 6. 封装响应信息
        class Response:
            # 返回响应内容
            text = response_obj.read().decode('utf-8')
            # 以列表元祖对的形式返回响应头信息
            # [('server', 'homeServer'), ('Content-Type', 'application/json;charset:utf-8;')
            response_header = response_obj.getheaders()
            version = response_obj.version  # 返回版本信息
            status = response_obj.status  # 返回状态码200 成功，404 代表网页未找到
            closed = response_obj.closed  # 返回对象是否关闭布尔值 False
            url = response_obj.geturl()  # 返回检索的URL http://127.0.0.1:5111/index?type=newsmedia
            code = response_obj.getcode()  # 返回响应的HTTP状态码 200
            msg = response_obj.msg  # 访问成功则返回 ok

        return Response()

    @final
    def input(self, field='', field_default_return=None):
        """
                获取请求参数
                返回值：
                    1. self.input() 值存在返回字典，不存在返回空字典{}
                    1. self.input(field) 值存在返回值，不存在返回None
                    1. self.input(field, field_default_return) 值存在返回值，不存在返回 field_default_return
            """
        if self.__request_params is not None:  # 第二次获取某个请求字段时，执行
            return self.__request_params.get(field, field_default_return) if field else self.__request_params

        # 获取url中?后的get参数,没有返回空字典{}
        #  self.env.get('QUERY_STRING') # 获取url请求参数，没有请求参数返回空字符串''
        query_string = self.__query_string_to_dict(self.env.get('QUERY_STRING'))

        # 获取post或get请求体数据
        post_request_data = {}

        if self.env.get('CONTENT_TYPE'):  # 请求体编码类型判断
            if 'application/x-www-form-urlencoded' in self.env.get('CONTENT_TYPE'):
                if request_body_size := int(self.env['CONTENT_LENGTH']):
                    request_body = self.env['wsgi.input'].read(request_body_size)
                    post_request_data = self.__query_string_to_dict(request_body.decode("utf-8"))

            elif 'multipart/form-data' in self.env.get('CONTENT_TYPE'):
                forms, files = InputParse(self.env).start_parse()
                post_request_data = {**forms, **files}

            elif 'application/json' in self.env.get('CONTENT_TYPE'):
                if request_body_size := int(self.env['CONTENT_LENGTH']):
                    request_body = self.env['wsgi.input'].read(request_body_size)
                    post_request_data = json.loads(request_body.decode("utf-8"))  # json字符串转python字典

            data_dict = {**query_string, **post_request_data}
            self.__request_params = data_dict  # 记录当前请求中所有请求参数

            return data_dict.get(field, field_default_return) if field else data_dict
        else:
            self.__request_params = query_string  # 记录当前请求中所有请求参数
            return query_string.get(field, field_default_return) if field else query_string

    # 参数字符串转字典
    # 返回值：参数为空字符串时返回空字典{}
    def __query_string_to_dict(self, query_string):
        if not query_string:  # 查询字符串如果为空直接返回空字典{}
            return {}
            # 将参数字符串转换为字典
        query_string = urllib.parse.unquote(query_string)  # 对字符串url接码：id=[15,16]&msg=985&address=16号
        query_string_list1 = query_string.split('&')  # 对字符串以'&'符号拆分为列表

        # 遍历每个元素，并根据'='符号进一步拆分为列表
        return_result = {}
        for query_string_list1_val in query_string_list1:
            query_string_list2 = query_string_list1_val.split('=')  # 对字符串拆分为列表
            # 将字符串值转化为python数据类型
            try:  # 正常运行代码
                query_string_list2[1] = json.loads(query_string_list2[1])  # 注：整数字符串会被转化为整数，字符串转换时会报错，需要捕获错误
            except:  # 这里对字符串转换时报错，不作处理
                ...
            finally:  # 总是执行
                return_result[query_string_list2[0]] = query_string_list2[1]
        return return_result

    @final
    def upload(self, field, upload_child_dir='') -> tuple:
        """
        文件上传
        :param field: 文件上传字段名
        :param upload_child_dir: 上传到upload内的子目录名
        :return: 单文件上传返回值 /upload/upload_child_dir/。。。。或 多文件上传返回值 [/upload/upload_child_dir/。。。]
        """
        # 如果是多文件上传，file_obj会是列表形式
        file_obj = self.input(field)  # 获取上传文件资源对象

        is_multipart = True  # 多文件上传标志
        if not isinstance(file_obj, list):  # 是否是多文件上传
            is_multipart = False
            file_obj = [file_obj]

        # 获取系统目录分隔符
        cur_sep = os.path.sep

        # 获取文件上传路径前缀配置
        if upload_path_prefix := UploadConfig.upload_path_prefix:
            upload_path_prefix = upload_path_prefix.removesuffix(cur_sep) + cur_sep

        # 检测文件是否上传
        file_request_url = []
        for file_item in file_obj:
            if file_item.filename:
                # 设置文件目录路径
                upload_path = 'upload'
                upload_path += cur_sep
                upload_path += upload_child_dir
                upload_path += cur_sep
                upload_path += time.strftime(f"%Y{cur_sep}%m{cur_sep}%d")

                # 文件目录路径不存在递归创建
                if not os.path.exists(upload_path_prefix + upload_path):
                    os.makedirs(upload_path_prefix + upload_path, mode=0o777)

                # 上传路径拼接
                file_suffix = os.path.splitext(file_item.filename)[-1]  # 获取文件后缀
                file_basename = os.path.basename(file_item.filename)  # 获取原始文件名
                new_file_name = md5(file_basename) + file_suffix  # 生成新文件名
                upload_full_path = upload_path + cur_sep + new_file_name

                # 移动文件到指定位置
                file_item.save_as(upload_path_prefix + upload_full_path)

                # 文件上传可访问网址组装
                file_web_url = '/' + upload_full_path.replace(cur_sep, '/')
                if is_multipart:
                    file_request_url.append(file_web_url)
                else:
                    file_request_url = file_web_url

        # 返回文件上传可访问网址
        return file_request_url, UploadConfig.domain
