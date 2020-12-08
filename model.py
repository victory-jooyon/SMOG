#!/usr/bin/env python
# coding: utf-8

import random
import math
import numpy
import parse as p
import operator

from deap import base
from deap import creator
from deap import tools

query = p.Parser("""select * from name_table where a>15 and b<10""")
predicates = query.parsePredicates()
new_dict = []
for comp in predicates['comparisons']:
    if '<' in comp:
        new_dict.append(['lt', comp.split('<')[0], comp.split('<')[1]])
        new_dict.append(['ge', comp.split('<')[0], comp.split('<')[1]])    
    if '>' in comp:
        new_dict.append(['gt', comp.split('>')[0], comp.split('>')[1]])
        new_dict.append(['le', comp.split('>')[0], comp.split('>')[1]])

        
print(new_dict)
# print(predicates['comparisons'][0])
# print(len(predicates['comparisons'])*2)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
#                      define 'attr_bool' to be an attribute ('gene')
#                      which corresponds to integers sampled uniformly
#                      from the range [0,1] (i.e. 0 or 1 with equal
#                      probability)
# 랜덤하게 뽑는 숫자의 범위를 지정한다
toolbox.register("attr_bool", random.randint, 0, 30)

# Structure initializers
#                         define 'individual' to be an individual
#                         consisting of 100 'attr_bool' elements ('genes')
# 조건에 따라 구해야하는 총 해의 갯수, 이 예시의 경우에는 x,y,z,w니까 4개
toolbox.register("individual", tools.initRepeat, creator.Individual,
    toolbox.attr_bool, len(predicates['comparisons'])*2)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# the goal ('fitness') function to be maximized
# 0~1까지의 fitness를 가진다
# i가 predicate을 만족하는 경우 fitness = 1
# i가 predicate을 만족하지 못하는 경우 distance의 normFactor의 역수를 fitness로 가진다
# evalOneMax는 해당 최적해의 묶음(=염색체 하나)의 fitness를 계산하여 리턴한다
# p dict는 predicate을 sql에서 파싱해서 만든다

def run_op(op_list):
    if op_list[0] == 'lt':
        return operator.lt(int(op_list[1]), int(op_list[2]))
    elif op_list[0] == 'gt':
        return operator.gt(int(op_list[1]), int(op_list[2]))
    elif op_list[0] == 'le':
        return operator.le(int(op_list[1]), int(op_list[2]))
    elif op_list[0] == 'ge':
        return operator.ge(int(op_list[1]), int(op_list[2]))
    
def rep(new_dict, x):
    ans_dict = []
    for t in new_dict:
        temp = t.copy()
        temp[1] = x
        ans_dict.append(temp)
    return ans_dict
        
print(new_dict)

def evalOneMax(individual):
    print(individual)
    fitness = 0
    for i in range(0, len(individual)):
        x = individual[i]
        p_dict = rep(new_dict, x)
        if run_op(p_dict[i]):
            fitness += 1
        else:
            if int(p_dict[i][2]) == p_dict[i][1]:
                fitness += 1/(math.sqrt(2))
            else:
                fitness += 1/(math.sqrt((int(p_dict[i][2])-x)**2 + (int(p_dict[i][2])-x)**2))
        print(fitness)

    return fitness,

#----------
# Operator registration
#----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)

# register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of three individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selSPEA2)

#----------

def main():
    random.seed()

    # create an initial population of 10 individuals (where
    # each individual is a list of integers)
    # population 사이즈를 정한다
    pop = toolbox.population(n=5)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    # 크로스오버, 뮤테이션 변수를 정한다
    CXPB, MUTPB = 0.5, 0.2

    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    print("  Evaluated %i individuals" % len(pop))

    # Extracting all the fitnesses of
    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations
    g = 0

    # Begin the evolution
    # max fitness에 도달할 때까지(=염색체 하나가 모두 최적해를 가지는데에 성공하면 스탑) or 1000세대까지 반복
    while max(fits) < 4 and g < 1000:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    # Best Solution
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    print("RESULT : (%s, %s) (%s, %s) (%s, %s) (%s, %s)" % (best_ind[0], best_ind[2], best_ind[0], best_ind[3], best_ind[1], best_ind[2], best_ind[1], best_ind[3]))

if __name__ == "__main__":
    main()
