
from typing import final

from core.common.password import md5_hmac, md5, sha1,get_uuid


class Password:
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

    # 设置 md5
    @final
    def md5(self, data: any) -> str:
        return md5(data)

    # 设置 sha1
    @final
    def sha1(self, data: any) -> str:
        return sha1(data)

    # 设置 md5_hmac
    @final
    def md5_hmac(self, data: any) -> str:
        return md5_hmac(data)

    # 获取 uuid
    @final
    def uuid(self, data=None) -> str:
        return get_uuid(data)