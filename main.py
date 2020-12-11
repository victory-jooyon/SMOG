import argparse
import random

from model import GA
from parse import Parser

def main(args):
    raw_sql_queries = [
        """select * from foo where a > 10 and b < 15""",
        """select * from user where age > 10 and class = 5""",
        # """select a from b where c < d + e""",
        # """select name, is_group from tabWarehouse where tabWarehouse.company = '_Test Company' order by tabWarehouse.modified desc""",
    ]

    raw_sql_query = random.choice(raw_sql_queries)
    predicates = Parser(raw_sql_query).parse()
    for p in predicates:
        print("Predicate : ", p)
        GA(args, raw_sql_query, p).evolve()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('SMOG')
    parser.add_argument('--population_size', default=40, type=int, help='population size')
    parser.add_argument('--cross_pb', default=0.5, type=float, help='crossover probability')
    parser.add_argument('--mutation_pb', default=0.2, type=float, help='mutation probability')
    parser.add_argument('--generations', default=1000, type=int, help='generations')

    args, _ = parser.parse_known_args()
    main(args)
