import datetime
import time


class Time:
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

    @property
    def cur_time(self):
        """
        获取当前时间戳 属性
        """
        return int(time.time())

    @property
    def cur_format_time(self):
        """
         获取当前格式化时间 属性
        """
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
