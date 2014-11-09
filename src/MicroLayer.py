from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random, get_other_player
from math import ceil
from sys import stderr



class MicroLayer(BotLayer):

	def __init__(self):
		# a list of important regions from the higher layer
		self.regions = []
		self.player = ''
		self.opponent = ''
		self.intended_moves = []

	def pick_starting_regions(self, info, input):
		pass

	def place_armies(self, info, input):
		regions = self.regions = sorted(input['regions'], key=lambda x:x[1],reverse=True)

		world = info['world']
		self.player = player = info['your_bot']
		self.opponent = opponent = get_other_player(player)

		starting_armies = info['starting_armies']
		left_armies = starting_armies

		self.intended_moves = []
		placements = []
		stderr.write('your_bot: '+your_bot)
		stderr.write('\n\nour regions:'+ ''.join([reg.id for reg in world.regions if reg.owner == player]))
		# distribute the armies by giving half of the remaining number
		# to the next region, stop when ran out of armies
		# with 7 armies available, 3 regions will be populated
		for region in regions:
			region_id = region[0]
			region_action = region[2]
			region_obj = world.get_region_by_id(region_id)
			placement_region_id =''
			stderr.write('checked region: '+region_id+'\n')
			if region_action == 'attack':
				candidates = []
				for neighbour in region_obj.neighbours:
					stderr.write('neighbour id: '+neighbour.id+'\n')
					stderr.write('is_fog: '+neighbour.is_fog+" "+'owner: '+neighbour.owner+'\n')
					if not neighbour.is_fog and neighbour.owner == player:
						candidates.append(neighbour)
				if candidates:
					placement_region = max(candidates,key=lambda x:x.troop_count)
					placement_region_id = placement_region.id
				# TODO add intended_move handling
			elif region_action == 'defend':
				placement_region_id = region_id

			if placement_region_id == '':
				continue
			placement_troops_count = int(round(left_armies*1.0/2))
			placements.append((placement_region_id,placement_troops_count))
			left_armies -= placement_troops_count
			if not left_armies:
				break

		return {
			'placements': placements
		}

	def attack_transfer(self, info, input):
		regions = self.regions
		world = info['world']

		attack_transfers = []
		for region in regions:
			region_id = region[0]
			region_action = region[2]
			region_obj = world.get_region_by_id(region_id)

			if region_action == 'attack':
				# TODO add intended_moves use
				candidates = []
				for neighbour in region_obj.neighbours:
					if not neighbour.is_fog and neighbour.owner == player:
						candidates.append(neighbour)
				if candidates:
					move_region = max(candidates,key=lambda x:x.troop_count)
					move_region_id = move_region.id
					move_troops_count = move_region.troops_count - 1
					if move_troops_count:
						attack_transfers.append((move_region_id, region_id, move_troops_count))

		return {
			'attack_transfers': attack_transfers
		}
