import re
from importlib import import_module


# 默认路由系统
# 没有装饰器的路由遵循请求方式： /模块/控制器/方法
# 控制器url访问规则：1.小写+下划线方式 2.多级控制器用'.'符号连接
# 示例：
# 实际目录结构： /home/MyIndex.py test方法 或 /home/order/MyIndex.py test方法
# url访问路径： /home/my_index/test 或 /home/order.my_index/test
class DefaultRoute:
    module_name = ''  # 模块
    controller_full_name, controller_name = ('', '')  # 控制器
    method_name = ''  # 方法

    # 获取默认路由的模块名
    def get_module_name(self, request_url) -> str:
        if match_obj := re.match(r'/(\w+)', request_url):
            return match_obj.group(1)
        else:
            return "home"  # 返回默认模块名

    # 获取路由的控制器名对应的python模块路径表示(全部控制器名，仅控制器名)
    # request_url示例： /home/order.my_order/index
    def get_controller_name(self, request_url) -> tuple:
        # 判断url中是否存在控制器
        if match_obj := re.match(r'/\w+/([\w.]+)', request_url):
            # 查找最后一次'.'符号，并进行分割成元组
            controller_alias_tuple = match_obj.group(1).rpartition(".")
            # 小写下划线连接的字符串变为大驼峰形式 my_order => MyOrder
            controller_name = controller_alias_tuple[2].title().replace("_", "")
            return controller_name if controller_alias_tuple[0] == '' else controller_alias_tuple[0] + '.' + controller_name, controller_name
        else:
            return "Index", "Index"

    # 获取默认路由的方法名
    def get_method_name(self, request_url) -> str:
        if match_obj := re.match(r'/\w+/[\w.]+/(\w+)', request_url):
            return match_obj.group(1)
        else:
            return "index"  # 返回默认方法名

    # 检测默认路由请求是否存在
    def is_exists_default_request(self, request_url):
        self.module_name = self.get_module_name(request_url)
        self.controller_full_name, self.controller_name = self.get_controller_name(request_url)
        self.method_name = self.get_method_name(request_url)
        try:
            # <class 'app.home.controller.Index.Index'>
            controller_class = getattr(import_module(f'app.{self.module_name}.controller.{self.controller_full_name}'),
                                       self.controller_name)

            # <bound method Index.demo of <app.home.controller.Index.Index object at 0x0000000002DE20A0>>
            # getattr(controller_class(), self.method_name)

            # <function Index.demo at 0x0000000002BE2430>
            # 注：如果控制器上存在装饰器，会返回None
            function_obj = getattr(controller_class, self.method_name)
        except:
            return False
        else:
            return controller_class, function_obj


defaultRoute = DefaultRoute()
