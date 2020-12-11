import argparse
import pathlib
import random

from database.schema import MySQL
from evaluation.evaluate import Evaluator
from model import GA
from parse import Parser

def main(args):
    raw_sql_queries = [
        """select * from user where age > 10 and class <= 5""",
    ]

    raw_sql_query = random.choice(raw_sql_queries)
    predicates = Parser(raw_sql_query).parse()

    ga_results = []
    for p in predicates:
        print("Predicate : ", p)
        ga_results.append(GA(args, raw_sql_query, p).evolve())

    print('GA results:', ga_results)
    sql = MySQL().create(args.sql_file).read_schema()
    Evaluator(sql).insert_data(ga_results).read_test_queries(args.test_sql_file)


if __name__ == '__main__':
    HOME_DIR = pathlib.Path().absolute()

    parser = argparse.ArgumentParser('SMOG')

    parser.add_argument('--sql_file', default=f'{HOME_DIR}/database/sample_schema.sql', type=str, help='sql script file')
    parser.add_argument('--test_sql_file', default=f'{HOME_DIR}/evaluation/test_queries.sql', type=str, help='test queries from sqlfpc')

    parser.add_argument('--population_size', default=40, type=int, help='population size')
    parser.add_argument('--cross_pb', default=0.5, type=float, help='crossover probability')
    parser.add_argument('--mutation_pb', default=0.2, type=float, help='mutation probability')
    parser.add_argument('--generations', default=1000, type=int, help='generations')

    args, _ = parser.parse_known_args()
    main(args)
