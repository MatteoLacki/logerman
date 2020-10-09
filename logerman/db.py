from datetime import datetime
from pathlib import Path
import sqlite3
from collections import namedtuple

LOG = namedtuple('log', 'date ip project_id group process_name key value')


class DB(object):
    def __init__(self, path):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, 
                               exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.create_logs_if_aint_there()

    def iter_logs(self):
        with self.conn as cur:
            for log in cur.execute("SELECT * FROM 'logs'"):
                yield LOG(*log)

    def tables(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        with self.conn as cur:
            return {n[0] for n in cur.execute(sql)}

    def table_exist(self, name):
        return name in self.tables() 

    def create_logs_if_aint_there(self):
        sql = \
        """CREATE TABLE IF NOT EXISTS 'logs' (
            'insert_date' TIMESTAMP,
            'ip' TEXT,
            'project_id' INTEGER,
            'group' TEXT,
            'process_name' TEXT,
            'data_key' TEXT NOT NULL,
            'data_value' TEXT
        );"""
        with self.conn as cur:
            cur.execute(sql)

    def log(self, ip, project_id, group, process_name, data_key, data_value):
        with self.conn as cur:
            sql = """INSERT INTO 'logs'
            ('insert_date','ip','project_id','group','process_name','data_key','data_value')
            VALUES (?,?,?,?,?,?,?)"""
            cur.execute(sql, (datetime.now(),
                              ip,
                              project_id,
                              group,
                              process_name,
                              data_key,
                              data_value))

    def get_free_project_id(self):
        with self.conn as cur:
            # sql = "SELECT MAX(project_id) FROM 'logs'"
            sql = "SELECT project_id FROM 'logs' WHERE oid = (SELECT max(oid) FROM 'logs')"
            try:
                rows = cur.execute(sql).fetchall()
                project_id = rows[0][0] 
                return project_id + 1
            except IndexError:
                return 0

    def drop_logs(self):
        with self.conn as cur:
            cur.execute(("DROP TABLE IF EXISTS 'logs'"))

    def __del__(self):
        self.conn.close()