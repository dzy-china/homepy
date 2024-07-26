import os


# 获取文件信息
def get_file_info(file_path: str):
    class File:
        # 文件名  tum6.png
        @property
        def basename(self):
            return os.path.basename(file_path)

        # 文件拓展名  png
        @property
        def ext(self):
            _, ext = os.path.splitext(file_path)
            return ext.removeprefix('.')

    return File()
