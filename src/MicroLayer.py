from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random

class MicroLayer(BotLayer):

	def __init__(self):
		pass

	def pick_starting_regions(self, info, input):
		pass

	def place_troops(self, info, input):
		pass

	def attack_transfer(self, info, input):
		troop_numbers = []
		if info.has_key('you_decide') and not info['you_decide'] and info.has_key('troops'):
			troop_numbers = info['troops']
		else:
			troop_numbers = [10, 20, 12]
		
		return {
			'attack_transfers': [
				(1,2,troop_numbers[0]),
				(4,5,troop_numbers[1]),
				(7,3,troop_numbers[2])
			]
		}