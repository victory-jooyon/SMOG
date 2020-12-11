import math
import operator
import random
import argparse
from deap import base, creator, tools
from moz_sql_parser import parse as moz_parse

from parse import Parser

class GA:
    def __init__(self, args, query, predicate):
        self.query = query
        self.comparisons = predicate # [['gt', 'a', 10], ['lt', 'b', 15]]
#         print(predicate)
        field = []
        result_form = {}
        for i in range(0, len(predicate)):
            if not isinstance(predicate[i][1], int):
                result_form[predicate[i][1]] = -1
            elif not isinstance(predicate[i][2], int):
                result_form[predicate[i][2]] = -1
#         print(result_form)
        self.result = result_form
#         print(self.result)
        random.seed()

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.register_toolbox()

        # create an initial population of n individuals (where each individual is a list of integers)
        # population 사이즈를 정한다
        self.population = self.toolbox.population(n=args.population_size)

        # CXPB  is the probability with which two individuals
        #       are crossed
        #
        # MUTPB is the probability for mutating an individual
        # 크로스오버, 뮤테이션 변수를 정한다
        self.CXPB = args.cross_pb
        self.MUTPB = args.mutation_pb
        self.generations = args.generations


#     def parse(self):
#         self.parsed_query = Parser(self.query).parse()
#         self.parsed_query = moz_parse(self.query)['where']
        
#         comparisons = []
#         for comp in self.parsed_query['comparisons']:
#             if '<' in comp:
#                 comparisons.append(['lt', comp.split('<')[0], comp.split('<')[1]])
#                 comparisons.append(['ge', comp.split('<')[0], comp.split('<')[1]])
#             if '>' in comp:
#                 comparisons.append(['gt', comp.split('>')[0], comp.split('>')[1]])
#                 comparisons.append(['le', comp.split('>')[0], comp.split('>')[1]])

#         self.comparisons = comparisons
#         self.comparisons = self.parsed_query

    def register_toolbox(self):
        # Attribute generator
        #                      define 'attr_bool' to be an attribute ('gene')
        #                      which corresponds to integers sampled uniformly
        #                      from the range [0,1] (i.e. 0 or 1 with equal
        #                      probability)
        # 랜덤하게 뽑는 숫자의 범위를 지정한다
        self.toolbox.register("attr_bool", random.randint, 0, 30)

        # Structure initializers
        #                         define 'individual' to be an individual
        #                         consisting of 100 'attr_bool' elements ('genes')
        # 조건에 따라 구해야하는 총 해의 갯수
        
        self.toolbox.register("individual", tools.initRepeat, creator.Individual,
                              self.toolbox.attr_bool, len(self.comparisons))

        # define the population to be a list of individuals
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # ----------
        # Operator registration
        # ----------
        # register the goal / fitness function
        self.toolbox.register("evaluate", self.evaluate_fittest)

        # register the crossover operator
        self.toolbox.register("mate", tools.cxTwoPoint)

        # register a mutation operator with a probability to
        # flip each attribute/gene of 0.05
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

        # operator for selecting individuals for breeding the next
        # generation: each individual of the current generation
        # is replaced by the 'fittest' (best) of three individuals
        # drawn randomly from the current generation.
        self.toolbox.register("select", tools.selSPEA2)

    def evolve(self):
#         print("Start of evolution")

        # Evaluate the entire population
        fitnesses = list(map(self.toolbox.evaluate, self.population))
        for ind, fit in zip(self.population, fitnesses):
            # ind = individual
            ind.fitness.values = fit

#         print("  Evaluated %i individuals" % len(self.population))

        # Extracting all the fitnesses of
        fits = [ind.fitness.values[0] for ind in self.population]

        # Variable keeping track of the number of generations
        g = 0

        # Begin the evolution
        # max fitness에 도달할 때까지(=염색체 하나가 모두 최적해를 가지는데에 성공하면 스탑) or 1000세대까지 반복
        while max(fits) < len(self.comparisons) and g < 1000:
            # A new generation
            g = g + 1
#             print("-- Generation %i --" % g)

            # Select the next generation individuals
            offspring = self.toolbox.select(self.population, len(self.population))
            # Clone the selected individuals
            offspring = list(map(self.toolbox.clone, offspring))

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):

                # cross two individuals with probability CXPB
                if random.random() < self.CXPB:
                    self.toolbox.mate(child1, child2)

                    # fitness values of the children
                    # must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:

                # mutate an individual with probability MUTPB
                if random.random() < self.MUTPB:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

#             print("  Evaluated %i individuals" % len(invalid_ind))

            # The population is entirely replaced by the offspring
            self.population[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in self.population]

            length = len(self.population)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean ** 2) ** 0.5

#             print("  Min %s" % min(fits))
#             print("  Max %s" % max(fits))
#             print("  Avg %s" % mean)
#             print("  Std %s" % std)

#         print("-- End of (successful) evolution --")

        best_ind = tools.selBest(self.population, 1)[0]

        # Best Solution
        print("Best individual & fitness is %s, %s " % (best_ind, best_ind.fitness.values))
        keys = list(self.result.keys())
        for i in range(0, len(keys)):
            self.result[keys[i]] = best_ind[i]
        print("======= RETURN DICT :",self.result," =======\n")
        return self.result
    
#         print("RESULT : (%s, %s) (%s, %s) (%s, %s) (%s, %s)" % (
#             best_ind[0], best_ind[2], best_ind[0], best_ind[3], best_ind[1], best_ind[2], best_ind[1], best_ind[3]))

    def evaluate_fittest(self, population):
        # 해당 최적해의 묶음(=염색체 하나)의 fitness를 계산하여 리턴한다
        def run_op(op_list):
            if op_list[0] == 'eq':
                return operator.eq(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'neq':
                return not operator.eq(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'lt':
                return operator.lt(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'gt':
                return operator.gt(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'lte':
                return operator.le(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'gte':
                return operator.ge(int(op_list[1]), int(op_list[2]))

        def substitute(comparisons, num):
            num_comparisons = []
            for c in comparisons:
                temp = c.copy()
                for i in range(1, len(temp)):
                    if not isinstance(temp[i], int):
                        temp[i] = num
                num_comparisons.append(temp)
            return num_comparisons

#         print(population)
        fitness = 0
        for i in range(0, len(population)):
            x = population[i]
            p_list = substitute(self.comparisons, x)
#             print('=====fittest:', self.comparisons, x, p_list)
            if run_op(p_list[i]):
                fitness += 1
            else:
                
                if (int(p_list[i][2]) == int(p_list[i][1])) and (p_list[i][0] != 'eq' or p_list[i][0] != 'neq'):
                    fitness += 1 / (math.sqrt(2))
                else:
                    fitness += 1 / (math.sqrt((int(p_list[i][2]) - x) ** 2 + (int(p_list[i][2]) - x) ** 2))
#             print(fitness)

        return fitness,
