import json
import os
import re
import traceback
from typing import List
from importlib import import_module

from core.common.JsonEncode import JsonEncode
from core.extend.c8pyServer.HttpServer import httpServer
from core.extend.log.Log import log
from core.route.DefaultRoute import defaultRoute
from config.CORS import CORS

# 应用入口
class Application:
    """
    # 所有装饰器路由列表，
    [
        {
            'route': '/', 
            'route_method': ['get', 'post'], 
            'route_path_func': <function now at 0x0000000002BF2430>, 
            'route_path_func_name': 'now', 
            'route_path_func_args': ('self','name', 'age'), 
            'route_path_func_module_path': 'app.home.controller.Index', 
            'route_path_func_type_limit': {'name': <class 'str'>, 'age': <class 'int'>, 'return': <class 'str'>}
        }
    ]
    """

    # 构造函数
    def __init__(self):
        # 存放带装饰器的路由
        self.routes: List[dict] = []
        # 路由中间件
        self.middleware = None

    # 中间件处理响应
    def call_next(self, request, response):
        return self.__get_response_data(request, response)

    # 获取响应信息
    def __get_response_data(self, request, response):
        # 首先处理带装饰器的路由
        for route_info in self.routes:
            # 判断当前请求url是否满足装饰器路由
            # 带参装饰器路由 /my-dzy-18      /my-{name}-{age}
            # request['PATH_INFO'] = /my-dzy-18
            # route_info['route'] = /my-{name}-{age}
            reg_str = '^' + re.sub(r'{\w+}', '(\\\w+)', route_info['route']) + '$'
            if matchObj := re.search(reg_str, request['PATH_INFO']):
                # 带参装饰器路由处理
                route_path_func_decorator_params_val = []
                if len(matchObj.groups()) > 0:  # 如果是带参装饰器路由url
                    for params in matchObj.groups():
                        route_path_func_decorator_params_val.append(params)

                # 获取控制器类文件的模块路径
                route_path_func_module_path = route_info['route_path_func_module_path']
                # 控制器实例化
                route_class_obj = getattr(import_module(route_path_func_module_path),
                                          route_path_func_module_path.rpartition(".")[2])()

                # 收集请求cookie
                if request.get('HTTP_COOKIE'):
                    route_class_obj._gather_request_cookies(request['HTTP_COOKIE'])

                # 动态属性赋值(将当前请求环境变量赋值给当前控制器实例化对象)
                route_class_obj.env = request

                # 执行路径函数，并传递所需参数
                route_path_func_return = route_info['route_path_func'](route_class_obj,
                                                                       *route_path_func_decorator_params_val[
                                                                        0:len(route_info['route_path_func_args']) - 1])
                # 响应状态和响应头
                response('200 OK', [*route_class_obj.header_response, *route_class_obj._assemble_response_cookies()])
                if route_path_func_return is not None:  # 如果存在返回值
                    if isinstance(route_path_func_return, set):  # 如果是集合先转为列表list再转为js类型数据
                        route_path_func_return = json.dumps(list(route_path_func_return), cls=JsonEncode)
                    elif isinstance(route_path_func_return, (dict, list, tuple, int, float, bool)):
                        route_path_func_return = json.dumps(route_path_func_return, cls=JsonEncode)
                    elif isinstance(route_path_func_return, object):
                        route_path_func_return = str(route_path_func_return)
                    return route_path_func_return
                else:  # 如果不存在返回值或返回值为None，返回空字符串''
                    return ''
                # return  # 直接返回不在执行后续else
        else:  # 如果没有匹配到带装饰器的路由,执行默认路由
            defaultRoute_return = defaultRoute.is_exists_default_request(request['PATH_INFO'])

            if isinstance(defaultRoute_return, tuple) and defaultRoute_return[1]:  # 处理没有装饰器的路由
                # <app.home.controller.Index.Index object at 0x0000000002E620A0>
                controller_obj = defaultRoute_return[0]()

                # 收集请求cookie
                if request.get('HTTP_COOKIE'):
                    controller_obj._gather_request_cookies(request['HTTP_COOKIE'])

                # 动态属性赋值(将当前请求环境变量赋值给当前控制器实例化对象)
                controller_obj.env = request

                # 调用控制器方法
                route_path_func_return = defaultRoute_return[1](controller_obj)
                # 处理响应数据
                response('200 OK', [*controller_obj.header_response, *controller_obj._assemble_response_cookies()])
                if route_path_func_return is not None:  # 如果存在返回值
                    if isinstance(route_path_func_return, set):  # 如果是集合先转为列表list再转为js类型数据
                        route_path_func_return = json.dumps(list(route_path_func_return), cls=JsonEncode)
                    elif isinstance(route_path_func_return, (dict, list, tuple, int, float, bool)):
                        route_path_func_return = json.dumps(route_path_func_return, cls=JsonEncode)
                    elif isinstance(route_path_func_return, object):
                        route_path_func_return = str(route_path_func_return)
                    return route_path_func_return
                else:  # 如果不存在返回值或返回值为None，返回空字符串''
                    return ''
            else:  # 404处理
                response('404 No Found', [('Content-Type', 'text/html')])
                return '找不到资源'

    # wsgi 入口函数： application
    """request：
        CONTENT_TYPE	这个环境变量的值指示所传递来的信息的MIME类型。目前，环境变量CONTENT_TYPE一般都是：application/x-www-form-urlencoded,他表示数据来自于HTML表单。
        CONTENT_LENGTH	如果服务器与CGI程序信息的传递方式是POST，这个环境变量即使从标准输入STDIN中可以读到的有效数据的字节数。这个环境变量在读取所输入的数据时必须使用。
        HTTP_COOKIE	客户机内的 COOKIE 内容。
        HTTP_USER_AGENT	提供包含了版本数或其他专有数据的客户浏览器信息。
        PATH_INFO	这个环境变量的值表示紧接在CGI程序名之后的其他路径信息。它常常作为CGI程序的参数出现。
        QUERY_STRING	如果服务器与CGI程序信息的传递方式是GET，这个环境变量的值即使所传递的信息。这个信息经跟在CGI程序名的后面，两者中间用一个问号'?'分隔。
        REMOTE_ADDR	这个环境变量的值是发送请求的客户机的IP地址，例如上面的192.168.1.67。这个值总是存在的。而且它是Web客户机需要提供给Web服务器的唯一标识，可以在CGI程序中用它来区分不同的Web客户机。
        REMOTE_HOST	这个环境变量的值包含发送CGI请求的客户机的主机名。如果不支持你想查询，则无需定义此环境变量。
        REQUEST_METHOD	提供脚本被调用的方法。对于使用 HTTP/1.0 协议的脚本，仅 GET 和 POST 有意义。
        SCRIPT_FILENAME	CGI脚本的完整路径
        SCRIPT_NAME	CGI脚本的的名称
        SERVER_NAME	这是你的 WEB 服务器的主机名、别名或IP地址。
        SERVER_SOFTWARE	这个环境变量的值包含了调用CGI程序的HTTP服务器的名称和版本号。例如，上面的值为Apache/2.2.14(Unix)
    """
    def __call__(self, env, response):
        # options请求（跨域预检）
        if env.get('REQUEST_METHOD') == 'OPTIONS':
            # 响应头(状态码，状态信息，响应头)
            response('200 OK', [
                ('Access-Control-Allow-Origin', CORS.origin),
                ('Access-Control-Allow-Headers', CORS.headers),
                ('Access-Control-Allow-Methods', CORS.methods)])
            # 响应体
            return [''.encode('utf-8')]

        # 捕获应用程序执行错误
        try:
            if self.middleware:  # 中间件
                return_response = self.middleware(env, response, self.call_next)
            else:  # 执行控制器函数
                return_response = self.__get_response_data(env, response)
        except:  # 异常时执行的分支
            log.print(traceback.format_exc())
        else:  # 没有引发错误执行
            return [return_response.encode('utf-8')]

    # 启动自定义http服务器
    def run(self, host="", port=5111):
        httpServer.run(host=host, port=port, callback=self.__call__)
        # make_server：python内置http服务，不支持并发请求
        # server = make_server(host, port, self.__call__)
        # # 捕获服务中断异常
        # try:
        #     server.serve_forever() # 启动服务
        # except KeyboardInterrupt:
        #     print('homepy已停止运行···')

"""
1. 单例实例化
2. wsgi协议规定：入口文件必须存在命名为application的可被调用对象
"""
application = Application()

# 导入全部控制器文件(获取全部注解路由)
module_lists = os.listdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app'))  # 扫描app目录
# 遍历全部控制器模块
for module_name in module_lists:
    if module_name != 'common':  # 排除 common 目录
        # 递归遍历 controller 目录
        controller_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', module_name, 'controller')
        for root, dirs, files in os.walk(controller_path):
            # print(root, dirs, files)
            # D:\project\python\pydyProject\app\home\controller ['my', '__pycache__'] ['Index.py']
            # D:\project\python\pydyProject\app\home\controller\my ['__pycache__'] ['MyIndex.py']
            for controller_name in files:
                if controller_name[-3:] == '.py' and controller_name != '__init__.py':
                    controller_prefix = root.replace(os.path.sep, '.').split(f'app.{module_name}.controller')[
                        1]  # 拆分字符串为列表
                    import_module(f'app.{module_name}.controller{controller_prefix}.{controller_name[:-3]}')