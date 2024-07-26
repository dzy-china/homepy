from typing import List, final
from core.ComtrollerBase import ComtrollerBase

"""
#1. 获取 cookie： self.cookie('name')
#2. 设置 cookie: self.cookie('name', 'dzy', {'path': '/', 'max-age': 600})
参数：
    只有一个参数，是获取值
    2个以及两个以上是设置cookie，第一个参数是键，第二个参数是值(字符串/整数/小数)，第三个参数是cookie相关特性，用字典表示
     cookie相关特性：
         path: cookie 匹配路径, 默认'/', 表示站点根目录下任何路径下生效
         max-age：存活的秒数,如果忽略该参数，Cookie 会在会话结束时过期（也就是关掉浏览器时）
         domain : 指定了 Cookie 所属的域名，若没有指定Domain属性，那么其默认值就是当前域名（不包含子域名）
         secure: 唯一值 secure, 默认为空， 表示仅能用与 HTTPS 协议
         httponly：唯一值 httponly, 默认为空，表现形式为 cookie 不能被客户端脚本javascript获取到
         SameSite:  禁止第三方Cookie，默认None，SameSite=Strict 可以严格限定 Cookie 不能随着跳转链接跨站发送。SameSite=Lax 则略宽松一点，允许GET/HEAD 等安全方法，但禁止 POST 跨站发送。SameSite=None：允许使用第三方Cookie
"""


class Cookie(ComtrollerBase):
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

        # 当前待响应cookie [{'name':'dzy', 'path':'/', 'max-age':3600}]
        self.__response_cookies: List[dict] = []

        # 当前请求cookie {'name':'dzy','age':18}
        self.__request_cookies: dict = {}

    # ***1.获取cookie： cookie('name')
    # ***2.设置cookie: cookie('name', 'dzy', {'path': '/', 'max-age': 60*30})
    @final
    def cookie(self, *args):
        if len(args) == 1:  # 获取cookie(优先获取服务端新设置的cookie)
            for val in self.__response_cookies:
                if args[0] in val:
                    return val[args[0]]
            if args[0] in self.__request_cookies.keys():
                return self.__request_cookies[args[0]]
            else:
                return ''
        elif len(args) == 2:  # 设置cookie
            # 处理重复设置cookie
            for index, val in enumerate(self.__response_cookies):
                if args[0] in val:
                    self.__response_cookies[index] = {args[0]: args[1], 'path': '/'}
                return
            # 正常设置cookie
            self.__response_cookies.append({args[0]: args[1], 'path': '/'})
        elif len(args) == 3 and type(args[2]) == dict:  # 设置cookie
            # 处理重复设置cookie
            for index, val in enumerate(self.__response_cookies):
                if args[0] in val:
                    self.__response_cookies[index] = {**{args[0]: args[1], 'path': '/'}, **args[2]}
                return
            # 正常设置cookie
            self.__response_cookies.append({**{args[0]: args[1], 'path': '/'}, **args[2]})

    # 获取当前请求cookie
    # 'request_token=bAfhQoWXho16clJjqhdMhJzJmiSuHmhHojKkn8OcYyC3vGSa; order=id%20desc; site_model=php; page_number=20'
    def _gather_request_cookies(self, http_cookie):
        http_cookies_list = http_cookie.split('; ')
        for val in http_cookies_list:
            http_cookie_list = val.split('=')
            self.__request_cookies[http_cookie_list[0]] = http_cookie_list[1]

    # 组装响应cookie
    def _assemble_response_cookies(self) -> List[tuple]:
        temp_list = []
        for val in self.__response_cookies:
            temp_str = ''
            for key2, val2 in val.items():
                temp_str += f'{key2}={val2}; '
            temp_list.append(('Set-Cookie', temp_str))  # ('Set-Cookie', 'my_name=dzy; path=/; max-age=6000;')
        return temp_list
