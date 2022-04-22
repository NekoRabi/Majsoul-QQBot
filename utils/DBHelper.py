import sqlite3
'''
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


class DBHelper():

    def __init__(self,dbpath:str):
        if dbpath.strip() == "":
            return
        self.cx = sqlite3.connect(f'./database/{dbpath}')
        self.cursor = self.cx.cursor()

    def createtable(self,tablename:str,col_param:dict,fk:dict=None):
        if tablename.strip():
            raise ""
            return False
        elif len(col_param) == 0:
            return False
        sql = f'''create table if not exists {tablename}('''

        for key,value in col_param.items():
            params = ""
            for v in value:
                params += f'{v} '
            sql += f'''{key} {params},'''
        sql = sql[:-1]
        if fk:
            fksql = ''

            for fktbname,cols_map in fk.items():
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

        cx=self.cx
        cursor = self.cursor
        cursor.execute(sql)
        cx.commit()

        return True

    def closeconnection(self):
        self.cursor.close()
        self.cx.close()