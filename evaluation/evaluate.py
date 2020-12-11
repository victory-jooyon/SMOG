import random

import pymysql


class Evaluator:
    def __init__(self, sql):
        self.sql = sql
        smog_db = pymysql.connect(
            user='root',
            passwd='',
            host='127.0.0.1',
            db='smog',
            charset='utf8'
        )

        self.cursor = smog_db.cursor(pymysql.cursors.DictCursor)

    def insert_data(self, ga_results):
        fields = list(self.sql.schema.keys())

        inserting_queries = []
        inserting_values = []
        for ga_result in ga_results:
            inserting_data = {}
            for f in fields:
                inserting_data[f] = ga_result.get(f) or random.randrange(1,1000)

            inserting_query =  f"""insert into {self.sql.table_name}("""
            for k in inserting_data.keys():
                inserting_query += f'{k}, '
            inserting_query = inserting_query[:-2]
            inserting_query += ') values('

            for v in inserting_data.values():
                inserting_query += '%s, '
            inserting_query = inserting_query[:-2]
            inserting_query += ')'

            inserting_queries.append(inserting_query)
            inserting_values.append(tuple(inserting_data.values()))

        print('======= Inserting data:', inserting_query)
        print(inserting_values)
        self.cursor.executemany(inserting_query, inserting_values)

        return self

    def read_test_queries(self, test_sql_file):
        f = open(test_sql_file, 'r')
        lines = f.readlines()
        correct = 0
        for line in lines:
            print(line)
            self.cursor.execute(line)
            results = self.cursor.fetchall()

            if results:
                correct += 1

        print(f'=========== Got correct with {correct} out of {len(lines)}')

        f.close()
