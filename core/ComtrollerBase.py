from config.CORS import CORS


class ComtrollerBase:

    def __init__(self):
        # wsgi  env
        self.__env = None
        # 响应头
        self.__header_response = [
            ('Content-Type', 'application/json;charset:utf-8;'),
            ('Access-Control-Allow-Origin', CORS.origin),
            ('Access-Control-Allow-Headers', CORS.headers),
            ('Access-Control-Allow-Methods', CORS.methods),
        ]

    # 获取 env 属性
    @property
    def env(self):
        return self.__env

    # 设置 env 属性
    @env.setter
    def env(self, val):
        self.__env = val

    # 获取 header_response 属性
    @property
    def header_response(self):
        return self.__header_response

