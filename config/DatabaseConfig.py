# 数据库配置
# 注：默认使用索引0的配置
class DatabaseConfig:
    mongodb = [
        # 卉生媒介易api数据
        {
            "host": "139.196.145.155",
            "port": "27017",
            "user": "root",
            "password": "mongodb@itinhs@dzy2022*8",
            "database": "meijieyi_ziyuan",
        }
    ]

    mysql = [
        # 宝塔本地卉生新后台数据
        {
            "host": "192.168.0.211",
            "port": 3306,
            "database": "hs_admin",
            "user": "hs_admin",
            "password": "ZBRCpjDzD7G2emsL",
            "charset": "utf8",
            "prefix": "hs_",
        }
    ]

    redis = [
        # 卉生美橙阿里云redis
        {
            "host": "192.168.0.211",
            "port": 6379,
            "password": "123456",
        }
    ]

    sqlite = [
        # 当前项目目录下sqlite数据库
        {
            "path": "data/product_price_criterion.db",
            "prefix": "",
        },
    ]