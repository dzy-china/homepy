from core.Application import application


# 装饰器路由系统
class DecoratorRoute:

    # 路由装饰器
    # 注：
    #   1.当文件启动时，会自动执行路径函数上的每个装饰器函数,把参数传递给__call__，把路径函数名传递给__call__返回值对应的函数
    #   2.此处因框架机制"路由唯一性原则"需求，并未实现路由装饰器下的路径函数,使用 getattr 获取带装饰器的控制器方法时，会返回None
    def __call__(self, route='/', method=['get', 'post']):
        def decorator(path_func):
            # print(route,method,decorated_obj.__module__)
            # /test ['get', 'post'] <function Index.test at 0x0000000002BCA280>

            # 追加路由前判断是否存在相同的url路由
            for route_info in application.routes:
                if route == route_info['route']:
                    exception_msg = f'路径方法 <<{path_func.__module__}.{path_func.__name__}>>'
                    exception_msg += f' 与 <<{route_info["route_path_func_module_path"]}.{route_info["route_path_func"].__name__}>>'
                    exception_msg += " 存在冲突的路由：" + route
                    raise Exception(exception_msg)

            # 装载路由
            application.routes.append({
                'route': route,  # 路由url
                'route_method': method, # 路由请求方法
                'route_path_func': path_func, # 路由路径函数
                'route_path_func_name': path_func.__name__, # 路由路径函数名
                'route_path_func_args': path_func.__code__.co_varnames,  # 路径函数参数, ('name', 'age')
                'route_path_func_module_path': path_func.__module__,  # 路径函数"模块路径", 'app.home.controller.Index'
                'route_path_func_type_limit': path_func.__annotations__  # 类型约束，{'name': <class 'str'>, 'age': <class 'int'>, 'return': <class 'str'>}
            })
        return decorator


route = DecoratorRoute()

