from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random
from sys import stderr

class StrategyLayer(BotLayer):

    def __init__(self):
        pass

    def pick_starting_regions(self, info, input):
      regions = info['regions']
      world = info['world']

      chosen_regions = []
      for region_id in regions:
        if world.get_region_by_id(region_id).super_region.id == '3':
          chosen_regions.append(region_id)
      for region_id in regions:
        if world.get_region_by_id(region_id).super_region.id == '4':
          chosen_regions.append(region_id)
      for region_id in regions:
        if world.get_region_by_id(region_id).super_region.id == '2':
          chosen_regions.append(region_id)

        # output contains 'placements', will skip all further layers
        return {'picked_regions': chosen_regions}

    def place_armies(self, info, input):
      world = info['world']
      your_bot = info['your_bot']
      super_regions = []
      for super_region in world.super_regions:

        super_region_neigbours = []

        owned_troops = 0
        enemy_troops = 0
        owned_regions = 0
        enemy_regions = 0
        neutral_regions = 0
        neighbour_owned_troops = 0
        neighbour_enemy_troops = 0
        neighbour_owned_regions = 0
        neighbour_enemy_regions = 0
        neighbour_neutral_regions = 0

        for region in super_region.regions:
          if region.owner == 'neutral':
            neutral_regions += 1
          elif region.owner == your_bot:
            owned_troops += region.troop_count
            owned_regions += 1
          else:
            enemy_troops += region.troop_count
            enemy_regions += 1

          #if region.is_on_super_region_border
          
          neighbour_found = False
          for neighbour in region.neighbours:
          neighbour_found = False
            if neighbour.super_region != super_region:
              for found_neighbour in super_region_neigbours:
                if neighbour.id == found_neighbour.id:
                  neighbour_found = True

            if not neighbour_found:
              super_region_neigbours.append(neighbour)
        
        for neighbour in super_region_neigbours:
          if region.owner == 'neutral':
            neighbour_neutral_regions += 1
          elif region.owner == your_bot:
            neighbour_owned_troops += region.troop_count
            neighbour_owned_regions += 1
          else:
            neighbour_enemy_troops += region.troop_count
            neighbour_enemy_regions += 1


        total_regions = owned_regions + enemy_regions + neutral_regions
        total_neighbour_regions = neighbour_enemy_regions + neighbour_owned_regions + neighbour_neutral_regions
        total_troops = owned_troops + enemy_troops

        if total_troops != 0:
          immediate_thread_rate = (neighbour_enemy_troops - (owned_troops / 2)) / total_troops * 10
          own_occupation_rate = owned_regions / total_regions * 10
          enemy_occupation_rate = enemy_regions / total_regions * 10
          super_region_value = (immediate_thread_rate + own_occupation_rate) / 2 - (enemy_occupation_rate / 2)
        else:
          super_region_value = 0

        super_regions.append((super_region.id, super_region_value))

      return {
        'continents': super_regions
      }

    def attack_transfer(self, info, input):
      pass

class SuperRegionData(object):
  def __init__(self):
    self.owned_troops = 0
    self.enemy_troops = 0
    self.owned_regions = 0
    self.enemy_regions = 0
    self.neutral_regions = 0
    self.neighbour_owned_troops = 0
    self.neighbour_enemy_troops = 0
    self.neighbour_owned_regions = 0
    self.neighbour_enemy_regions = 0
    self.neighbour_neutral_regions = 0

    total_regions = 0
    total_troops = 0
    total_neighbour_regoins = 0

