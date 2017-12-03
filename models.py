import yaml
import os
from pprint import pprint
from app import APP_ROOT, UPLOAD_FOLDER, merge_dicts
from utils import Utils
from enum import Enum
from random import *

class Simulation(object):

	species = {}
	habitats = {}
	months_in_year = 12
	years = 0
	months = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec')
	seasons = {
		'jan' : 'winter', 'feb' : 'winter', 'mar' : 'spring', 'apr' : 'spring', 'may' : 'spring', 'jun' : 'summer',
		'jul': 'summer', 'aug' : 'summer', 'sept' : 'fall', 'oct' : 'fall', 'nov' : 'fall', 'dec' : 'winter'
	 }
	OUTPUT = {}
	DEBUG = False

	def __init__(self, file):
		file_name = os.path.join(UPLOAD_FOLDER, file)
		with open(file_name, 'r') as stream:
			try:
				simulation = yaml.load(stream)
				self.years = simulation['years']
				self.species = simulation['species']
				self.habitats = simulation['habitats']
				self.DEBUG = True
			except yaml.YAMLError as e:
				print(e)

	def get_season(self, month):
		return self.seasons[month]

	#wrapper so we only define this structure once
	#can later return custom object perhaps
	def get_inhabitants_structure(self,key):
		#age is in permutations or months
		#food_consumption and water_concumption keys
		#are based on permutation or month they are born in
		#so these may be arbitrary but will be in increments of 1
		return {
			key : {
				'age' : 0, 
				'food_consumption' : {},
				'water_consumption' : {}
			}
		}

	def process_all_habitat_simulations(self):
		for animal in self.species:
			self.OUTPUT[animal['name']] = {}
			for habitat in self.habitats:
				self.OUTPUT[animal['name']][habitat['name']] = self.process_habitat_simulation(animal,habitat)
		if self.DEBUG:
			pprint(self.OUTPUT)

	def process_habitat_simulation(self,animal,habitat):

		#general initialization of necessary variables
		average_population = 0
		max_population = 0
		mortality_rate = 0
		cause_of_death = {}
		#each habitat starts off with exactly one
		#male and one female
		male_inhabitants = self.get_inhabitants_structure(0)
		female_inhabitants = self.get_inhabitants_structure(0)
		permutation = 0

		#attempt to initialize species indicator variables
		try:
			animal_monthly_water_consumption = animal['attributes']['monthly_water_consumption']
			animal_monthly_food_consumption = animal['attributes']['monthly_food_consumption']
			life_span = animal['attributes']['life_span']
			minimum_temperature = animal['attributes']['minimum_temperature']
			maximum_temperature = animal['attributes']['maximum_temperature']
			off_spring_rate = animal['attributes']['off_spring_rate']
			off_spring_min = animal['attributes']['off_spring_min']
			off_spring_max = animal['attributes']['off_spring_max']
			habitat_monthly_food = habitat['monthly_food']
			habitat_monthly_water = habitat['monthly_water']
		except OSError as e:
			print(e)
			#return if missing info
			return False

		#lets run the actual simulation for this given habitat
		for year in range(self.years):
			for month in self.months:
				#i typically dont write methods with this many parameters
				#but for the sake of completing the task, here we go
				female_inhabitants, male_inhabitants = self.grow_inhabitants(
					male_inhabitants,female_inhabitants,permutation,animal_monthly_water_consumption,
					animal_monthly_food_consumption,habitat_monthly_food,habitat_monthly_water
				)
				female_inhabitants, male_inhabitants = self.breed_inhabitants(
					male_inhabitants,female_inhabitants,off_spring_rate,off_spring_min,off_spring_max,permutation
				)
				female_inhabitants, male_inhabitants = self.kill_inhabitants(
					male_inhabitants,female_inhabitants,permutation,animal_monthly_water_consumption,
					animal_monthly_food_consumption,life_span,minimum_temperature,maximum_temperature
				)

				#months count
				permutation += 1

		if self.DEBUG:
			pprint("-------------")
			pprint(animal['name'])
			pprint(habitat['name'])
			pprint('females:')
			pprint(female_inhabitants)
			pprint('males:')
			pprint(male_inhabitants)

		return {
			"Average_Population" : average_population, 
			"Max_Population" : max_population, 
			"Mortality_Rate" : mortality_rate, 
			"Cause_of_Death" : cause_of_death
		}


	def grow_inhabitants(
		self,male_inhabitants,female_inhabitants,permutation,animal_monthly_water_consumption,
		animal_monthly_food_consumption,habitat_monthly_food,habitat_monthly_water
	):
		female_inhabitants, male_inhabitants = self.age_inhabitants(male_inhabitants,female_inhabitants)

		#habitat elders will be given priority in food consumption
		female_inhabitants, male_inhabitants = self.feed_inhabitants(
			male_inhabitants,female_inhabitants,permutation,animal_monthly_food_consumption,habitat_monthly_food
		)

		#habitat elders will be given priority in water consumption
		female_inhabitants, male_inhabitants = self.water_inhabitants(
			male_inhabitants,female_inhabitants,permutation,animal_monthly_water_consumption,habitat_monthly_water
		)

		return female_inhabitants, male_inhabitants

	def age_inhabitants(self,male_inhabitants,female_inhabitants):
		#grow both men and women by one month
		#age is recorded as months or permutations
		for male_inhabitant in male_inhabitants:
			male_inhabitants[male_inhabitant]['age'] += 1
			#TODO: write method for food consumption
		for female_inhabitant in female_inhabitants:
			female_inhabitants[female_inhabitant]['age'] += 1
			#TODO: write method for food consumption
		return female_inhabitants, male_inhabitants

	def feed_inhabitants(self,male_inhabitants,female_inhabitants,permutation,animal_monthly_food_consumption,habitat_monthly_food):
		#data structures for reset of dicts
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		#roughly distribute food 50/50
		male_habitat_monthly_food = habitat_monthly_food/2
		male_consumption_total = 0
		for male_inhabitant in male_inhabitants:
			new_male_inhabitants[male_inhabitant] = male_inhabitants[male_inhabitant]
			#merge new data
			new_male_inhabitants[male_inhabitant]['food_consumption'] = merge_dicts(
				new_male_inhabitants[male_inhabitant]['food_consumption'],
				{
					#only consume food if its under alotted amount for habitat for that month
					permutation : animal_monthly_food_consumption if male_consumption_total <= (male_habitat_monthly_food - animal_monthly_food_consumption) else 0
				}
			)
			#add consumption to total
			male_consumption_total += animal_monthly_food_consumption

		#roughly distribute food 50/50
		female_habitat_monthly_food = habitat_monthly_food/2
		female_consumption_total = 0
		for female_inhabitant in female_inhabitants:
			new_female_inhabitants[female_inhabitant] = female_inhabitants[female_inhabitant]
			#merge new data
			new_female_inhabitants[female_inhabitant]['food_consumption'] = merge_dicts(
				new_female_inhabitants[female_inhabitant]['food_consumption'],
				{
					#only consume food if its under alotted amount for habitat for that month
					permutation : animal_monthly_food_consumption if female_consumption_total <= (female_habitat_monthly_food - animal_monthly_food_consumption) else 0
				}
			)
			#add consumption to total
			female_consumption_total += animal_monthly_food_consumption

		#return new dicts
		return female_inhabitants, male_inhabitants

	def water_inhabitants(self,male_inhabitants,female_inhabitants,permutation,animal_monthly_water_consumption,habitat_monthly_water):
		#data structures for reset of dicts
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		#roughly distribute water 50/50
		male_habitat_monthly_water = habitat_monthly_water/2
		male_consumption_total = 0
		for male_inhabitant in male_inhabitants:
			new_male_inhabitants[male_inhabitant] = male_inhabitants[male_inhabitant]
			#merge new data
			new_male_inhabitants[male_inhabitant]['water_consumption'] = merge_dicts(
				new_male_inhabitants[male_inhabitant]['water_consumption'],
				{
					#only consume water if its under alotted amount for habitat for that month
					permutation : animal_monthly_water_consumption if male_consumption_total <= (male_habitat_monthly_water - animal_monthly_water_consumption) else 0
				}
			)
			#add consumption to total
			male_consumption_total += animal_monthly_water_consumption

		#roughly distribute water 50/50
		female_habitat_monthly_water = habitat_monthly_water/2
		female_consumption_total = 0
		for female_inhabitant in female_inhabitants:
			new_female_inhabitants[female_inhabitant] = female_inhabitants[female_inhabitant]
			#merge new data
			new_female_inhabitants[female_inhabitant]['water_consumption'] = merge_dicts(
				new_female_inhabitants[female_inhabitant]['water_consumption'],
				{
					#only consume water if its under alotted amount for habitat for that month
					permutation : animal_monthly_water_consumption if female_consumption_total <= (female_habitat_monthly_water - animal_monthly_water_consumption) else 0
				}
			)
			#add consumption to total
			female_consumption_total += animal_monthly_water_consumption

		#return new dicts
		return female_inhabitants, male_inhabitants

	#passing in large amount of parameters because 
	#passing entire animal structure is potentially more expensive
	def breed_inhabitants(self,male_inhabitants,female_inhabitants,off_spring_rate,off_spring_min,off_spring_max,permutation):

		#create new lists so we can add while in loop
		new_female_inhabitants = {}
		new_male_inhabitants = {}
		new_births = {}
		i = 0

		#if is breeding interval
		if permutation % off_spring_rate == 0:

			#iterate through all females check if minimum age has been reached
			for female_inhabitant in female_inhabitants:
				#zero in numerator may cause an issue, lets ignore that
				try:
					if female_inhabitants[female_inhabitant]['age']/self.months_in_year > off_spring_min and female_inhabitants[female_inhabitant]['age']/self.months_in_year < off_spring_max:
						new_births[i] = i
				except OSError as e:
					print(e)

			#create new babies, if no new births loop wont iter once
			for new_birth in new_births:
				if random() < .5:
					#create correctly ordered key
					new_female_inhabitants = self.get_inhabitants_structure(len(female_inhabitants) + new_birth)
				else:
					#create correctly ordered key
					new_male_inhabitants = self.get_inhabitants_structure(len(male_inhabitants) + new_birth)

			#return merged dictionaries
			return merge_dicts(female_inhabitants, new_female_inhabitants), merge_dicts(male_inhabitants, new_male_inhabitants)
		else:
			#return original dictionaries
			return female_inhabitants, male_inhabitants

	#passing in large amount of parameters because 
	#passing entire animal structure is potentially more expensive
	def kill_inhabitants(
		self,male_inhabitants,female_inhabitants,permutation,animal_monthly_water_consumption,
		animal_monthly_food_consumption,life_span,minimum_temperature,maximum_temperature
	):
		male_inhabitants,female_inhabitants = self.kill_inhabitants_from_starvation(
			male_inhabitants,female_inhabitants
		)
		male_inhabitants,female_inhabitants = self.kill_inhabitants_from_dehydration(
			male_inhabitants,female_inhabitants
		)

		male_inhabitants,female_inhabitants = self.kill_inhabitants_from_natural_causes(
			male_inhabitants,female_inhabitants,life_span
		)

		male_inhabitants,female_inhabitants = self.kill_inhabitants_from_extreme_temperature(
			male_inhabitants,female_inhabitants,minimum_temperature,maximum_temperature
		)

		return male_inhabitants,female_inhabitants

	def kill_inhabitants_from_starvation(self,male_inhabitants,female_inhabitants):
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		#kill females
		i = 0
		#check each inhabitant
		for female_inhabitant in female_inhabitants:
			live = True
			#iterate through inhabitant food consumption
			for food_consumption in female_inhabitants[female_inhabitant]['food_consumption']:
				#if previous 2 month keys exist
				if ((female_inhabitants[female_inhabitant]['food_consumption']).has_key(food_consumption - 1)
					and (female_inhabitants[female_inhabitant]['food_consumption']).has_key(food_consumption - 2)):
					#then we check summation of those keys
					#if sum of this iteration and last 2 months consumption == 0 then we ignore addition to list
					#by setting live to False
					if ((female_inhabitants[female_inhabitant]['food_consumption'][food_consumption] + 
						 female_inhabitants[female_inhabitant]['food_consumption'][food_consumption - 1] +
						 female_inhabitants[female_inhabitant]['food_consumption'][food_consumption - 2]) <= 0):
						#by setting live to false, we are essentially killing 
						#that inhabitant by not transferring it to return dict
						live = False
						break
			#after inner loop processes we only add to return data structure
			#if live was never set to False
			if live:
				new_female_inhabitants[i] = female_inhabitants[female_inhabitant]
				#increment in order to reorder new structure
				i += 1

		#kill males
		i = 0
		#check each inhabitant
		for male_inhabitant in male_inhabitants:
			live = True
			#iterate through inhabitant food consumption
			for food_consumption in male_inhabitants[male_inhabitant]['food_consumption']:
				#if previous 2 month keys exist
				if ((male_inhabitants[male_inhabitant]['food_consumption']).has_key(food_consumption - 1)
					and (male_inhabitants[male_inhabitant]['food_consumption']).has_key(food_consumption - 2)):
					#then we check summation of those keys
					#if sum of this iteration and last 2 months consumption == 0 then we ignore addition to list
					#by setting live to False
					if ((male_inhabitants[male_inhabitant]['food_consumption'][food_consumption] + 
						 male_inhabitants[male_inhabitant]['food_consumption'][food_consumption - 1] +
						 male_inhabitants[male_inhabitant]['food_consumption'][food_consumption - 2]) <= 0):
						#by setting live to false, we are essentially killing 
						#that inhabitant by not transferring it to return dict
						live = False
						break
			#after inner loop processes we only add to return data structure
			#if live was never set to False
			if live:
				new_male_inhabitants[i] = male_inhabitants[male_inhabitant]
				#increment in order to reorder new structure
				i += 1

		return new_male_inhabitants,new_female_inhabitants

	def kill_inhabitants_from_dehydration(self,male_inhabitants,female_inhabitants):
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		#kill females
		i = 0
		#check each inhabitant
		for female_inhabitant in female_inhabitants:
			live = True
			#iterate through inhabitant water consumption
			for water_consumption in female_inhabitants[female_inhabitant]['water_consumption']:
				#if current month less than or equal to 0 then we kill due to thirst
				if female_inhabitants[female_inhabitant]['water_consumption'][water_consumption] <= 0:
					live = False
					break
			#after inner loop processes we only add to return data structure
			#if live was never set to False
			if live:
				new_female_inhabitants[i] = female_inhabitants[female_inhabitant]
				#increment in order to reorder new structure
				i += 1

		#kill males
		i = 0
		#check each inhabitant
		for male_inhabitant in male_inhabitants:
			live = True
			#iterate through inhabitant water consumption
			for water_consumption in male_inhabitants[male_inhabitant]['water_consumption']:
				#if current month less than or equal to 0 then we kill due to thirst
				if male_inhabitants[male_inhabitant]['water_consumption'][water_consumption] <= 0:
					live = False
					break
			#after inner loop processes we only add to return data structure
			#if live was never set to False
			if live:
				new_male_inhabitants[i] = male_inhabitants[male_inhabitant]
				#increment in order to reorder new structure
				i += 1

		return new_male_inhabitants,new_female_inhabitants

	def kill_inhabitants_from_natural_causes(self,male_inhabitants,female_inhabitants,life_span):
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		#kill females
		i = 0
		#check each inhabitant
		for female_inhabitant in female_inhabitants:
			#check age of each inhabitant against given life span
			if female_inhabitants[female_inhabitant]['age']/12 <= life_span:
				new_female_inhabitants[i] = female_inhabitants[female_inhabitant]
				#increment in order to reorder new structure
				i += 1

		#kill males
		i = 0
		#check each inhabitant
		for male_inhabitant in male_inhabitants:
			#check age of each inhabitant against given life span
			if male_inhabitants[male_inhabitant]['age']/12 <= life_span:
				new_male_inhabitants[i] = male_inhabitants[male_inhabitant]
				#increment in order to reorder new structure
				i += 1

		return new_male_inhabitants,new_female_inhabitants

	def kill_inhabitants_from_extreme_temperature(
		self,male_inhabitants,female_inhabitants,minimum_temperature,maximum_temperature
	):
		return male_inhabitants,female_inhabitants