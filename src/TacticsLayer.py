from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random

class TacticsLayer(BotLayer):

	def __init__(self):
		pass

	def pick_starting_regions(self, info, input):
		pass

	def place_armies(self, info, input):
		pass

	def attack_transfer(self, info, input):
		if info.has_key('cmd_for_lower_layer'):
			return {
				'you_decide': False,
				'troops': [3,4,5]
			}
		else:
			return {'you_decide': True}