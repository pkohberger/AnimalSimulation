import yaml
import os
from pprint import pprint
from app import UPLOAD_FOLDER, OUTPUT_FOLDER, merge_dicts
from utils import Utils
from random import random

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
	POPULATION = 0
	CAUSES_OF_DEATH_RAW = {
		'TOTAL_DIED' : 0,
		'STARVATION' : 0,
		'THIRST': 0,
		'COLD_WEATHER':0,
		'HOT_WEATHER':0
	}
	CAUSES_OF_DEATH_AGGREGATED = {
		'starvation' : 0,
		'thirst': 0,
		'cold_weather':0,
		'hot_weather':0
	}
	MAX_POPULATION = 0
	MORTALITY_RATE = 0
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
				self.DEBUG = False
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
		return dict({
			key : {
				'age' : 0, 
				'food_consumption' : {},
				'water_consumption' : {}
			}
		})

	def process_all_habitat_simulations(self):
		try:
			for animal in self.species:
				self.OUTPUT[animal['name']] = {}
				for habitat in self.habitats:
					self.OUTPUT[animal['name']][habitat['name']] = self.process_habitat_simulation(animal,habitat)
			#output data structure to yaml format
			file_name = os.path.join(OUTPUT_FOLDER, "sample_output.txt")
			with open(file_name, 'w') as stream:
				yaml.dump(self.OUTPUT, stream, default_flow_style=False)

				if self.DEBUG:
					pprint(self.OUTPUT)

				return True
			
		except OSError as e:
			print(e)
			return False

	def process_habitat_simulation(self,animal,habitat):

		#each habitat starts off with exactly one
		#male and one female
		male_inhabitants = self.get_inhabitants_structure(0)
		female_inhabitants = self.get_inhabitants_structure(0)
		permutation = 0

		#attempt to initialize species variables
		try:
			animal_monthly_water_consumption = animal['attributes']['monthly_water_consumption']
			animal_monthly_food_consumption = animal['attributes']['monthly_food_consumption']
			animal_temperature_failure_decimation_percentage = animal['attributes']['temperature_failure_decimation_percentage']
			life_span = animal['attributes']['life_span']
			animal_minimum_temperature = animal['attributes']['minimum_temperature']
			animal_maximum_temperature = animal['attributes']['maximum_temperature']
			off_spring_rate = animal['attributes']['off_spring_rate']
			off_spring_min = animal['attributes']['off_spring_min']
			off_spring_max = animal['attributes']['off_spring_max']
			habitat_monthly_food = habitat['monthly_food']
			habitat_monthly_water = habitat['monthly_water']
			habitat_average_temperature = habitat['average_temperature']
		except OSError as e:
			print(e)
			#return if missing info
			return False

		#make sure we clear the habitat
		#aggregation properties for each habitat
		self.reset_habitat_data_structures()		

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
					animal_monthly_food_consumption,life_span,animal_minimum_temperature,animal_maximum_temperature,
					habitat_average_temperature,month,animal_temperature_failure_decimation_percentage
				)

				self.aggregate_population_data(len(female_inhabitants)+len(female_inhabitants))
				self.aggregate_max_population_data(len(female_inhabitants)+len(female_inhabitants))

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
			pprint(self.CAUSES_OF_DEATH_RAW)

		return {
			"Average_Population" : self.get_aggregate_population_data(), 
			"Max_Population" : self.get_aggregate_max_population_data(), 
			"Mortality_Rate" : self.get_aggregate_mortality_data(), 
			"Cause_of_Death" : self.get_aggregate_death_clauses()
		}

	def reset_habitat_data_structures(self):
		self.POPULATION = 0
		self.MAX_POPULATION = 0
		self.CAUSES_OF_DEATH_RAW = {
			'TOTAL_DIED' : 0,
			'STARVATION' : 0,
			'THIRST': 0,
			'COLD_WEATHER':0,
			'HOT_WEATHER':0
		}
		self.CAUSES_OF_DEATH_AGGREGATED = {
			'starvation' : 0,
			'thirst': 0,
			'cold_weather':0,
			'hot_weather':0
		}
		self.MAX_POPULATION = 0
		self.MORTALITY_RATE = 0
		return

	def get_aggregate_population_data(self):
		return self.POPULATION/(self.years * self.months_in_year)

	def aggregate_population_data(self,inhabitants_count):
		self.POPULATION += inhabitants_count
		return

	def get_aggregate_max_population_data(self):
		return self.MAX_POPULATION

	def aggregate_max_population_data(self,inhabitants_count):
		self.MAX_POPULATION = max(inhabitants_count,self.MAX_POPULATION)
		return

	def get_aggregate_mortality_data(self):
		return str(round(float(float(self.CAUSES_OF_DEATH_RAW["TOTAL_DIED"])/float(self.POPULATION) * float(100)),2))+"%"

	def get_aggregate_death_clauses(self):
		#current iteration plus previous
		total_died = self.CAUSES_OF_DEATH_RAW["TOTAL_DIED"]
		starvation = self.CAUSES_OF_DEATH_RAW["STARVATION"]
		thirst = self.CAUSES_OF_DEATH_RAW["THIRST"]
		cold_weather = self.CAUSES_OF_DEATH_RAW["COLD_WEATHER"]
		hot_weather = self.CAUSES_OF_DEATH_RAW["HOT_WEATHER"]

		if total_died == 0:
			#build structure
			return  {
				'starvation' : "0.00%",
				'thirst': "0.00%",
				'cold_weather': "0.00%",
				'hot_weather': "0.00%"
			}
		else:
			#build structure
			return  {
				'starvation' : str(round(float(float(starvation)/float(total_died) * float(100)),2)) + "%",
				'thirst': str(round(float(float(thirst)/float(total_died) * float(100)),2)) + "%",
				'cold_weather': str(round(float(float(cold_weather)/float(total_died) * float(100)),2)) + "%",
				'hot_weather': str(round(float(float(hot_weather)/float(total_died) * float(100)),2)) + "%"
			}

	def aggregate_death_clauses(
		self,killed_from_starvation,killed_from_thirst,killed_from_natural_causes,
		killed_from_cold_weather,killed_from_hot_weather,male_inhabitants_living_count,female_inhabitants_living_count
	):

		#current iteration plus previous
		total_died = killed_from_starvation + killed_from_thirst + killed_from_natural_causes + killed_from_cold_weather + killed_from_hot_weather + self.CAUSES_OF_DEATH_RAW["TOTAL_DIED"]
		starvation = killed_from_starvation + self.CAUSES_OF_DEATH_RAW["STARVATION"]
		thirst = killed_from_thirst + self.CAUSES_OF_DEATH_RAW["THIRST"]
		cold_weather = killed_from_cold_weather + self.CAUSES_OF_DEATH_RAW["COLD_WEATHER"]
		hot_weather = killed_from_hot_weather + self.CAUSES_OF_DEATH_RAW["HOT_WEATHER"]

		#rebuild structure
		self.CAUSES_OF_DEATH_RAW = {
			'TOTAL_DIED' : total_died,
			'STARVATION' : starvation,
			'THIRST': thirst,
			'COLD_WEATHER': cold_weather,
			'HOT_WEATHER': hot_weather
		}

		return		

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
		#TODO make the limit actual by
		#computing percentage of males to females
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
		#TODO make the limit actual by
		#computing percentage of males to females
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
		#TODO make the limit actual by
		#computing percentage of males to females
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
		#TODO make the limit actual by
		#computing percentage of males to females
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
					if  female_inhabitants[female_inhabitant]['age']/self.months_in_year > off_spring_min and female_inhabitants[female_inhabitant]['age']/self.months_in_year < off_spring_max:
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
		animal_monthly_food_consumption,life_span,animal_minimum_temperature,animal_maximum_temperature,
		habitat_average_temperature,month,animal_temperature_failure_decimation_percentage
	):

		killed_from_starvation = 0
		killed_from_thirst = 0
		killed_from_natural_causes = 0
		killed_from_cold_weather = 0
		killed_from_hot_weather = 0
		
		male_inhabitants,female_inhabitants,killed_from_natural_causes = self.kill_inhabitants_from_natural_causes(
			male_inhabitants,female_inhabitants,life_span
		)

		male_inhabitants,female_inhabitants,killed_from_starvation = self.kill_inhabitants_from_starvation(
			male_inhabitants,female_inhabitants
		)

		male_inhabitants,female_inhabitants,killed_from_thirst = self.kill_inhabitants_from_thirst(
			male_inhabitants,female_inhabitants
		)

		male_inhabitants,female_inhabitants,killed_from_cold_weather,killed_from_hot_weather = self.kill_inhabitants_from_extreme_temperature(
			male_inhabitants,female_inhabitants,animal_minimum_temperature,animal_maximum_temperature,
			habitat_average_temperature,month,animal_temperature_failure_decimation_percentage
		)

		self.aggregate_death_clauses(
			killed_from_starvation,killed_from_thirst,killed_from_natural_causes,
			killed_from_cold_weather,killed_from_hot_weather,len(male_inhabitants),len(female_inhabitants)
		)

		return male_inhabitants,female_inhabitants

	def kill_inhabitants_from_starvation(self,male_inhabitants,female_inhabitants):
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		killed_from_starvation = 0

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
						killed_from_starvation += 1
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
						killed_from_starvation += 1
			#after inner loop processes we only add to return data structure
			#if live was never set to False
			if live:
				new_male_inhabitants[i] = male_inhabitants[male_inhabitant]
				#increment in order to reorder new structure
				i += 1

		return new_male_inhabitants,new_female_inhabitants,killed_from_starvation

	def kill_inhabitants_from_thirst(self,male_inhabitants,female_inhabitants):
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		killed_from_thirst = 0

		#we are assuming that the current iteration stands for one given month
		#because as this loop moves to the next iteration it is guarenteed that for one month
		#the fluctuation temperature will persist

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
					killed_from_thirst += 1
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
					killed_from_thirst += 1
			#after inner loop processes we only add to return data structure
			#if live was never set to False
			if live:
				new_male_inhabitants[i] = male_inhabitants[male_inhabitant]
				#increment in order to reorder new structure
				i += 1

		return new_male_inhabitants,new_female_inhabitants,killed_from_thirst

	def kill_inhabitants_from_natural_causes(self,male_inhabitants,female_inhabitants,life_span):
		new_male_inhabitants = self.get_inhabitants_structure(0)
		new_female_inhabitants = self.get_inhabitants_structure(0)

		killed_from_natural_causes = 0

		#kill females
		i = 0
		#check each inhabitant
		for female_inhabitant in female_inhabitants:
			#check age of each inhabitant against given life span
			#we are transferring all unless they are older
			if female_inhabitants[female_inhabitant]['age']/12 <= life_span:
				new_female_inhabitants[i] = female_inhabitants[female_inhabitant]
				#increment in order to reorder new structure
				i += 1
			else:
				killed_from_natural_causes += 0

		#kill males
		i = 0
		#check each inhabitant
		for male_inhabitant in male_inhabitants:
			#check age of each inhabitant against given life span
			#we are transferring all unless they are older
			if male_inhabitants[male_inhabitant]['age']/12 <= life_span:
				new_male_inhabitants[i] = male_inhabitants[male_inhabitant]
				#increment in order to reorder new structure
				i += 1
			else:
				killed_from_natural_causes += 0

		return new_male_inhabitants,new_female_inhabitants,killed_from_natural_causes

	def kill_inhabitants_from_extreme_temperature(
		self,male_inhabitants,female_inhabitants,animal_minimum_temperature,animal_maximum_temperature,
		habitat_average_temperature,month,animal_temperature_failure_decimation_percentage
	):

		killed_from_cold_weather = 0
		killed_from_hot_weather = 0

		actual_fluctuated_temperature = self.get_monthly_fluctuated_temperature(
			habitat_average_temperature[self.get_season(month)]
		)
		
		decimation_amount = 0
		#if in temperature danger zone
		#we are assuming that the current iteration stands for one given month
		#because as this loop moves to the next iteration it is guarenteed that for one month
		#the fluctuation temperature will persist
		if actual_fluctuated_temperature > animal_maximum_temperature or actual_fluctuated_temperature < animal_minimum_temperature:

			new_male_inhabitants = self.get_inhabitants_structure(0)
			new_female_inhabitants = self.get_inhabitants_structure(0)

			#count of females plus given percentage
			decimation_amount = int(float(len(female_inhabitants)) * float(float(animal_temperature_failure_decimation_percentage)/float(100)))

			#if greater then one then decimate
			if decimation_amount >= 1:
				i = 0
				j = 0
				for female_inhabitant in female_inhabitants:
					#only add if counter greater than decimation kill number
					#we are essentially skipping the oldest inhabitants
					#as they are most susceptible to fluctuation changes, thats
					#the assumption anyway
					if i > decimation_amount:
						new_female_inhabitants[j] = female_inhabitants[female_inhabitant]
						#for renumbering
						j += 1
					else:
						killed_from_cold_weather += 1 if actual_fluctuated_temperature < animal_minimum_temperature else 0
						killed_from_hot_weather += 1 if actual_fluctuated_temperature > animal_maximum_temperature else 0
					i += 1
			#if we have a decimation value equal to 0
			#it means we are in the temperature danger zone
			#but our population isnt large enough to kill a percentage of
			#so we return our original structure. lets let the population grow
			#and only kill if we have a valid integer response from decimation_amount
			#i ran into this edge case while testing,if we are testing and returning floats then the 
			#population will never grow
			else:
				new_female_inhabitants = female_inhabitants

			#count of males plus given percentage
			decimation_amount = int(float(len(male_inhabitants)) * float(float(animal_temperature_failure_decimation_percentage)/float(100)))

			#if greater then one then decimate
			if decimation_amount >= 1:
				i = 0
				j = 0
				for male_inhabitant in male_inhabitants:
					#only add if counter greater than decimation kill number
					#we are essentially skipping the oldest inhabitants
					#as they are most susceptible to fluctuation changes, thats
					#the assumption anyway
					if i >= decimation_amount:
						new_male_inhabitants[j] = male_inhabitants[male_inhabitant]
						#for renumbering
						j += 1
					else:
						killed_from_cold_weather += 1 if actual_fluctuated_temperature < animal_minimum_temperature else 0
						killed_from_hot_weather += 1 if actual_fluctuated_temperature > animal_maximum_temperature else 0
					i += 1
			#if we have a decimation value equal to 0
			#it means we are in the temperature danger zone
			#but our population isnt large enough to kill a percentage of
			#so we return our original structure. lets let the population grow
			#and only kill if we have a valid integer response from decimation_amount
			#i ran into this edge case while testing,if we are testing and returning floats then the 
			#population will never grow
			else:
				new_male_inhabitants = male_inhabitants

			#only returning new if severe temperature fluctuation
			return new_male_inhabitants,new_female_inhabitants,killed_from_cold_weather,killed_from_hot_weather

		return male_inhabitants,female_inhabitants,killed_from_cold_weather,killed_from_hot_weather

	def get_monthly_fluctuated_temperature(self,temperature):
		#randomnly choose between hotter or colder fluctuation
		if random() < .5:
			#give .05 % chance 15 degrees colder
			if random() < .05:
				temperature -= 15
			#else make 5 degrees colder
			else:
				temperature -= 5
		else:
			#give .05 % chance 15 degrees hotter
			if random() < .05:
				temperature += 15
			#else make 5 degrees hotter
			else:
				temperature += 5

		return temperature