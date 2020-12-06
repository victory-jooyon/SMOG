import sqlparse
from sqlparse import sql, tokens as T
from sqlparse.tokens import Keyword, DML

class Parser:
    def __init__(self, raw_query):
        self.query = raw_query
        self.format()
        self.parsePredicates()

    def format(self):
        self.format = sqlparse.format(self.query, reindent=True, keyword_case='upper', indent_width="1")

        raw_list = self.format.split('\n')
        format_list = []
        for r in raw_list:
            format_list.append({
                'indent_count': 0,
                'sql': r,
            })

        print(self.format)
        # for item in self.format.split(' '):
        #     print(item)

        tokens = sqlparse.parse(self.query)[0].tokens

        # for item in format_list:
        #     stmt = item['sql']
        #     i = 0
        #     while(stmt[i] == ' '):
        #         item['indent_count'] += 1
        #         i += 1

        # print(format_list)


    def parsePredicates(self):
        parsed = sqlparse.parse(self.query)
        stmt = parsed[0]
        from_seen = False
        select_seen = False
        where_seen = False
        groupby_seen = False
        orderby_seen = False
        print(parsed)
        print(stmt.tokens)

        for token in stmt.tokens:
            if select_seen:
                if isinstance(token, sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        print("{} {}\n".format("Attr = ", identifier) )
                elif isinstance(token, sql.Identifier):
                    print("{} {}\n".format("Attr = ", token))
                elif token.ttype is T.Wildcard:
                    print("{} {}\n".format("Attr = ", token))
            if from_seen:
                if isinstance(token, sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        print("{} {}\n".format("TAB = ", identifier) )
                elif isinstance(token, sql.Identifier):
                    print("{} {}\n".format("TAB = ", token))
            
            if isinstance(token, sql.Where):
                select_seen = False
                from_seen = False
                where_seen = True
                for where_tokens in token:
                    if isinstance(where_tokens, sql.Comparison):
                        print("{} {}\n".format("Comparaison = ", where_tokens))
                    elif isinstance(where_tokens, sql.Parenthesis):
                        print("{} {}\n".format("Parenthesis = ", where_tokens))
                    # tables.append(token)
            if token.ttype is T.Keyword and token.value.upper() == "FROM":
                select_seen = False
                from_seen = True
                where_seen = False
            if token.ttype is DML and token.value.upper() == "SELECT":
                select_seen = True
                from_seen = False
                where_seen = False



if __name__ == '__main__':
    Parser("""select * from foo where a > 10 and b < 15""")

    Parser("""select a from b where c < d + e""")

    Parser("""select name, is_group from 'tabWarehouse' where 'tabWarehouse'.company = '_Test Company' order by 'tabWarehouse'.'modified' desc""")