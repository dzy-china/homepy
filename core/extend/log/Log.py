import datetime
import logging.handlers
import os
from pathlib import Path


class Log:
    def __init__(self):
        # 1.创建日志器对象
        self.logger = logging.getLogger('homepy')
        # 2.设置logger可输出日志级别范围
        self.logger.setLevel(logging.DEBUG)

        # 3.1 添加控制台handler，用于输出日志到控制台
        console_handler = logging.StreamHandler()

        # 3.2 添加日志文件handler，用于输出日志到文件中，按文件大小分隔
        # 定义日志文件的路径
        log_file = Path('runtime') / 'log' / 'log.log'
        log_dir = log_file.parent  # 获取文件目录

        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            mode='a',
            encoding='UTF-8',
            maxBytes=1024*1024*2,
            backupCount=3
        )

        # 4. 设置控制台和文件日志格式
        dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatter = logging.Formatter(f'{dt_ms} - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # 5. 将handler添加到日志器中
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    # 打印日志
    def print(self, msg):
        self.logger.debug(msg)


log = Log()
