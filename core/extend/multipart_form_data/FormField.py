# 同一个实例对象逐行读取完字段内容
from io import BytesIO
from tempfile import TemporaryFile

from .public import parse_options_header, copy_file


# 一个实例对象读取一个字段
class FormField:
    def __init__(self, buffer_size=2 ** 16, mem_file_limit=2 ** 18, charset="utf8"):
        self.file = None  # 文件对象
        self.size = 0  # 每个字段对应值的字节大小
        self.name = None  # 每个字段对应键名
        self.filename = None  # 上传文件对应键名
        self.content_type = None  # 请求头字段类型
        self.charset = charset  # 字符集

        # 对象方法依赖属性
        self._line_end_buf = b""
        self._mem_file_limit = mem_file_limit
        self._buffer_size = buffer_size

    # 根据 self.file 对象是否为真，写入请求体或请求头
    def write_contents(self, line, nl):
        if self.file:  # 读取每个字段值
            self.write_body(line, nl)
        else:   # 读取每个字段头信息
            self.write_header(line, nl)

    # 读取字段键信息
    def write_header(self, line, nl):
        line = line.decode(self.charset)  # 解码读取字段键信息
        if not line.strip():  # 读取到空白行时，代表一个字段键信息读取完毕
            # 设置文件指向，为读取字段请求体做准备
            self.file = BytesIO()
        else:  # 记录读取的字段请求头信息
            _, value = line.split(":", 1)
            self.content_type, options = parse_options_header(value)
            if options:
                self.name = options.get("name")
                self.filename = options.get("filename")

    # 读取字段值
    def write_body(self, line, nl):
        self.size += len(self._line_end_buf) + len(line)
        self.file.write(self._line_end_buf + line)  # 数据写入到内存或临时文件
        self._line_end_buf = nl

        # ***大文件上传处理(如果文件过大，改变文件流指向)***
        if self.size > self._mem_file_limit and isinstance(self.file, BytesIO):
            self.file, old = TemporaryFile(mode="w+b"), self.file
            old.seek(0)  # 文件指针初始化
            copy_file(old, self.file, self.size, self._buffer_size)

    # 对象类型判断
    def is_buffered(self):
        return isinstance(self.file, BytesIO)

    # 获取普通字段值
    @property
    def value(self):
        pos = self.file.tell()  # 记录文件指针位置
        self.file.seek(0)  # 初始化文件指针位置(为了可多次读取)
        try:
            val = self.file.read()
        except IOError:
            raise
        finally:
            self.file.seek(pos)  # 设置文件指针位置
        return val.decode(self.charset)

    # 移动文件
    def save_as(self, path):
        with open(path, "wb") as fp:
            pos = self.file.tell()  # 记录文件指针位置
            self.file.seek(0)  # 初始化文件指针位置(为了可多次读取)
            try:
                size = copy_file(self.file, fp)
            except IOError:
                raise
            finally:
                self.file.seek(pos)  # 设置文件指针位置
        return size

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
