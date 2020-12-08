import math
import operator
import random

from deap import base, creator, tools
from moz_sql_parser import parse as moz_parse

from parse import Parser


class GA:
    def __init__(self, args, query):
        self.query = query
        self.parse()

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


    def parse(self):
        self.parsed_query = Parser(self.query).parse()

        comparisons = []
        for comp in self.parsed_query['comparisons']:
            if '<' in comp:
                comparisons.append(['lt', comp.split('<')[0], comp.split('<')[1]])
                comparisons.append(['ge', comp.split('<')[0], comp.split('<')[1]])
            if '>' in comp:
                comparisons.append(['gt', comp.split('>')[0], comp.split('>')[1]])
                comparisons.append(['le', comp.split('>')[0], comp.split('>')[1]])

        self.comparisons = comparisons

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
        # 조건에 따라 구해야하는 총 해의 갯수, 이 예시의 경우에는 x,y,z,w니까 4개

        # TODO: 마지막 Parameter: 해의 개수 구하는 방법 수정
        self.toolbox.register("individual", tools.initRepeat, creator.Individual,
                              self.toolbox.attr_bool, len(self.parsed_query['comparisons']) * 2)

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
        print("Start of evolution")

        # Evaluate the entire population
        fitnesses = list(map(self.toolbox.evaluate, self.population))
        for ind, fit in zip(self.population, fitnesses):
            # ind = individual
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(self.population))

        # Extracting all the fitnesses of
        fits = [ind.fitness.values[0] for ind in self.population]

        # Variable keeping track of the number of generations
        g = 0

        # Begin the evolution
        # max fitness에 도달할 때까지(=염색체 하나가 모두 최적해를 가지는데에 성공하면 스탑) or 1000세대까지 반복
        while max(fits) < 4 and g < 1000:
            # A new generation
            g = g + 1
            print("-- Generation %i --" % g)

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

            print("  Evaluated %i individuals" % len(invalid_ind))

            # The population is entirely replaced by the offspring
            self.population[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in self.population]

            length = len(self.population)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean ** 2) ** 0.5

            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)

        print("-- End of (successful) evolution --")

        best_ind = tools.selBest(self.population, 1)[0]

        # Best Solution
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        print("RESULT : (%s, %s) (%s, %s) (%s, %s) (%s, %s)" % (
            best_ind[0], best_ind[2], best_ind[0], best_ind[3], best_ind[1], best_ind[2], best_ind[1], best_ind[3]))

    def evaluate_fittest(self, population):
        # 해당 최적해의 묶음(=염색체 하나)의 fitness를 계산하여 리턴한다
        def run_op(op_list):
            if op_list[0] == 'lt':
                return operator.lt(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'gt':
                return operator.gt(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'le':
                return operator.le(int(op_list[1]), int(op_list[2]))
            elif op_list[0] == 'ge':
                return operator.ge(int(op_list[1]), int(op_list[2]))

        def substitute(comparisons, num):
            num_comparisons = []
            for t in comparisons:
                temp = t.copy()
                temp[1] = num
                num_comparisons.append(temp)
            return num_comparisons

        print(population)
        fitness = 0
        for i in range(0, len(population)):
            x = population[i]
            p_dict = substitute(self.comparisons, x)
            print('=====fittest:', self.comparisons, x, p_dict)
            if run_op(p_dict[i]):
                fitness += 1
            else:
                if int(p_dict[i][2]) == p_dict[i][1]:
                    fitness += 1 / (math.sqrt(2))
                else:
                    fitness += 1 / (math.sqrt((int(p_dict[i][2]) - x) ** 2 + (int(p_dict[i][2]) - x) ** 2))
            print(fitness)

        return fitness,
