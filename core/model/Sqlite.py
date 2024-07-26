import math
import sqlite3
from typing import List, Dict

from config.DatabaseConfig import DatabaseConfig


class Sqlite:
    # 构造函数
    def __init__(self):
        self.db_config = None  # 数据库配置
        self.prefix = ''  # 表前缀
        self.table_name: str = ""  # 数据库表名

        self.link_obj = None  # db连接对象
        self.cursor_obj = None  # db cursor对象

    # 析构函数
    def __del__(self):
        # 先关闭游标
        if self.cursor_obj:
            self.cursor_obj.close()
            self.cursor_obj = None
        # 再关闭连接对象
        if self.link_obj:
            self.link_obj.close()
            self.link_obj = None

    # 初始化配置
    def init(self, active_index: int = 0):
        # 获取 连接配置
        self.db_config = DatabaseConfig.sqlite[active_index]  # active_index为配置激活索引
        if self.db_config.get('prefix'):
            self.prefix = self.db_config['prefix']

        # 创建连接对象
        self.link_obj = sqlite3.connect(self.db_config['path'])

        # 生成游标
        self.cursor_obj = self.link_obj.cursor()

    # 指定表
    def table(self, table_name='test'):
        if not table_name.startswith(self.prefix):
            table_name = self.prefix + table_name
        self.table_name = table_name
        return self

    """
       功能：新增，支持批量
       返回值：新增行数
       示例：
        result = sqlite_obj.table("student").add(
            field=['name', 'age'],
            fieldVal=[
                ('july', '14'),
                ('june', '25'),
                ('marin', '36')
            ]
        )
        """

    def add(self, field: List, fieldVal=None):
        if fieldVal is None:
            fieldVal = []

        # 1.字段sql拼接
        field_str = ''
        for val in field:
            field_str += f'{val},'
        field_str = field_str.rstrip(',')

        # 字段参数绑定符号"%s"拼接
        bind_symbol = ('?,' * len(fieldVal[0])).rstrip(',')

        sql = f'insert into {self.table_name}({field_str}) values({bind_symbol})'
        # 执行SQL语句
        result_cursor_obj = self.cursor_obj.executemany(sql, fieldVal)
        # 涉及写操作注意要提交
        self.link_obj.commit()
        return result_cursor_obj.rowcount

    """
           功能：删除，支持批量
          返回值：删除行数
          示例：
           result = sqlite_obj.table("student").delete(
               whereSql='where id = %s',
               whereSqlVal=[(25), (26), (27)]
           )
       """

    def delete(self, whereSql: str, whereSqlVal=None):
        if whereSqlVal is None:
            whereSqlVal = []

        sql = f"delete from {self.table_name} {whereSql}"
        # 执行SQL语句
        self.cursor_obj.executemany(sql, whereSqlVal)
        # 涉及写操作注意要提交
        self.link_obj.commit()
        # 影响的行数
        return self.cursor_obj.rowcount

    """
        功能：修改，支持批量不同修改
        返回值：修改受影响行数
        示例1：批量相同修改 
            result = sqlite_obj.table("student").edit(
                    sql='set gender=? where name=?',
                    sqlVal=[('女','Tom')]
                )
        示例2：批量不同修改 
            result = sqlite_obj.table("student").edit(
                sql='set age=? where name=?',
                sqlVal=[
                    ('10', 'july'),
                    ('11', 'june'),
                    ('12', 'marin'),
                ]
            )
        """

    def edit(self, sql: str, sqlVal=None):

        if sqlVal is None:
            sqlVal = []
        sql = f"update {self.table_name} {sql}"
        # 执行SQL语句
        self.cursor_obj.executemany(sql, sqlVal)
        # 涉及写操作注意要提交
        self.link_obj.commit()
        # 影响的行数
        return self.cursor_obj.rowcount

    """
        查询 - 普通查询
        示例：
        result = sqlite_obj.table('student').query(
            whereSql='where id>?',
            whereSqlVal=[12]
        )
        """

    def query(self, whereSql: str = '', whereSqlVal: list = None):
        # 执行SQL语句
        if not whereSqlVal:
            self.cursor_obj.execute(f"select * from `{self.table_name}` {whereSql}")
        else:
            self.cursor_obj.execute(f"select * from `{self.table_name}` {whereSql}", whereSqlVal)
        return_data = self.cursor_obj.fetchall()
        # 遍历每行元组数据
        return_result = []
        for row in return_data:
            return_result.append(self.__dict_factory(self.cursor_obj, row))
        return return_result

    """
            查询 - 分页查询
            示例：
            result = sqlite_obj.table('student').query_page(
                whereSql='where id>?',
                whereSqlVal=[12],
                currentPage=1,
                pageSize=5
            )
            """

    def query_page(self, whereSql: str = '', whereSqlVal: list = None, currentPage: int = 1, pageSize: int = 10) -> Dict:
        # 分页参数强制转int
        currentPage = int(currentPage)
        pageSize = int(pageSize)

        start_index = (currentPage - 1) * pageSize  # 计算起始索引
        sql1 = f"select * from `{self.table_name}` {whereSql}  limit {pageSize} offset {start_index}"

        if not whereSqlVal:
            self.cursor_obj.execute(sql1)
        else:
            self.cursor_obj.execute(sql1, whereSqlVal)

        return_data = self.cursor_obj.fetchall()

        # 遍历每行元组数据
        return_result = []
        for row in return_data:
            return_result.append(self.__dict_factory(self.cursor_obj, row))
        result = {'items': return_result}

        sql2 = f"select count(*) as total_rows from `{self.table_name}` {whereSql}"

        if not whereSqlVal:
            self.cursor_obj.execute(sql2)
        else:
            self.cursor_obj.execute(sql2, whereSqlVal)
        total_rows = self.cursor_obj.fetchall()[0][0]

        result['pages'] = {
            "totalCount": total_rows,
            "pageCount": math.ceil(total_rows / pageSize),
            "pageSize": pageSize,
            "currentPage": currentPage
        }
        return result

    """
        查询 - 查询某列不同值
        示例：
        result = sqlite_obj.table('student')query_dif(
            whereSql='where id>?',
            whereSqlVal=[12],
            field='id'
        )
        """

    def query_dif(self, whereSql: str = '', whereSqlVal: list = None, field: str = 'id') -> List:

        # 执行SQL语句
        if not whereSqlVal:
            self.cursor_obj.execute(f"select distinct(`{field}`)  from {self.table_name} {whereSql}")
        else:
            self.cursor_obj.execute(f"select distinct(`{field}`)  from {self.table_name} {whereSql}", whereSqlVal)

        result = self.cursor_obj.fetchall()
        return_result = []
        for val in result:
            return_result.append(val[0])
        return return_result

    """
            查询 - 多表查询
            # query_uni({"tb1":"a", "tb2" : "b"}, ['tb1_key', 'tb2_key'], "whereSql", [whereSqlVal], false)
            # query_uni({"tb1":"a", "tb2" : "b", "tb3" : "c"},[['tb1_key1', 'tb1_key2'], 'tb2_key','tb3_key'], "whereSql", [whereSqlVal], false)
            示例：
            result = sqlite_obj.query_uni(
                uniTb={"hs_archives": "a", "hs_addonarticle": "b","hs_arctype": "c"},
                uniKey=[['id','typeid'],'aid', 'id'],
                whereSql='where a.id>?',
                whereSqlVal=[12],
                fieldsAlias=True
            )
            """

    def query_uni(self,
                  uniTb: Dict,
                  uniKey: List,
                  whereSql: str = '',
                  whereSqlVal: list = None,
                  fieldsAlias: bool = False
                  ) -> List:

        # 1.拼接表
        uni_tb_sql = ""
        for k, v in uniTb.items():
            if not k.startswith(self.prefix):
                k = self.prefix + k
            uni_tb_sql += f"{k} as {v},"
        uni_tb_sql = uni_tb_sql.rstrip(',')

        # 2.拼接关联键
        uni_key_sql = ""
        tb_alias = list(uniTb.values())  # 获取全部表别名
        primary_tb_uni_key = uniKey[0]  # 获取主表全部关联键名
        if isinstance(primary_tb_uni_key, list):
            for index, val in enumerate(primary_tb_uni_key):
                uni_key_sql += f"{tb_alias[0]}.{val} = {tb_alias[index + 1]}.{uniKey[index + 1]} and "
        else:
            for index in range(len(uniKey) - 1):
                uni_key_sql += f"{tb_alias[0]}.{uniKey[0]} = {tb_alias[index + 1]}.{uniKey[index + 1]} and "
        uni_key_sql = uni_key_sql.rstrip().rstrip('and')

        # 3.拼接查询条件
        if whereSql:
            whereSql = ' and ' + whereSql.replace("where", "")

        fields_sql = '*'
        # 字段名添加表前缀
        if fieldsAlias:
            fields_sql = self.__getUniTbFields(uniTb)
        sql = f"select {fields_sql} from {uni_tb_sql} where {uni_key_sql} {whereSql}"
        if not whereSqlVal:
            self.cursor_obj.execute(sql)
        else:
            self.cursor_obj.execute(sql, whereSqlVal)
        return_data = self.cursor_obj.fetchall()
        # 遍历每行元组数据
        return_result = []
        for row in return_data:
            return_result.append(self.__dict_factory(self.cursor_obj, row))
        return return_result

    """
    查询 - 多表分页查询
    # query_uni_page({"tb1":"a", "tb2" : "b"}, ['tb1_key', 'tb2_key'], "whereSql", [whereSqlVal], false,1,10)
    # query_uni_page({"tb1":"a", "tb2" : "b", "tb3" : "c"},[['tb1_key1', 'tb1_key2'], 'tb2_key','tb3_key'], "whereSql", [whereSqlVal], false,1,10)
    示例：
    result = mysql.query_uni_page(
        uniTb={"hs_archives": "a", "hs_addonarticle": "b","hs_arctype": "c"},
        uniKey=[['id','typeid'],'aid', 'id'],
        whereSql='where a.id>?',
        whereSqlVal=[12],
        fieldsAlias=True,
        currentPage=1,
        pageSize=5,
    )
    """

    def query_uni_page(self,
                       uniTb: Dict,
                       uniKey: List,
                       whereSql: str = '',
                       whereSqlVal: list = None,
                       fieldsAlias: bool = False,
                       currentPage: int = 1,
                       pageSize: int = 10,
                       ) -> dict:
        # 分页参数强制转int
        currentPage = int(currentPage)
        pageSize = int(pageSize)

        # 1.拼接表
        uni_tb_sql = ""
        for k, v in uniTb.items():
            if not k.startswith(self.prefix):
                k = self.prefix + k
            uni_tb_sql += f"{k} as {v},"
        uni_tb_sql = uni_tb_sql.rstrip(',')

        # 2.拼接关联键
        uni_key_sql = ""
        tb_alias = list(uniTb.values())  # 获取全部表别名
        primary_tb_uni_key = uniKey[0]  # 获取主表全部关联键名
        if isinstance(primary_tb_uni_key, list):
            for index, val in enumerate(primary_tb_uni_key):
                uni_key_sql += f"{tb_alias[0]}.{val} = {tb_alias[index + 1]}.{uniKey[index + 1]} and "
        else:
            for index in range(len(uniKey) - 1):
                uni_key_sql += f"{tb_alias[0]}.{uniKey[0]} = {tb_alias[index + 1]}.{uniKey[index + 1]} and "
        uni_key_sql = uni_key_sql.rstrip().rstrip('and')

        # 3.拼接查询条件
        if whereSql:
            whereSql = ' and ' + whereSql.replace("where", "")

        fields_sql = '*'
        # 字段名添加表前缀
        if fieldsAlias:
            fields_sql = self.__getUniTbFields(uniTb)

        start_index = (currentPage - 1) * pageSize  # 计算起始索引
        sql1 = f"select {fields_sql} from {uni_tb_sql} where {uni_key_sql} {whereSql} limit {pageSize} offset {start_index}"
        if not whereSqlVal:
            self.cursor_obj.execute(sql1)
        else:
            self.cursor_obj.execute(sql1, whereSqlVal)
        return_data = self.cursor_obj.fetchall()
        # 遍历每行元组数据
        return_result = []
        for row in return_data:
            return_result.append(self.__dict_factory(self.cursor_obj, row))
        result = {'items': return_result}
        sql2 = f"select count(*) as total_rows from {uni_tb_sql} where {uni_key_sql} {whereSql}"
        if not whereSqlVal:
            self.cursor_obj.execute(sql2)
        else:
            self.cursor_obj.execute(sql2, whereSqlVal)
        total_rows = self.cursor_obj.fetchall()[0][0]
        result['pages'] = {
            "totalCount": total_rows,
            "pageCount": math.ceil(total_rows / pageSize),
            "pageSize": pageSize,
            "currentPage": currentPage
        }
        return result

    #  多表查询时获取带别名(无前缀表名+下划线+字段名)的全部字段拼接的sql字符串
    def __getUniTbFields(self, uniTb):
        # sql拼接
        fields_sql = ''
        prefix = self.prefix  # 获取表前缀
        for tb, tb_alias in uniTb.items():
            # 去除表前缀
            if tb.startswith(prefix):
                tb = tb[len(prefix):]
            # ***获取某表添加表前缀后的全部字段名
            sql = f"PRAGMA table_info('{tb}')"
            self.cursor_obj.execute(sql)
            tb_all_fields = self.cursor_obj.fetchall()
            for fields_alias in tb_all_fields:
                fields_sql += f'{tb_alias}.{fields_alias[1]} as {tb}_{fields_alias[1]},'
        return fields_sql.rstrip(',')

    # 将每行元组数据转化为字典形式
    def __dict_factory(self, cursor_obj, row):
        # 列表推导式
        return dict((field_tuple[0], row[index]) for index, field_tuple in enumerate(cursor_obj.description))
