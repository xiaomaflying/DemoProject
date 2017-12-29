import mysql.connector
from Source.lib.config import DB_CONFIG

class DBConnector(object):
    def __init__(self, db_conf):
        self.db_conf = db_conf
        self.conn = self._connect()

    def _connect(self):
        conf = self.db_conf
        conn = mysql.connector.connect(
            user=conf['user'],
            password=conf['password'],
            host=conf['host'],
            port=conf['port'],
            database=conf['database'])
        return conn

    def execute_insert_sql(self, ip, user, email, info):
        cur = self.conn.cursor()
        cur.execute('insert into sysinfo (ip, user, email, info) values (%s, %s, %s, %s)', [ip, user, email, info])
        self.conn.commit()
        cur.close()

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    connector = DBConnector(DB_CONFIG)
    connector.execute_insert_sql('127.0.0.1', 'maxinmin', 'firstbestma@126.com', 'xxxxxx')
    connector.close()