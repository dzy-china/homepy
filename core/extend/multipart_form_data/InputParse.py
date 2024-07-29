from .FormField import FormField
from .public import parse_options_header

"""
    Content-Type: multipart/form-data
    
    使用说明：
        from content_type.multipart_form_data.InputParse import InputParse
        # 实例化
        part = InputParse(env)
        forms, files = part.start_parse()
        
        # 获取 请求内容
        print(forms)  #{'name': 'dzy', 'age': '18'}
        files['pic'].save_as('./my.jpg')
"""


class InputParse:
    # 初始化数据
    def __init__(self, environ: dict):
        # 编码
        self.charset = 'utf8'

        # 表单数据
        self.forms = {}

        # 表单文件
        self.files = {}

        # 请求数据长度
        self.content_length = -1

        # 请求类型
        self.content_type = ''

        # multipart/form-data请求类型对应boundary值
        self.boundary_flag = ''

        # wsgi.input数据
        self.wsgi_input = None

        # 硬盘大小限制  1G
        self.disk_limit = 1 * 1024 * 1024 * 1024

        #  内存大小限制  10M
        self.mem_limit = 10 * 1024 * 1024

        # 文件数据是否采用本地硬盘临时存储(超过该大小采用临时文件，否则采用内存存储) 256KB
        self.mem_file_limit = 256 * 1024

        #  允许读取文件缓存大小 4M
        self.buffer_size = 4 * 1024 * 1024

        self.content_length = int(environ.get("CONTENT_LENGTH", "-1"))

        self.content_type, boundary_dict = parse_options_header(environ.get("CONTENT_TYPE", ""))
        self.boundary_flag = boundary_dict.get("boundary", "")

        self.wsgi_input = environ.get("wsgi.input", None)

    def start_parse(self):
        # 如果是 multipart/form-data 请求, 并且内容长度大于0
        if "multipart/form-data" == self.content_type and self.content_length > 0:
            # 遍历 生成器的数据
            for part in self._iterparse():
                if part.filename or not part.is_buffered():  # 文件
                    if part.name in self.files:  # 多文件
                        if isinstance(self.files[part.name], list):
                            self.files[part.name].append(part)
                        else:
                            self.files[part.name] = [self.files[part.name], part]
                    else:  # 单文件
                        self.files[part.name] = part
                else:  # 普通字段
                    if part.name in self.forms:  # 多字段
                        if isinstance(self.forms[part.name], list):
                            self.forms[part.name].append(part.value)
                        else:
                            self.forms[part.name] = [self.forms[part.name], part.value]
                    else:  # 单字段
                        self.forms[part.name] = part.value

        return self.forms, self.files

    # 生成器 解析读取的 wsgi.input 每行数据
    def _iterparse(self):
        # 调用生成器读取 wsgi.input 每行数据
        lines = self._lineiter()

        # 定义 form-data 类型数据分隔符和结束符
        separator = b"--" + self.boundary_flag.encode('utf8')
        terminator = b"--" + self.boundary_flag.encode('utf8') + b"--"

        # 消耗第一个边界，根据RFC的要求，忽略任何前导码
        lines.__next__()

        # 记录当前请求内存和硬盘使用大小
        mem_used = 0
        disk_used = 0

        opts = {
            "buffer_size": self.buffer_size,
            "mem_file_limit": self.mem_file_limit,
            "charset": self.charset,
        }

        # 初始化实例对象开始读取第一个字段
        part = FormField(**opts)

        # 遍历 生成器读取 wsgi.input 每行数据
        for line, nl in lines:
            if line == terminator:  # 读取完毕时
                part.file.seek(0)  # 移动文件指针到起始位置，以待读取
                yield part
                break
            elif line == separator:  # 读取分隔线时
                if part.is_buffered():
                    mem_used += part.size
                else:
                    disk_used += part.size
                part.file.seek(0)  # 移动文件指针到起始位置，以待读取
                yield part

                # 新建实例对象准备读取新字段值
                part = FormField(**opts)  # 引用赋值

            else:  # 读取字段内容时
                part.write_contents(line, nl)  # 根据 self.file 对象是否为真，写入请求体或请求头
                # 大小限制判断
                if part.is_buffered():
                    if part.size + mem_used > self.mem_limit:
                        raise Exception(f"内存大小使用超过{self.mem_limit}字节")
                elif part.size + disk_used > self.disk_limit:
                    raise Exception(f"硬盘大小使用超过{self.disk_limit}字节")
        else:
            part.close()

    # 生成器读取 wsgi.input 每行数据
    def _lineiter(self):
        max_read = self.content_length
        max_buf = self.buffer_size

        # 循环读取请求体
        while True:
            # 分片读取数据
            data = self.wsgi_input.read(max_buf if max_read < 0 else min(max_buf, max_read))
            if data:
                max_read -= len(data)  # 每次读完递减

                # 以换行符拆分,保留换行符
                lines_data = data.splitlines(True)

                # 依次返回每一行数据和尾部换行符
                for line in lines_data:
                    if line.endswith(b"\r\n"):
                        yield line[:-2], b"\r\n"
                    elif line.endswith(b"\n"):
                        yield line[:-1], b"\n"
                    elif line.endswith(b"\r"):
                        yield line[:-1], b"\r"
                    else:
                        yield line, b""
            else:
                break
