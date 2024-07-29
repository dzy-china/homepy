import os
from pathlib import Path


# 获取文件信息
def get_file_info(file_path: str):
    class File:
        def __init__(self):
            self.p = Path(file_path)

        # 文件名  tum6.png
        @property
        def basename(self):
            return self.p.name

        # 文件拓展名  png
        @property
        def ext(self):
            return self.p.suffix.removeprefix('.')

    return File()
