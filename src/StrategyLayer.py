from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random

class StrategyLayer(BotLayer):

	def __init__(self):
		pass

	def pick_starting_regions(self, info, input):
		# output contains 'placements', will skip all further layers
		return {'placements': [10, 1, 30, 12, 43, 23]}

	def place_troops(self, info, input):
		pass

	def attack_transfer(self, info, input):
		world = info['world']
		your_bot = info['your_bot']

		return {'cmd_for_lower_layer': 666}