import pymongo
from typing import List, Dict, Tuple
from urllib import parse
from pymongo.collation import Collation
from config.DatabaseConfig import DatabaseConfig
import math
from bson.objectid import ObjectId


class Mongodb:
    # 构造函数
    def __init__(self):
        # 定义连接对象
        self.link_obj = None

        # 数据库名对象
        self.database_obj = None

        # 数据库表名
        self.table_name: str = ""

    # 析构函数
    def __del__(self):
        if self.link_obj:
            self.link_obj.close()
            self.link_obj = None

    # 初始化配置
    def init(self, active_index: int = 0):
        # 初始化mongodb数据库配置
        mongodb_config = DatabaseConfig.mongodb[active_index]  # active_index为配置激活索引
        # 转义用户名和密码
        user = parse.quote_plus(mongodb_config['user'])
        passwd = parse.quote_plus(mongodb_config['password'])
        link_str = f"mongodb://{user}:{passwd}@{mongodb_config['host']}:{mongodb_config['port']}"
        # 创建mongodb连接对象
        self.link_obj = pymongo.MongoClient(link_str)

        # 数据库名对象
        self.database_obj = self.link_obj[DatabaseConfig.mongodb[active_index]['database']]

    # 重置 数据库对象
    def database(self, database_name: str):
        # 指定数据库
        self.database_obj = self.link_obj[database_name]
        return self

    # 指定表名
    def table(self, table_name: str):
        self.table_name = table_name
        return self

    def get_database_list(self):
        """
            # 获取全部数据库名
            obj_mongodb = self.db(dbtype='mongodb', active_index=0)
            database_list = obj_mongodb.get_database_list()
        """
        return self.link_obj.list_database_names()


    def get_table_list(self) -> List[str]:
        """
           # 获取全部表(集合)名
           obj_mongodb = self.db(dbtype='mongodb', active_index=0)
           collection_list = obj_mongodb.database('fenlei_zimeiti').get_collection_list()
       """
        return self.database_obj.list_collection_names()



    def table_copy_to(self, new_table_name):
        """
        把 company 集合的数据完全复制到 new_company
        obj_mongodb = self.db(dbtype='mongodb', active_index=0)
        result = obj_mongodb.database('fenlei_zimeiti').table('company').table_copy_to('new_company')
        """

        # 指定数据库表(集合)
        table_obj = self.database_obj[self.table_name]
        table_obj.aggregate([{'$out': new_table_name}])


    def query(self,
              where: Dict = None,
              fieldFilter: Dict = None,
              sort: List[Tuple] = None
              ) -> List:
        """
        查询- 普通查询(where查询条件支持所有mongodb语法)
        obj_mongodb = self.db(dbtype='mongodb', active_index=0)
        result = obj_mongodb.table('meiti').query(
                    where={'id': {'$gt': '9980'}},
                    fieldFilter= {'_id': 0},
                    sort=[('id', 1)]
            )
        # 动态改变数据库查询
        result2 = obj_mongodb.database('fenlei_zimeiti').table('media_area').query()
        # 返回值：
        # 非空结果：[{...},[...]]
        # 空结果：[]
        """

        # fieldFilter = {**{'_id': 0}, **fieldFilter}
        # 指定数据库表(集合)
        table_obj = self.database_obj[self.table_name]

        if sort:
            sql_find_obj = table_obj.find(where, fieldFilter).collation(
                Collation(locale='en_US', numericOrdering=True)).sort(sort)
        else:
            sql_find_obj = table_obj.find(where, fieldFilter)
        result = []
        for item in sql_find_obj:
            if '_id' in item:  # 如果结果集存在'_id'字段，_id 将 ObjectId类型转为字符串
                item['_id'] = str(item['_id'])
            result.append(item)
        return result



    def query_distinct(self,
                       where: Dict = None,
                       distinct: str = 'id',
                       ) -> List:
        """
        查询- 查询某个字段全部值(where查询条件支持所有mongodb语法)
        obj_mongodb = self.db(dbtype='mongodb', active_index=0)
        result = obj_mongodb.database('fenlei_zimeiti').table('meiti').query_distinct(
                    where={'id': {'$gt': '9980'}},
                    distinct='id'
            )
        """
        # 指定数据库表(集合)
        table_obj = self.database_obj[self.table_name]
        sql_find_obj = table_obj.find(where).collation(Collation(locale='en_US', numericOrdering=True)).distinct(
            distinct)
        result = []
        for item in sql_find_obj:
            result.append(item)
        return result

    """
            查询- 聚合查询
            管道操作符
                $group	将collection中的document分组，可用于统计结果
                $match	查询条件，只输出符合结果的文档
                $count	返回聚合管道此阶段的文档数计数
                $project	字段投影，修改输入文档的结构(例如重命名，增加、删除字段，创建结算结果等)
                $sort	将结果进行排序后输出
                $limit	限制管道输出的结果个数
                $skip	跳过制定数量的结果，并且返回剩下的结果
                $unwind	将数组类型的字段进行拆分
                $lookup	联表查询
                $geoNear	输出接近某一地理位置的有序文档。
                facet/bucket	分类搜索（MongoDB 3.4以上支持）

            表达式操作符
                $sum	计算总和，{$sum: 1}表示返回总和×1的值(即总和的数量),使用{$sum: '$制定字段'}也能直接获取制定字段的值的总和
                $avg	平均值
                $min	min
                $max	max
                $push	将结果文档中插入值到一个数组中
                $first	根据文档的排序获取第一个文档数据
                $last	同理，获取最后一个数据
            
            示例：
                from model import mongodb
                result = mongodb.database('fenlei_zimeiti').table('meiti').query_aggregate([
                                {'$match': {'id': {'$gte': 20}}},
                                {"$count": "totalNum"}
                            ])
                # 结果： [{'totalNum': 525}]
            
            # 返回值：数据不为空返回字典列表，数据为空返回空列表[]
            """

    def query_aggregate(self,
                        aggregate_list: List[Dict] = None,
                        ) -> List[Dict]:
        # 指定数据库表(集合)
        table_obj = self.database_obj[self.table_name]
        aggregate_result = table_obj.aggregate(aggregate_list,
                                               collation=Collation(locale="en_US", numericOrdering=True))
        result = []
        for item in aggregate_result:
            result.append(item)
        return result

    """
    查询 - 分页查询(where查询条件支持所有mongodb语法)
    obj_mongodb = self.db(dbtype='mongodb', active_index=0)
    result = obj_mongodb.table('meiti').query_page(
            where={'id': {'$gt': '9980'}},
            currentPage=currentPage,
            pageSize=pageSize,
            sort=[('id', 1)]
    )
    # 返回值：
    # 非空数据时：{'items': [{...},{...}], 'pages': {'totalCount': 100, 'pageCount': 10, 'pageSize': 100, 'currentPage': 1}}
    # 空数据时：{'items': [], 'pages': {'totalCount': 0, 'pageCount': 0, 'pageSize': 100, 'currentPage': 1}}
    """

    def query_page(self,
                   where: Dict = None,
                   fieldFilter: Dict = None,
                   currentPage: int = 1,
                   pageSize: int = 100,
                   sort: Dict = None
                   ) -> dict:
        # 分页参数强制转int
        currentPage = int(currentPage)
        pageSize = int(pageSize)

        # 指定数据库表(集合)
        table_obj = self.database_obj[self.table_name]

        # 计算起始索引
        start_index = (currentPage - 1) * pageSize

        # 查询语句
        # fieldFilter = {**{'_id': 0}, **fieldFilter}
        aggregate_list = []
        if fieldFilter:
            aggregate_list.append({'$project': fieldFilter})  # 追加过滤字段
        if where:
            aggregate_list.append({'$match': where})  # 追加查询条件
        if sort:
            aggregate_list.append({'$sort': sort})  # 排序字段

        # 多个聚合管道
        aggregate_list.append({
            "$facet": {
                "total": [{"$count": "total"}],
                "data": [
                    {"$skip": start_index},
                    {"$limit": pageSize}
                ]
            }
        })
        # 聚合查询
        # collation 参数设置用数字排序
        aggregate_result = table_obj.aggregate(aggregate_list,
                                               collation=Collation(locale="en_US", numericOrdering=True))

        # 获取 aggregate 聚合值
        temp_list = []
        for item in aggregate_result:  # 结果集游标遍历
            # item空数据时： {'total': [], 'data': []}
            #  将 _id 字段 ObjectId类型转为字符串
            for index, ele in enumerate(item['data']):
                if '_id' in ele:  # 如果结果集存在'_id'字段，_id 将 ObjectId类型转为字符串
                    item['data'][index]['_id'] = str(ele['_id'])
            # 放进数据容器
            temp_list.append(item)
        return_result = {'items': temp_list[0]['data']}
        # 求满足查询条件的数据总条数
        if temp_list[0].get('total'):  # 空数据判断
            total_rows = temp_list[0]['total'][0]['total']  # 获取查询满足结果总条数
        else:
            total_rows = 0

        return_result['pages'] = {
            "totalCount": total_rows,
            "pageCount": math.ceil(total_rows / pageSize),
            "pageSize": pageSize,
            "currentPage": currentPage
        }
        return return_result

    """
           插入单条数据
           # 返回值：返回新增_id字符串形式
           result = obj_mongodb.table('sites').add({'x': i})
           """

    def add_one(self, data: dict) -> str:
        result = self.database_obj[self.table_name].insert_one(data)
        return str(result.inserted_id)

    """
    插入多条数据
    返回值：默认 return_type='count'返回新增行数，可选值return_type='_id' 返回新增_id字符串值形式的列表
    result = obj_mongodb.table('sites').add([{'x': i} for i in range(2)])
    """
    def add_many(self, data: List[dict], return_type='count') -> list[str] | int:
        # 指定数据库表(集合)
        if isinstance(data, list):
            result = self.database_obj[self.table_name].insert_many(data)
            if return_type == '_id':
                return [str(id_obj) for id_obj in result.inserted_ids]
            else:
                return len(result.inserted_ids)

    """
        修改
        # 返回更改条数
        obj_mongodb = self.db(dbtype='mongodb', active_index=0)
        result = obj_mongodb.table('sites').update(
            where={"name": {"$regex": "^G"}},
            update_sql={"$set": {"url": '456'}}
        )
        """

    def update(self, where=None, update_sql=None) -> int:

        # 指定数据库表(集合)
        if where is None:
            where = {}
        if update_sql is None:
            update_sql = {}
        result = self.database_obj[self.table_name].update_many(where, update_sql)
        return result.modified_count

    """
       重命名表(集合)
      obj_mongodb = self.db(dbtype='mongodb', active_index=0)
      obj_mongodb.rename_table('sites')
   """

    def rename_table(self, new_table_name: str) -> None:
        self.database_obj[self.table_name].rename(new_table_name)

    """
        删除集合内容
        # 返回删除的条数
        # 注：如果不写删除条件会删除全部集合内文档
        obj_mongodb = self.db(dbtype='mongodb', active_index=0)
        result = obj_mongodb.table('sites').delete(
            where={ "name": {"$regex": "^F"} },
        )
    """

    def delete(self, where=None) -> int:
        if where is None:
            where = {}
        result = self.database_obj[self.table_name].delete_many(where)
        return result.deleted_count

    """
       删除集合(表)
      obj_mongodb = self.db(dbtype='mongodb', active_index=0)
      result = obj_mongodb.table('sites').drop()
       """

    def drop(self) -> None:
        self.database_obj[self.table_name].drop()

    """
          删除数据库
         obj_mongodb = self.db(dbtype='mongodb', active_index=0)
         result = obj_mongodb.drop_database('my_test')
          """

    def drop_database(self, database_name):
        self.link_obj.drop_database(database_name)

    def toObjectIDs(self, _id: str | list) -> list:
        """
        id转为ObjectID
        id类型支持：单个字符串，多个字符串(逗号间隔)，列表
        """
        if isinstance(_id, str):
            return [ObjectId(val) for val in _id.split(',')]
        elif isinstance(_id, list):
            return [ObjectId(val) for val in _id]

