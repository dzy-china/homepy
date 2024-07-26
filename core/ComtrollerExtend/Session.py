from typing import final

from core.ComtrollerExtend.Cookie import Cookie
from core.common.password import md5
import shutil, os, uuid, time

"""
#获取 session： self.session('name')
#设置 session: self.session('name', 'dzy')
参数：
    1个参数，是获取值
    2个参数是设置session，第一个参数是键，第二个参数是值(字符串/整数/小数)
"""


# 1.获取session session('name')
# 2.设置session  session('name', 'dzy')

class Session(Cookie):
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

        # session存活时间(秒):30分钟
        self.__session_expires_time = 60 * 30

        # session_id
        self.__session_id = str(uuid.uuid1())

        # 记录新增session
        self.__temp_session = {}

    # session数据存放目录
    def __get_session_path(self, args):
        homepy_session_dir_path = os.path.join(os.getcwd(), 'homepy', 'data', 'session')
        homepy_sessid_dir_path = os.path.join(homepy_session_dir_path, self.__session_id)
        homepy_sessid_file_path = os.path.join(homepy_sessid_dir_path, f'{md5(args[0])}.txt')
        homepy_sessid_expires_file_path = os.path.join(homepy_sessid_dir_path, 'expires.txt')
        return homepy_sessid_dir_path, homepy_sessid_file_path, homepy_sessid_expires_file_path

    #  # 重置session过期时间
    def __reset_session_expires_time(self, file_path, expires_time):
        with open(file_path, "w") as file_obj:
            file_obj.write(str(int(time.time()) + expires_time))

    # session操作
    @final
    def session(self, *args):
        if len(args) == 1:  # 获取session
            if (session_val := self.__temp_session.get(args[0])) is not None:  # 取刚设置的session
                return session_val
            # 根据session_id取服务器中文件存储的session
            else:
                self.__session_id = self.cookie('HOMEPY_SESSID')
                homepy_sessid_dir_path, homepy_sessid_file_path, homepy_sessid_expires_file_path = self.__get_session_path(args)
                if self.__session_id and os.path.exists(homepy_sessid_file_path):  # 如果session_id和session文件存在
                    # 读取过期时间
                    file_obj1 = open(homepy_sessid_expires_file_path, "r")
                    expire_timestamp = file_obj1.read()  # 读取文件所有内容
                    file_obj1.close()

                    expire_timestamp = int(expire_timestamp.strip())  # 去除字符串两端空格

                    # 读取session内容
                    if expire_timestamp <= int(time.time()): # 过期删除
                        shutil.rmtree(homepy_sessid_dir_path)  # 递归删除非空目录
                        return ''
                    else:  # 读取 session 值
                        file_obj2 = open(homepy_sessid_file_path, "r")
                        data = file_obj2.read()  # 读取文件所有内容
                        file_obj2.close()
                        # 返回数据前，重置 session 和 session_id 过期时间999年
                        self.cookie('HOMEPY_SESSID', self.__session_id,
                                    {'path': '/', 'max-age': 999 * 365 * 24 * 3600})
                        self.__reset_session_expires_time(homepy_sessid_expires_file_path, self.__session_expires_time)
                        return eval(data)
                else:  # session_id 或 session文件不存在
                    return ''
        elif len(args) == 2:  # 设置session
            # 设置cookie session_id
            if len(self.__temp_session) == 0:  # 避免cookie多次设置
                # 设置session_id过期时间999年
                self.cookie('HOMEPY_SESSID', self.__session_id, {'path': '/', 'max-age': 999 * 365 * 24 * 3600})

            # 如果目录不存在
            homepy_sessid_dir_path, homepy_sessid_file_path, homepy_sessid_expires_file_path = self.__get_session_path(args)
            if not os.path.exists(homepy_sessid_dir_path):
                os.makedirs(homepy_sessid_dir_path, 0o777)  # 递归创建目录

            # 设置session
            file_obj = open(homepy_sessid_file_path, "w")
            # 写入内容到文件
            file_obj.write(repr(args[1]))
            file_obj.close()
            # 记录新增session
            self.__temp_session[args[0]] = args[1]
            # 重置 session 过期时间
            self.__reset_session_expires_time(homepy_sessid_expires_file_path, self.__session_expires_time)


