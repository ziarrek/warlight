from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random, get_other_player, format_region, format_move
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
		self.regions_of_interest = defaultdict(lambda: 0)
		self.riskiness = 0.5

	def pick_starting_regions(self, info, input):
		pass

	def place_armies(self, info, input):
		regions = self.regions = sorted(input['regions'], key=lambda x:x[1],reverse=True)

		self.regions_of_interest = defaultdict(lambda: 0)

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

		for region_id, region_priority, region_action in regions:
			# if not left_armies:
				# break
			region = world.get_region_by_id(region_id)

			if region_action == 'attack':
				opponent_troops = region.troop_count
				needed_attacking_troops = get_attack_armies(opponent_troops)
				allowed_troops_assignment = min(left_armies, needed_attacking_troops, int(math.ceil(starting_armies*region_priority/priorities_total)))
				candidates = sorted([neighbour for neighbour in region.neighbours if not neighbour.is_fog and neighbour.owner == player],key=lambda x:x.troop_count,reverse=True)
				candidate_unused_troops = {c.id: c.troop_count - used_troops[c.id] for c in candidates}

				proposed_moves = []

				needed_more = needed_attacking_troops
				allowed_more = allowed_troops_assignment
				for chosen in candidates:
					if needed_more <= 0:
						break
					unused = candidate_unused_troops[chosen.id]
					usage, assignment, needed_more = get_army_split(unused,allowed_more,needed_more)

					if unused<1 and assignment<1:
						continue
					placements_dict[chosen.id] += assignment
					chosen.troop_count += assignment
					used_troops[chosen.id] += usage + assignment
					allowed_more -= assignment
					left_armies -= assignment
					proposed_moves.append( (chosen.id, region.id, usage+assignment) )
					self.regions_of_interest[chosen.id] = max(self.regions_of_interest[chosen.id], region_priority)

				# if all attacks summed have the chance of killing more than half of the opponent's forces, attack


				if needed_more <= needed_attacking_troops * 0.5:
					moves += proposed_moves
					troops_used = needed_attacking_troops - needed_more
					pred_opp_casualties[region.id] += get_attack_casualties(troops_used)
				else:
					for start_id, end_id, troops in proposed_moves:
						used_troops[start_id] -= troops


			elif region_action == 'defend':
				neighbour_opponents = [neigh for neigh in region.neighbours if not neigh.is_fog and neigh.owner == opponent]

				# bail out if there is only one opponent and we are attacking him
				attacks_from_here = [move for move in moves if move[0]==region_id]
				if len(neighbour_opponents) == 1 and [1 for start, end, troops in attacks_from_here if end == neighbour_opponents[0].id]:
					stderr.write('Ignore defense: only opponent in '+format_region(end)+' attacked with\n\t'+format_move(start,end,troops)+'\n')
					continue

				# predict how many troops are needed to defend this regions
				# consider casualties to opponents from our planned attacks
				neighbour_opponent_troops = [max(0,neigh.troop_count - pred_opp_casualties[neigh.id] - 1) for neigh in neighbour_opponents]
				neighbour_opponent_troop_sum = max(neighbour_opponent_troops)
				needed_defending_troops = get_defend_armies(neighbour_opponent_troop_sum)
				allowed_troops_assignment = min(needed_defending_troops, int(round(starting_armies * region_priority/priorities_total)))

				unused = region.troop_count - used_troops[region_id]
				usage, assignment, needed_more = get_army_split(unused, allowed_troops_assignment, needed_defending_troops)
				placements_dict[region_id] += assignment
				region.troop_count += assignment
				used_troops[region_id] += usage+assignment
				left_armies -= assignment


		if left_armies>0 and moves:
			# redistribute unused armies to attack moves
			redistribution = int(math.ceil(left_armies *1.0/len(moves)))
			for i, move in enumerate(moves):
				if not left_armies:
					break
				amount = min(redistribution, left_armies)
				moves[i] = (move[0], move[1], move[2] + amount)
				placements_dict[move[0]] += amount
				left_armies -= amount
				stderr.write('Redistribute left_armies: add '+str(amount)+' to '+format_move(*move)+'\n')
		if left_armies>0 and placements_dict:
			# redistribute unused armies to placements
			redistribution = int(math.ceil(left_armies *1.0/len(placements_dict)))
			for placement_region_id in placements_dict:
				if not left_armies:
					break
				amount = min(redistribution, left_armies)
				placements_dict[placement_region_id] += amount
				left_armies -= amount
				stderr.write('Redistribute left_armies: add '+str(amount)+' to '+format_regin(placement_region_id)+'\n')

		# second iteration over regions: distribute unused and add regions_of_interest for defense
		# distribute unused troops from frontal regions to attack moves
		for region_id, region_priority, region_action in regions:
			if region_action == 'defend':
				self.regions_of_interest[region_id] = max(self.regions_of_interest[region_id], region_priority)

			region = world.get_region_by_id(region_id)
			unused = region.troop_count - used_troops[region_id]
			if region_id in self.regions_of_interest and unused>0:
				# stderr.write(format_region(region_id)+': unused troops: '+str(unused))
				local_moves = sorted([(i, move) for i, move in enumerate(moves) if move[0]==region_id],key=lambda x:x[1][2],reverse=True)
				if local_moves:
					i, best_move = local_moves[0]
					from_reg, to_reg, troops = best_move
					moves[i] = (from_reg,to_reg,troops+unused)
					stderr.write('Redistribute unused: add '+str(unused)+' to '+format_move(*best_move)+'\n')
					used_troops[region_id] += unused

		placements = [(reg_id, troop_count) for reg_id, troop_count in placements_dict.iteritems() if troop_count > 0]

		self.intended_moves = moves

		return {
			'placements': placements
		}

	def attack_transfer(self, info, input):
		world = info['world']
		player = info['your_bot']
		opponent = get_other_player(player)


		# algorithm for moving the idle armies to nearest region of interest
		alg_iter = 10 # acts as infinity - initial value of interest regions
		interest_regions = self.regions_of_interest

		stderr.write('\nRegions of interest:\n')
		for reg_id in interest_regions:
			stderr.write('\t'+format_region(reg_id)+'\n')
		# pp.pprint(interest_regions)

		initial_idle_moves = []
		deferred_idle_moves = []

		our_regions = {region.id: [False, 0, None, region] for region in world.regions if not region.is_fog and region.owner == player}

		# pp.pprint(our_regions)
		# pp.pprint(interest_regions)
		for region_id in interest_regions:
			# difference between = (go to closest interest regions) and += (take priority into consideration) - TEST!
			interest_regions[region_id] = alg_iter # or += alg_iter (see above)
			# pp.pprint(our_regions[region_id])
			our_regions[region_id][:2] = [True, alg_iter]

		for i in xrange(0,alg_iter):
			new_regions = dict(our_regions)
			for region_id, region_tup in our_regions.iteritems():
				is_interest, value, direction, region = tuple(region_tup)
				if not is_interest:
					for neighbour in region.neighbours:
						if neighbour.id in our_regions:
							neighbour_value = our_regions[neighbour.id][1]
							if neighbour_value - 1 > value:
								value = neighbour_value - 1
								direction = neighbour
					new_regions[region_id] = [is_interest, value, direction, region]
			our_regions = new_regions

		for region_id, region_tup in our_regions.iteritems():
			idle_region = region_tup[3]
			direction = region_tup[2]
			if region_id not in interest_regions:
				troop_count = idle_region.troop_count
				if troop_count > 1 and direction:
					move = (idle_region.id, direction.id, troop_count - 1)
					if direction.id in interest_regions:
						initial_idle_moves.append(move)
					else:
						deferred_idle_moves.append(move)
					stderr.write('Idle: '+format_move(*move)+'\n')

		attack_transfers = []
		attack_transfers += initial_idle_moves
		attack_transfers += self.intended_moves
		for move in self.intended_moves:
			stderr.write(format_move(*move)+'\n')
		attack_transfers += deferred_idle_moves


		return {
			'attack_transfers': attack_transfers
		}
