import sqlparse


class Parser:
    def __init__(self, raw_query):
        self.query = raw_query
        self.format()

    def format(self):
        self.format = sqlparse.format(self.query, reindent=True, keyword_case='upper')

        raw_list = self.format.split('\n')
        format_list = []
        for r in raw_list:
            format_list.append({
                'indent_count': 0,
                'sql': r,
            })


def parse(self):

if __name__ == '__main__':
    Parser("""select * from foo where a > 10 and b < 15""")
