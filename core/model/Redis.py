import json

import redis

from config.DatabaseConfig import DatabaseConfig


class Redis:
    # 构造函数
    def __init__(self, active_index: int = 0):
        self.active_index = active_index
        self.link_obj_list = []  # db连接对象

    def init(self, active_index: int = 0):
        """
        初始化配置
        """
        self.active_index = active_index

        if len(self.link_obj_list) - 1 >= active_index:  # 如果连接对象已存在
            return self
        else:
            db_config = DatabaseConfig.redis[active_index]  # active_index为配置激活索引
            link_obj = redis.Redis(
                host=db_config.get('host'),
                port=db_config.get('port'),
                password=db_config.get('password'),
                db=0
            )
            self.link_obj_list.append(link_obj)
            return self

    def delete(self, *names):
        """
            描述：键名操作, 删除redis中一个或多个键的所有数据
            参数：
                *names 待删除的单个或多个键名参数
            注：
                1.返回值：int 删除的个数
         """
        return self.link_obj_list[self.active_index].delete(*names)

    def set(self, key, val):
        """
        描述：设置字符串
        参数：
            key str 设置的键名
            val any(支持python任意基础数据类型) 设置的键值
        返回值： 设置成功返回true
        注：
            1.设置键名如果已存在会报错
        """
        return self.link_obj_list[self.active_index].set(key, json.dumps(val))

    def get(self, key):
        """
        描述：获取字符串
        参数：
            key str 获取的键名
        返回值： 不存在返回None
        """
        result = self.link_obj_list[self.active_index].get(key)
        if result:
            return result.decode()
        else:
            return result

    def sadd(self, name, *values):
        """
        描述：添加集合
        参数：
            name str 键名
            *values 待新增的单个或多个集合元素
        返回值： 插入的集合元素个数
        注：
            1.若插入已有的元素，则自动不插入
        """
        return self.link_obj_list[self.active_index].sadd(name, *values)

    def sismember(self, name, value):
        """
        描述：判断某个值是否在集合中
        参数：
            name str 键名
            value 集合元素
        返回值： 值存在返回True 值不存在或集合键名name本身不存在返回 False
        """
        return self.link_obj_list[self.active_index].sismember(name, value)

    def srem(self, name, *values):
        """
           描述：删除集合中的一个或多个元素
           参数：
               name str 键名
               *values 待删除的单个或多个集合元素
           返回值： 返回删除的元素个数 int
           """
        return self.link_obj_list[self.active_index].srem(name, *values)


# 单例
redis_obj = Redis()
