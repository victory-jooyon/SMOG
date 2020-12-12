# SMOG

SMOG is a SQL test data generator using Multi Objective Genetic algorithm.

SMOG includes the following features:

  * Genetic algorithm using [DEAP](https://github.com/DEAP/deap)
  
## Documentation

See the [DEAP User's Guide](http://deap.readthedocs.org/) for DEAP documentation.

We just provide an installation guide for SMOG.

## Installation
Our program based on Python 3.7.5, Deap 1.3.1. along with some parsing related libraries.

```bash
pip install -r requirements.txt
```

If you wish to run SMOG, run the main file.

```bash
python main.py
```
is enough, but to customize SMOG as you wish, use arguments.
```bash
python main.py --sql_file {your sql script file} --test_sql_file {your test queries from SQLFpc} \
--population_size 100 --cross_pb 0.7 --mutation_pb 0.1 --generations 10000

```

- Sample for sql script file is shown [here](https://github.com/victory-jooyon/SMOG/blob/main/database/sample_schema.sql).
- Sample for test sql queries is shown [here](https://github.com/victory-jooyon/SMOG/blob/main/evaluation/test_queries.sql).
- Test sql queries can be made from [SQLFpc](https://in2test.lsi.uniovi.es/sqlfpc/SQLFpcWeb/generate/).
