from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random
from math import ceil

# get other players name, assumes two constant name: player1, player2
def get_other_player(player_name):
	return 'player1' if player_name == 'player1' else 'player2'

class MicroLayer(BotLayer):

	def __init__(self):
		# a list of important regions from the higher layer
		self.regions = []
		self.player = ''
		self.opponent = ''

	def pick_starting_regions(self, info, input):
		pass

	def place_armies(self, info, input):
		regions = self.regions = sorted(input['regions'], key=lambda x:x[1],reversed=True)

		world = info['world']
		self.player = player = info['your_bot']
		self.opponent = opponent = get_other_player(player)

		starting_armies = info['starting_armies']
		left_armies = starting_armies

		placements = []

		# distribute the armies by giving half of the remaining number
		# to the next region, stop when ran out of armies
		# with 7 armies available, 3 regions will be populated
		for region in regions:
			region_id = region[0]
			region_action = region[2]

			# TODO
			placement_region = ''
			place_n = int(round(left_armies*1.0/2))
			placements.append((region_id,place_n))
			left_armies -= place_n
			if not left_armies:
				break

		return {
			'placements': placements
		}

	def attack_transfer(self, info, input):
		regions = self.regions
		world = info['world']

		for region in regions:
			region_id = region[0]
			region_action = region[2]
			region_obj = world.get_region_by_id(region_id)




		return {
			'attack_transfers': []
		}