from typing import final

from core.ComtrollerBase import ComtrollerBase
from core.model.Mysql import Mysql
from core.model.Mongodb import Mongodb
from core.model.Sqlite import Sqlite
from core.model.Redis import redis_obj

""" 
1.操作 mysql 示例：
    mysql_obj = self.db(dbtype='mysql', active_index=0)
    result = mysql_obj.table('member').query(
            whereSql='where id=?',
            whereSqlVal=[20]
        )
    或
    mysql_obj = self.db() # 默认使用mysql，0索引配置项
    result = mysql_obj.table('member').query(
            whereSql='where id=?',
            whereSqlVal=[20]
        )
        
2.操作 mongodb 示例：
    mongodb_obj = self.db(dbtype='mongodb', active_index=0)
    result =  mongodb_obj.database('meijieyi_ziyuan').table('wangzhan_meiti_show').query(
            where={'id': '66421'},
        )
        

3.操作 sqlite 示例：
    sqlite_obj = self.db(dbtype='sqlite', active_index=0)
    result = sqlite_obj.table('student').query(
            whereSql='where id>?',
            whereSqlVal=[12]
        )
        
4.操作 Redis 示例：
    redis_obj = self.db(dbtype='redis', active_index=0)
    result = redis_obj.get('login-admin')
"""


class Model(ComtrollerBase):
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

    # 类方法
    @final
    def db(self, dbtype='mysql', active_index=0):
        if dbtype == 'mongodb':
            mongodb = Mongodb()
            mongodb.init(active_index)
            return mongodb
        elif dbtype == 'mysql':
            mysql = Mysql()
            mysql.init(active_index)
            return mysql
        elif dbtype == 'sqlite':
            sqlite = Sqlite()
            sqlite.init(active_index)
            return sqlite
        elif dbtype == 'redis':
            return redis_obj.init(active_index)
