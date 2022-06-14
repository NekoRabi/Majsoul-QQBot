import sqlite3

'''

    一个SQLite操作类，旨在优化SQLite使用
    
    以下是一些注释

    dbpath    : 数据库存储位置，如存放在 database/Majsoul/majsou.sqlite ，dbpath = 'Majsoul/majsou.sqlite'
    
    tablename : 表名
    
    col_param : 列名及其约束，是一个dict
    
        以玩家表为例，有玩家名，玩家id,UUID 三个属性，可写为下面的形式
        
        {
            id : [
                integer,
                primary key
            ],
            playername: [
                varcher(50),
                not null,
            ],
            UUID :[
                varcher(50),
                UNIQUE
            ]
        }
    
    fk  : 外键约束,下面是它的结构
    
        {
            表名: {
                {
                    本表列名:外表列名
                }        
            }
        }

'''


class DBHelper:

    def __init__(self):
        self.cx = None
        self.cursor = None

    def __del__(self):
        self.closeconnection()
        super().__del__()

    def testconnect(self):
        if self.cx or self.cursor:
            return False, "请先建立数据库链接"
        else:
            return True, "Connected!"

    def openconnection(self, dbpath: str):
        if dbpath.strip() == "":
            return
        self.cx = sqlite3.connect(f'./database/{dbpath}')
        self.cursor = self.cx.cursor()

    def createtable(self, tablename: str, col_param: dict, fk: dict = None):
        if not self.testconnect()[0]:
            return self.testconnect()[1]
        if tablename.strip():
            return False, "请输入表名"
        elif len(col_param) == 0:
            return False
        sql = f'''create table if not exists {tablename}('''

        for key, value in col_param.items():
            params = ""
            for v in value:
                params += f'{v} '
            sql += f'''{key} {params},'''
        sql = sql[:-1]
        if fk:
            fksql = ''

            for fktbname, cols_map in fk.items():
                fksql += f'constraint {tablename}_{fktbname} '
                selftable = "FOREIGN KEY ("
                fktable = f'REFERENCES {fktbname} ('
                for selftablecol in cols_map.keys():
                    selftable += f'{selftablecol},'
                selftable = selftable[:-1] + ') '
                fksql += selftable
                for fktablecol in cols_map.values():
                    fktable += f'{fktablecol},'
                fktable = fktable[:-1] + ') '
                fksql += fktable
                sql += fksql

        sql += ')'

        cx = self.cx
        cursor = self.cursor
        try:
            cursor.execute(sql)
            cx.commit()
        except Exception as e:
            return False, str(e)
        return True

    def selecttable(self, tablename: str, columns: list = None, selection: dict = None, orderby: list = None,
                    sort: bool = True,
                    groupby: list = None):
        if tablename.strip() == '':
            print(f'请指定要查询的表名')
            return False, '请指定要查询的表名'
        sql = 'select '
        if columns:
            for column in columns:
                sql += f'{column}, '
            sql = sql[:-2] + f'from {tablename}'
        else:
            sql += f'* from {tablename}'

        if selection:
            sql += ' where '
            index = 0
            for condition, pre_connect in selection.items():
                sql_logic(sql=sql, condition=condition, pre_connect=pre_connect, index=index)
                index += 1
        if orderby:
            sql += ''
            for column in orderby:
                sql += f'{column},'
            sql = sql[:-1]
            if sort:
                sql += ' asc'
            else:
                sql += ' desc'
        cursor = self.cursor
        try:
            cursor.execute(sql)
            fetchresult = cursor.fetchall()
            result = []
            if not columns:
                return fetchresult
            for fetchone in fetchresult:
                one_dict = {}
                for i in range(len(columns)):
                    one_dict[columns[i]] = fetchone[i]
                result.append(one_dict)
        except Exception as e:
            return False, str(e)

        return True, result

    def closeconnection(self):
        if self.cursor:
            self.cursor.close()
        if self.cx:
            self.cx.close()


def sql_logic(sql: str, condition: str, pre_connect: str = None, index: int = 0):
    if pre_connect.strip() == '':
        pre_connect = None
    if index == 0 or not pre_connect:
        sql += f'{condition.strip()} '
    else:
        sql += f'{pre_connect.strip()} {condition.strip()} '
    return


dbhelper = DBHelper()
