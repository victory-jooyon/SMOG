import sqlparse
from sqlparse import sql, tokens as T
from sqlparse.tokens import DML
from moz_sql_parser import parse as moz_parse
import json


class Parser:
    def __init__(self, raw_query):
        self.query = raw_query
        # self.format()
        result = self.parse()
        print(result)

    def old_format(self):
        self.format = sqlparse.format(self.query, reindent=True, keyword_case='upper', indent_width="1")

        raw_list = self.format.split('\n')
        format_list = []
        for r in raw_list:
            format_list.append({
                'indent_count': 0,
                'sql': r,
            })

        print("--------------------------------------------------------------------------------------")
        print("                                        Query               ")
        print("--------------------------------------------------------------------------------------")
        print(self.query)
        print("--------------------------------------------------------------------------------------")
        print("                                      Parsed Data              ")
        print("--------------------------------------------------------------------------------------")
        print(json.dumps(parse(self.query)))
        print("--------------------------------------------------------------------------------------")

        print("")
        tokens = sqlparse.parse(self.query)[0].tokens


    def format(self):
        parsed = sqlparse.parse(self.query)
        stmt = parsed[0]
        from_seen = False
        select_seen = False
        where_seen = False
        # print(parsed)
        # print(stmt.tokens)
        attributes = []
        tables = []
        comparisons = []
        parenthesis = []
        query = {}

        for token in stmt.tokens:
            if select_seen:
                if isinstance(token, sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        attributes.append(identifier.value)
                        # print("{} {}\n".format("Attr = ", identifier) )
                elif isinstance(token, sql.Identifier):
                    attributes.append(token.value)
                    # print("{} {}\n".format("Attr = ", token))
                elif token.ttype is T.Wildcard:
                    attributes.append(token.value)
                    # print("{} {}\n".format("Attr = ", token))
            if from_seen:
                if isinstance(token, sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        tables.append(identifier)
                        # print("{} {}\n".format("TAB = ", identifier) )
                elif isinstance(token, sql.Identifier):
                    tables.append(token.value)
                    # print("{} {}\n".format("TAB = ", token))

            if isinstance(token, sql.Where):
                select_seen = False
                from_seen = False
                where_seen = True
                for where_tokens in token:
                    if isinstance(where_tokens, sql.Comparison):
                        comparisons.append(where_tokens.value)
                        # print("{} {}\n".format("Comparaison = ", where_tokens))
                    elif isinstance(where_tokens, sql.Parenthesis):
                        parenthesis.append(where_tokens.value)
                        # print("{} {}\n".format("Parenthesis = ", where_tokens))
                    # tables.append(token)
            if token.ttype is T.Keyword and token.value.upper() == "FROM":
                select_seen = False
                from_seen = True
                where_seen = False
            if token.ttype is DML and token.value.upper() == "SELECT":
                select_seen = True
                from_seen = False
                where_seen = False

        query["attributes"] = attributes
        query["tables"] = tables
        query["comparisons"] = comparisons
        query["parenthesis"] = parenthesis

        print(self.query)
        print (query)
        print(" ")

        return query

    def parse(self):
        data = (moz_parse(self.query)["where"])
        cond_list = ["lte", "gte", "gt", "lt", "eq", "neq"]
        conditions = self.dataToCondtions(data, [], cond_list)
        return self.parsedToData(conditions)

    def dataToCondtions(self, data, conditions, cond_list):
        for key in data:
            if key == "and" or key == "or":
                for i in range(len(data[key])):
                    first_key = list(data[key][i].keys())[0] 
                    self.dataToCondtions(data[key][i], conditions, cond_list)
            else:
                temp_list = []
                temp_list.append(key)
                if key in cond_list:
                    temp_list.extend(data[key])
                    conditions.append(temp_list)
                
        return conditions

    def parsedToData(self, conditions):
        result = []
        for item in conditions:
            newList = conditions.copy()
            newList.remove(item)
            tempList = []
            tempList.append(item)
            tempList.extend(newList)
            result.append(tempList)
            newItem = item.copy()
            if newItem[0] == "lte":
                newItem[0] = "gt"
            elif newItem[0] == "gt":
                newItem[0] = "lte"
            elif newItem[0] == "gte":
                newItem[0] = "lt"
            elif newItem[0] == "lt":
                newItem[0] = "gte"
            elif newItem[0] == "eq":
                newItem[0] = "neq"
            elif newItem[0] == "neq":
                newItem[0] = "eq"
                
            tempList = []
            tempList.append(newItem)
            tempList.extend(newList)
            result.append(tempList)

        return result

if __name__ == '__main__':
    Parser("""select * from foo where a > 10 """)

    Parser("""select a from b where c < 17""")

    # Parser("""select name, is_group from tabWarehouse where tabWarehouse.company = '_Test Company' order by tabWarehouse.modified desc""")