import yaml
import os
from pprint import pprint
from app import APP_ROOT, UPLOAD_FOLDER
from random import *

class Simulation():

	species = {}
	habitats = {}
	months_in_year = 12
	years = 0
	months = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec')
	seasons = {'jan' : 'winter', 'feb' : 'winter', 'mar' : 'spring', 'apr' : 'spring', 'may' : 'spring', 'jun' : 'summer', 'jul': 'summer', 'aug' : 'summer', 'sept' : 'fall', 'oct' : 'fall', 'nov' : 'fall', 'dec' : 'winter'}
	YAML_OUTPUT = {}

	def __init__(self, file):
		file_name = os.path.join(UPLOAD_FOLDER, file)
		with open(file_name, 'r') as stream:
			try:
				simulation = yaml.load(stream)
				self.years = simulation['years']
				self.species = simulation['species']
				self.habitats = simulation['habitats']
			except yaml.YAMLError as e:
				print(e)

	def get_season(self, month):
		return self.seasons[month]

	def process_all_habitat_simulations(self):
		for animal in self.species:
			self.YAML_OUTPUT[animal['name']] = {}
			for habitat in self.habitats:
				self.YAML_OUTPUT[animal['name']][habitat['name']] = self.process_habitat_simulation(animal,habitat)
		pprint(self.YAML_OUTPUT)

	def process_habitat_simulation(self,animal,habitat):

		average_population = 0
		max_population = 0
		mortality_rate = 0
		cause_of_death = {}
		male_inhabitants = {0 : {'age' : 0}}
		female_inhabitants = {0 : {'age' : 0}}
		off_spring_rate = animal['attributes']['off_spring_rate']
		off_spring_min = animal['attributes']['off_spring_min']
		permutation = 0

		for year in range(self.years):
			for month in self.months:
				female_inhabitants, male_inhabitants = self.grow_inhabitants(male_inhabitants,female_inhabitants)
				female_inhabitants, male_inhabitants = self.breed_inhabitants(male_inhabitants,female_inhabitants,off_spring_rate,off_spring_min,permutation)
				self.kill_inhabitants(male_inhabitants,female_inhabitants,permutation)

				permutation += 1

		pprint(animal['name'])
		pprint(female_inhabitants)

		return {
			"Average_Population" : average_population, 
			"Max_Population" : max_population, 
			"Mortality_Rate" : mortality_rate, 
			"Cause_of_Death" : cause_of_death
		}


	def grow_inhabitants(self,male_inhabitants,female_inhabitants):
		#grow both men and women by one month
		for male_inhabitant in male_inhabitants:
			male_inhabitants[male_inhabitant]['age'] += 1
		for female_inhabitant in female_inhabitants:
			female_inhabitants[female_inhabitant]['age'] += 1
		return female_inhabitants, male_inhabitants

	def breed_inhabitants(self,male_inhabitants,female_inhabitants,off_spring_rate,off_spring_min,permutation):

		#create new lists so we can add while in loop
		new_female_inhabitants = {}
		new_male_inhabitants = {}
		new_births = {}
		i = 0

		#if is breeding interval
		if permutation % off_spring_rate == 0:

			#iterate through all females check if minimum age has been reached
			for female_inhabitant in female_inhabitants:
				if female_inhabitants[female_inhabitant]['age'] > off_spring_min:
					new_births[i] = i

			#create new babies, if no new births loop wont iter once
			for new_birth in new_births:
				if random() < .5:
					new_female_inhabitants = {len(female_inhabitants) + new_birth : {'age' : 0}}
				else:
					new_male_inhabitants = {len(female_inhabitants) + new_birth : {'age' : 0}}

			#return merged dictionaries
			return self.merge_dicts(female_inhabitants, new_female_inhabitants), self.merge_dicts(male_inhabitants, new_male_inhabitants)
		else:
			#return original dictionaries
			return female_inhabitants, male_inhabitants

	def merge_dicts(self,x,y):
	    z = x.copy()
	    z.update(y)
	    return z


	def kill_inhabitants(self,male_inhabitants,female_inhabitants,permutation):
		return True