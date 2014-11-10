from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random, get_other_player
import math
import pprint
from collections import defaultdict
from operator import itemgetter
from sys import stderr

pp = pprint.PrettyPrinter(stream=stderr,indent=2)

def get_attack_armies(defender_count, risky=0.5):
	return int(math.ceil(defender_count / 0.6 + 1))

def get_defend_armies(attacker_count, risky=0.5):
	return int(math.ceil(attacker_count / 0.6 + 1))

def get_attack_casualties(attacker_count,risky=0.5):
	return int(round(attacker_count * 0.5))

class MicroLayer(BotLayer):

	def __init__(self):
		# a list of important regions from the higher layer
		self.regions = []
		self.player = ''
		self.opponent = ''
		self.intended_moves = []
		self.riskiness = 0.5

	def pick_starting_regions(self, info, input):
		pass

	def place_armies(self, info, input):
		regions = self.regions = sorted(input['regions'], key=lambda x:x[1],reverse=True)

		world = info['world']
		your_bot = info['your_bot']
		self.player = player = your_bot
		self.opponent = opponent = get_other_player(player)

		starting_armies = info['starting_armies']
		left_armies = starting_armies

		priorities_total = sum([tup[1] for tup in regions]) * 1.0

		# troops already on the map that have been assigned to a specific action
		used_troops = defaultdict(lambda: 1)
		# predicted casualties brought to opponent regions by our planned attacks
		pred_opp_casualties = defaultdict(lambda: 0)

		# planned moves (to be executed in attack_transfer)
		moves = []
		# planned troop placements
		placements_dict = defaultdict(lambda: 0)


		for region_tup in regions:
			region_id, region_priority, region_action = region_tup
			region = world.get_region_by_id(region_id)

			if region_action == 'attack':
				opponent_troops = region.troop_count
				needed_attacking_troops = get_attack_armies(opponent_troops)
				allowed_troops_assignment = min(needed_attacking_troops, int(round(starting_armies*region_priority/priorities_total)))
				candidates = [neighbour for neighbour in region.neighbours if neighbour.owner == player]
				candidate_unused_troops = [c.troop_count - used_troops[c.id] for c in candidates]
				# get neighbour with maximum unused troops
				chosen_i, chosen_unused_troops = max(enumerate(candidate_unused_troops), key=itemgetter(1))
				chosen = candidates[chosen_i]
				unused = candidate_unused_troops[chosen_i]
				used_troops[chosen.id] += min(needed_attacking_troops, unused)
				if needed_attacking_troops > unused:
					needed_more = needed_attacking_troops - unused
					# used_troops[chosen.id] += unused
					final_assignment = min(needed_more, allowed_troops_assignment)
					placements_dict[chosen.id] += final_assignment
					left_armies -= final_assignment

					if needed_more > allowed_troops_assignment:
						# skip the movement, wait for better times...
						continue
						# placements_dict[chosen.id] += allowed_troops_assignment
						# left_armies -= allowed_troops_assignment
					# else:
						# placements_dict[chosen.id] += needed_more
						# left_armies -= needed_more
						# moves.append( (chosen.id, region.id, needed_attacking_troops) )
				# else:
					# used_troops[chosen.id] += needed_attacking_troops

				# add the intended move to the list
				moves.append( (chosen.id, region.id, needed_attacking_troops) )
				pred_opp_casualties[region.id] += get_attack_casualties(needed_attacking_troops)


			elif region_action == 'defend':
				neighbour_opponents = [neigh for neigh in region.neighbours if neigh.owner == opponent]
				# predict how many troops are needed to defend this regions
				# consider casualties to opponents from our planned attacks
				neighbour_opponent_troops = [max(0,neigh.troop_count - pred_opp_casualties[neigh.id]) for neigh in neighbour_opponents]
				neighbour_opponent_troop_sum = sum(neighbour_opponent_troops)
				needed_defending_troops = get_defend_armies(neighbour_opponent_troop_sum)
				allowed_troops_assignment = min(needed_defending_troops, int(round(starting_armies * region_priority/priorities_total)))
				unused = region.troop_count - used_troops[region_id]
				used_troops[region_id] += min(needed_defending_troops, unused)

				if needed_defending_troops > unused:
					needed_more = needed_defending_troops - unused
					final_assignment = min(needed_more, allowed_troops_assignment)
					placements_dict[region_id] += final_assignment
					left_armies -= final_assignment

			if not left_armies:
				break

		if moves:
			# redistribute unused armies to attack moves
			redistribution = int(math.ceil(left_armies *1.0/len(moves)))
			for i, move in enumerate(moves):
				if not left_armies:
					break
				amount = min(redistribution, left_armies)
				moves[i] = (move[0], move[1], move[2] + amount)
				# move[2] += amount
				placements_dict[move[0]] += amount
				left_armies -= amount

		# while left_armies:
		# 	for move in moves:
		# 		move[2] += 1
		# 		placements_dict[move[0]] += 1
		# 		left_armies -= 1
		# 		if not left_armies:
		# 			break

		placements = [(reg_id, troop_count) for reg_id, troop_count in placements_dict.iteritems() if troop_count > 0]

		stderr.write('\n\n')
		pp.pprint(placements)
		stderr.write('\n\n')
		stderr.write('place_armies: left_armies: '+str(left_armies))
		self.intended_moves = moves

		return {
			'placements': placements
		}

	def attack_transfer(self, info, input):
		regions = self.regions
		world = info['world']

		player = info['your_bot']
		opponent = get_other_player(player)


		attack_transfers = [move for move in self.intended_moves]
		# attack_transfers = []
		# for region_tup in regions:
		# 	region_id = region_tup[0]
		# 	region_action = region_tup[2]
		# 	region = world.get_region_by_id(region_id)

		# 	if region_action == 'attack':
		# 		# TODO add intended_moves use
		# 		candidates = []
		# 		for neighbour in region.neighbours:
		# 			if not neighbour.is_fog and neighbour.owner == player:
		# 				candidates.append(neighbour)
		# 		if candidates:
		# 			move_region = max(candidates,key=lambda x:x.troop_count)
		# 			move_region_id = move_region.id
		# 			move_troops_count = move_region.troop_count - 1
		# 			if move_troops_count:
		# 				attack_transfers.append((move_region_id, region_id, move_troops_count))

		return {
			'attack_transfers': attack_transfers
		}
