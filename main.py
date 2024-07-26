"""
wsgi协议规定：入口文件必须存在命名为application的可被调用对象
"""
from core.Application import application

"""
非wsgi协议应用入口
"""
if __name__ == '__main__':
    application.run(port=5111)  # 启动自定义http服务器
