import os

import pymysql


class MySQL:
    def __init__(self):
        self.db_user = os.environ.get('SMOG_USER', 'root')
        self.db_passwd = os.environ.get('SMOG_PASSWD')

    def create(self, sql_file):
        if self.db_passwd is None:
            os.system(f'mysql -u{self.db_user} < {sql_file}')

        return self

    def read_schema(self):
        smog_db = pymysql.connect(
            user='root',
            passwd='',
            host='127.0.0.1',
            db='smog',
            charset='utf8'
        )

        self.cursor = smog_db.cursor(pymysql.cursors.DictCursor)
        self.cursor.execute('SHOW tables;')
        self.table_name = self.cursor.fetchone()['Tables_in_smog']
        self.cursor.execute(f'DESCRIBE {self.table_name}')
        fields = self.cursor.fetchall()

        fields_dict = {}
        for field in fields:
            fields_dict[field['Field']] = {
                'type': field['Type'],
                'null': not (field['Null'] == 'NO'),
            }

        print('DB schema:', fields_dict)
        self.schema = fields_dict
        return self
