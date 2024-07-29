import pymysql
import pymysql.cursors
from config.DatabaseConfig import DatabaseConfig
from typing import List, Dict, Tuple
import math
from core.common.password import md5, sha1

class Mysql:
    # 构造函数
    def __init__(self, active_index: int = 0):
        self.db_config = None  # 数据库配置
        self.prefix = ''  # 表前缀
        self.database = ''  # 数据库名

        self.link_obj = None  # db连接对象
        self.cursor_obj = None  # db cursor对象
        self.table_name: str = ""  # 数据库表名

    # 析构函数
    def __del__(self):
        self.close()


    # 初始化配置
    def init(self, active_index: int = 0):
        self.db_config = DatabaseConfig.mysql[active_index]  # active_index为配置激活索引
        self.prefix = self.db_config['prefix']  # 表前缀
        self.database = self.db_config['database']  # 数据库名

        self.link_obj = pymysql.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            database=self.db_config['database'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            charset=self.db_config['charset'],
            # 获取带字段名数据
            cursorclass=pymysql.cursors.DictCursor
        )

        self.cursor_obj = self.link_obj.cursor()

    # 指定表
    def table(self, table_name='test'):
        if not table_name.startswith(self.prefix):
            table_name = self.prefix + table_name
        self.table_name = table_name
        return self

    """
    功能：新增，支持批量
   示例：
   # 返回值：新增首条id值(新增多条时，返回首条插入时的新增id)
    result = obj_mysql.table("student").add(
        field=['name', 'age'],
        fieldVal=[
            ('july', '14'),
            ('june', '25'),
            ('marin', '36')
        ]
    )
    """
    def add(self, field: List, fieldVal=None) -> int:

        # 1.字段sql拼接
        if fieldVal is None:
            fieldVal = []
        field_str = ''
        for val in field:
            field_str += f'{val},'
        field_str = field_str.rstrip(',')

        # 字段参数绑定符号"%s"拼接
        bind_symbol = ('%s,' * len(fieldVal[0])).rstrip(',')

        sql = f'insert into {self.table_name}({field_str}) values({bind_symbol})'
        # 执行SQL语句
        self.cursor_obj.executemany(sql, fieldVal)
        # 涉及写操作注意要提交
        self.link_obj.commit()
        # 新增首条id值(新增多条时，返回首条插入时的新增id)
        return self.cursor_obj.lastrowid

    """
           功能：删除，支持批量
          返回值：删除行数
          示例：
           result = mysql.table("student").delete(
               whereSql='where id = ?',
               whereSqlVal=[(25), (26), (27)]
           )
       """

    def delete(self, whereSql: str, whereSqlVal=None):
        if whereSqlVal is None:
            whereSqlVal = []

        whereSql = whereSql.replace("?", "%s")
        sql = f"delete from {self.table_name} {whereSql}"
        # 执行SQL语句
        self.cursor_obj.executemany(sql, whereSqlVal)
        # 涉及写操作注意要提交
        self.link_obj.commit()
        # 影响的行数
        return self.cursor_obj.rowcount

    """
    修改，支持批量不同修改
    示例1：批量相同修改 
        result = mysql.table("student").edit(
                sql='set gender=? where name=?',
                sqlVal=[('女','Tom')]
            )
    示例2：批量不同修改 
        result = mysql.table("student").edit(
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

        sql = sql.replace("?", "%s")
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
    result = mysql.table('student').query(
        whereSql='where id>?',
        whereSqlVal=[12]
    )
    """
    def query(self, whereSql: str = '', whereSqlVal: list = None) -> List:
        # 执行SQL语句
        whereSql = whereSql.replace("?", "%s")
        self.cursor_obj.execute(f"select * from `{self.table_name}` {whereSql}", whereSqlVal)
        return_data = self.cursor_obj.fetchall()
        return return_data

    """
        查询 - 分页查询
        示例：
        result = mysql.table('student').query_page(
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
        whereSql = whereSql.replace("?", "%s")
        sql1 = f"select sql_calc_found_rows  * from `{self.table_name}` {whereSql}  limit {start_index},{pageSize}"
        self.cursor_obj.execute(sql1, whereSqlVal)
        result = {'items': self.cursor_obj.fetchall()}
        sql2 = "select found_rows() as total_rows"
        self.cursor_obj.execute(sql2)
        total_rows = self.cursor_obj.fetchall()[0]['total_rows']
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
    result = mysql.table('student')query_dif(
        whereSql='where id>?',
        whereSqlVal=[12],
        field='id'
    )
    """

    def query_dif(self, whereSql: str = '', whereSqlVal: list = None, field: str = 'id') -> List:

        # 执行SQL语句
        whereSql = whereSql.replace("?", "%s")
        self.cursor_obj.execute(f"select distinct(`{field}`)  from {self.table_name} {whereSql}", whereSqlVal)
        result = self.cursor_obj.fetchall()
        return_result = []
        for val in result:
            return_result.append(val[field])
        return return_result

    """
        查询 - 多表查询
        # query_uni({"tb1":"a", "tb2" : "b"}, ['tb1_key', 'tb2_key'], "whereSql", [whereSqlVal], false)
        # query_uni({"tb1":"a", "tb2" : "b", "tb3" : "c"},[['tb1_key1', 'tb1_key2'], 'tb2_key','tb3_key'], "whereSql", [whereSqlVal], false)
        示例：
        result = mysql.query_uni(
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
            whereSql = ' and ' + whereSql.replace("where", "").replace("?", "%s")

        fields_sql = '*'
        # 字段名添加表前缀
        if fieldsAlias:
            fields_sql = self.__getUniTbFields(uniTb)

        sql = f"select {fields_sql} from {uni_tb_sql} where {uni_key_sql} {whereSql}"
        self.cursor_obj.execute(sql, whereSqlVal)
        return_result = self.cursor_obj.fetchall()
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
        currentPage=currentPage,
        pageSize=pageSize,
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
            whereSql = ' and ' + whereSql.replace("where", "").replace("?", "%s")

        fields_sql = '*'
        # 字段名添加表前缀
        if fieldsAlias:
            fields_sql = self.__getUniTbFields(uniTb)

        start_index = (currentPage - 1) * pageSize  # 计算起始索引

        sql1 = f"select sql_calc_found_rows {fields_sql} from {uni_tb_sql} where {uni_key_sql} {whereSql} limit {start_index},{pageSize}"
        self.cursor_obj.execute(sql1, whereSqlVal)
        result = {'items': self.cursor_obj.fetchall()}
        sql2 = "select found_rows() as total_rows"
        self.cursor_obj.execute(sql2)
        total_rows = self.cursor_obj.fetchone()['total_rows']
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
            sql = f"select concat('{tb}_',GROUP_CONCAT(COLUMN_NAME SEPARATOR ',{tb}_')) as fields_alias from information_schema.COLUMNS where table_name = '{prefix}{tb}' and table_schema = '{self.database}'"
            self.cursor_obj.execute(sql)
            columnAliasName = self.cursor_obj.fetchone()['fields_alias']
            tb_all_fields_alias = columnAliasName.split(",")  # 以, 为标志拆分字符串
            for fields_alias in tb_all_fields_alias:
                field_name = fields_alias[len(tb + '_'):]
                fields_sql += f'{tb_alias}.{field_name} as {fields_alias},'
        return fields_sql.rstrip(',')


    # 关闭连接
    def close(self):
        # 先关闭游标
        if self.cursor_obj:
            self.cursor_obj.close()
            self.cursor_obj = None
        # 后关闭连接
        if self.link_obj:
            self.link_obj.close()
            self.link_obj = None

    # 加密字段
    def encrypt_password(self, msg: any):
        return md5(sha1(msg))


