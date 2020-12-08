import argparse
import random

from model import GA
from parse import Parser


def main(args):
    raw_sql_queries = [
        """select * from foo where a > 10 and b < 15""",
        # """select a from b where c < d + e""",
        # """select name, is_group from tabWarehouse where tabWarehouse.company = '_Test Company' order by tabWarehouse.modified desc""",
    ]

    raw_sql_query = random.choice(raw_sql_queries)
    GA(args, raw_sql_query).evolve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('SMOG')
    parser.add_argument('--population_size', default=5, type=int, help='population size')
    parser.add_argument('--cross_pb', default=0.5, type=float, help='crossover probability')
    parser.add_argument('--mutation_pb', default=0.2, type=float, help='mutation probability')
    parser.add_argument('--generations', default=1000, type=int, help='generations')

    args, _ = parser.parse_known_args()
    main(args)
