# pylint: disable=C

from Trainer import Trainer
from Battle import BattleSim
from Pokemon import Pokemon
from Utils import pokeDict

import random

class PokeGA(object):
    def __init__(self, listOfOpposingTrainers=[]):
        self.poke_mutation_rate = 0.005
        self.move_mutation_rate = 0.01
        self.crossover_rate = 0.6
        self.points_of_crossover = 1
        self.population_size = 20
        self.epoch_limit = 10000
        self.draw_graph = False
        self.current_generation = 0
        self.list_of_opposing_trainers = listOfOpposingTrainers
        self.convergence_array = []

        self.chromosomes = []

        self.parseConfig()

        for _ in range(6):
            self.convergence_array.append(False)


    def parseConfig(self):
        config = open("config.txt", "r")
        for line in config:
            lineSpl = line.split()
            exec("self." + lineSpl[0] + lineSpl[1])

    def generateStartingPopulation(self):
        for _ in range(self.population_size):
            self.chromosomes.append(Trainer(manual=False))

    def calculateAndAssignFitness(self):
        for trainer in self.chromosomes:
            for enemyTrainer in self.list_of_opposing_trainers:
                trainer.resetPokemon()
                enemyTrainer.resetPokemon()
                sim = BattleSim(trainer, enemyTrainer)
                trainerHPPercentage, enemyHPPercentage = sim.run_battle()
                trainer.fitness = trainerHPPercentage - enemyHPPercentage

    def compareFitnesses(self, cand_one, cand_two):
        chosen_parent = None
        if cand_one.fitness > cand_two.fitness:
            chosen_parent = cand_one
        else:
            chosen_parent = cand_two
        return chosen_parent

    def getMatingCandidatesAndReturnChoice(self):
        first_candidate = random.choice(self.chromosomes)
        self.chromosomes.remove(first_candidate)
        second_candidate = random.choice(self.chromosomes)
        self.chromosomes.remove(second_candidate)
        chosen_parent = self.compareFitnesses(first_candidate, second_candidate)
        self.chromosomes.append(first_candidate)
        self.chromosomes.append(second_candidate)
        return chosen_parent

    def mateParents(self, parent_one, parent_two):
        doCrossover = random.random() < self.crossover_rate
        if doCrossover:
            crossoverPoint = random.randrange(0, 6)
            return self.performCrossover(crossoverPoint, parent_one, parent_two)
        else:
            return parent_one, parent_two

    def performCrossover(self, crossoverPoint, parent_one, parent_two):
        offspring_one_pokemon = parent_one.pokemon[:crossoverPoint] + parent_two.pokemon[crossoverPoint:]
        offspring_two_pokemon = parent_two.pokemon[:crossoverPoint] + parent_one.pokemon[crossoverPoint:]

        parent_one.pokemon = offspring_one_pokemon
        parent_two.pokemon = offspring_two_pokemon

        return parent_one, parent_two

    def performTournamentAndMating(self):
        next_generation = []
        while len(next_generation) < self.population_size:
            parent_one = self.getMatingCandidatesAndReturnChoice()
            parent_two = self.getMatingCandidatesAndReturnChoice()

            offspring_one, offspring_two = self.mateParents(parent_one, parent_two)

            offspring_one.resetPokemon()
            offspring_two.resetPokemon()

            offspring_one.tryMutation(self.move_mutation_rate, self.poke_mutation_rate)
            offspring_two.tryMutation(self.move_mutation_rate, self.poke_mutation_rate)

            next_generation.append(offspring_one)
            next_generation.append(offspring_two)
        self.current_generation += 1
        self.chromosomes = next_generation

    def checkForConvergence(self):
        for geneIdx in range(len(self.convergence_array)):
            poke_ids = []
            for trainer in self.chromosomes:
                poke_ids.append(trainer.pokemon[geneIdx].id)
            poke_ids.sort()
            self.convergence_array[geneIdx] = poke_ids.count(poke_ids[9]) / self.population_size >= 0.92
        if self.convergence_array.count(True) == 6:
            return True
        else:
            return False

    def getFittest(self):
        fitList = []
        for chrom in self.chromosomes:
            fitList.append((chrom.fitness, chrom))
        maxTup = max(fitList,key=lambda item:item[0])
        return maxTup[1]

    def runAlgorithm(self):
        self.generateStartingPopulation()
        while self.current_generation < self.epoch_limit and not self.checkForConvergence():
            self.calculateAndAssignFitness()
            self.performTournamentAndMating()

        fittest = self.getFittest()
        fittest.printTeam()
        print(fittest.fitness)

team_config = ["385", "442", "382", "202", "150", "483"]

opposing_team_list = []
uber_team = []
for poke_id in team_config:
    uber_team.append(Pokemon(poke_id, pokeDict[poke_id]["name"], pokeDict[poke_id]["types"], pokeDict[poke_id]["stats"], pokeDict[poke_id]["moves"]))

opposing_team_list.append(Trainer(uber_team, manual=False))

pg = PokeGA(opposing_team_list)
pg.runAlgorithm()