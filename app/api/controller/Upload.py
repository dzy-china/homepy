import os

from app.common.controller.Base import Base
from config.UploadConfig import UploadConfig


class Upload(Base):
    # 处理文件上传
    def index(self):
        """
         print(self.input())
            {
                'upload_dir': 'member',
                'file_field': 'certification',
                'certification': <core.extend.multipart__form_data.FormField.FormField object at 0x000001F6D67BC210>
            }
        """
        return self.upload(field=self.input('file_field'), upload_child_dir=self.input('upload_dir'))

    def upload_del(self):
        """
        上传文件删除
        """
        remove_file = self.input('remove_file')  # "/upload/staffs/2022/07/29/1659096967336745.jpeg"
        os.unlink(UploadConfig.upload_path_prefix + remove_file.replace("/", os.path.sep))
        return True
