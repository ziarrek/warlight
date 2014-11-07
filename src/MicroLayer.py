from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random

class MicroLayer(BotLayer):

	def __init__(self):
		# a list of important regions from the higher layer
		self.regions = []

	def pick_starting_regions(self, info, input):
		pass

	def place_armies(self, info, input):
		regions = self.regions = input['regions']
		world = info['world']

		starting_armies = info['starting_armies']

		return {
			'placements': []
		}

	def attack_transfer(self, info, input):
		regions = self.regions
		world = info['world']

		return {
			'attack_transfers': []
		}