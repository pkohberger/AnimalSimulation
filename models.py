import yaml
import os
from pprint import pprint
from app import APP_ROOT, UPLOAD_FOLDER
from random import *

class Simulation():

	years = 0
	species = {}
	habitats = {}
	months_in_year = 12
	simulation_permutations = 0
	YAML_OUTPUT = {}

	def __init__(self, file):
		file_name = os.path.join(UPLOAD_FOLDER, file)
		with open(file_name, 'r') as stream:
			try:
				simulation = yaml.load(stream)
				self.years = simulation['years']
				self.species = simulation['species']
				self.habitats = simulation['habitats']
				self.simulation_permutations = self.years * self.months_in_year
			except yaml.YAMLError as e:
				print(e)

	def process_all_habitat_simulations(self):
		for animal in self.species:
			self.YAML_OUTPUT[animal['name']] = {}
			for habitat in self.habitats:
				self.YAML_OUTPUT[animal['name']][habitat['name']] = self.process_habitat_simulation(animal,habitat)
		pprint(self.YAML_OUTPUT)

	def process_habitat_simulation(self,animal,habitat):

		max_population = 0
		mortality_rate = 0
		cause_of_death = {}
		male_inhabitants = 1
		female_inhabitants = 1
		pregnancy_term = 9

		for permutation in range(self.simulation_permutations):
			#birth rate really very simple, every nine months
			#50/50 chance of male birth or female birth
			if permutation % pregnancy_term == 0:
				if random() < .5:
					male_inhabitants += 1
				else:
					female_inhabitants += 1

		pprint(male_inhabitants)

		average_population = (male_inhabitants + female_inhabitants)/self.years

		return {
			"Average_Population_(Annual)" : male_inhabitants, 
			"Max_Population" : max_population, 
			"Mortality_Rate" : mortality_rate, 
			"Cause_of_Death" : cause_of_death
		}

	class Species():

		name = ""
		monthly_food_consumption = 0
	  	monthly_water_consumption = 0
	  	life_span = 0
	  	minimum_temperature = 0
	  	maximum_temperature = 0

	class Habitat():

		name = ""
		monthly_food = 0
	  	monthly_water = 0
	  	summer_temp = 0
	  	spring_temp = 0
	  	fall_temp = 0
	  	winter_temp = 0