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

		def get_army_split(unused_existing, allowed_assignment, needed):
			usage = min(needed, unused_existing)
			assignment = 0
			unfulfilled = 0
			if unused_existing < needed:
				more_needed = needed - unused_existing
				assignment = min(more_needed, allowed_assignment)
				if assignment < more_needed:
					unfulfilled = more_needed - assignment
			return (usage, assignment, unfulfilled)

		for region_tup in regions:
			if not left_armies:
				break
			region_id, region_priority, region_action = region_tup
			region = world.get_region_by_id(region_id)

			if region_action == 'attack':
				opponent_troops = region.troop_count
				needed_attacking_troops = get_attack_armies(opponent_troops)
				allowed_troops_assignment = min(needed_attacking_troops, int(round(starting_armies*region_priority/priorities_total)))
				candidates = sorted([neighbour for neighbour in region.neighbours if neighbour.owner == player],key=lambda x:x.troop_count,reverse=True)
				candidate_unused_troops = {c.id: c.troop_count - used_troops[c.id] for c in candidates}

				proposed_moves = []

				needed_more = needed_attacking_troops
				allowed_more = allowed_troops_assignment
				for chosen in candidates:
					if needed_more <= 0 or allowed_more <= 0:
						break
					unused = candidate_unused_troops[chosen.id]
					usage, assignment, needed_more = get_army_split(unused,allowed_more,needed_more)

					used_troops[chosen.id] += usage
					placements_dict[chosen.id] += assignment
					allowed_more -= assignment
					left_armies -= assignment
					proposed_moves.append( (chosen.id, region.id, usage+assignment) )

				# if all attacks have the chance of killing more than half of the opponent's forces, attack
				if needed_more <= needed_attacking_troops * 0.5:
					moves += proposed_moves
					troops_used = needed_attacking_troops - needed_more
					pred_opp_casualties[region.id] += get_attack_casualties(troops_used)

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

		if left_armies and moves:
			# redistribute unused armies to attack moves
			redistribution = int(math.ceil(left_armies *1.0/len(moves)))
			for i, move in enumerate(moves):
				if not left_armies:
					break
				amount = min(redistribution, left_armies)
				moves[i] = (move[0], move[1], move[2] + amount)
				placements_dict[move[0]] += amount
				left_armies -= amount
		if left_armies:
			# redistribute unused armies to placements
			redistribution = int(math.ceil(left_armies *1.0/len(placements_dict)))
			for placement_region_id in placements_dict:
				if not left_armies:
					break
				amount = min(redistribution, left_armies)
				placements_dict[placement_region_id] += amount
				left_armies -= amount

		placements = [(reg_id, troop_count) for reg_id, troop_count in placements_dict.iteritems() if troop_count > 0]

		self.intended_moves = moves

		return {
			'placements': placements
		}

	def attack_transfer(self, info, input):

		attack_transfers = [move for move in self.intended_moves]

		return {
			'attack_transfers': attack_transfers
		}
