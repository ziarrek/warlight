from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random

class StrategyLayer(BotLayer):

    def __init__(self):
        pass

    def pick_starting_regions(self, info, input):
        # output contains 'placements', will skip all further layers
        return {'picked_regions': ['19 ', '20', '18', '16', '15', '14', '13', '10', '11', '12', '13', '9' ]}
    
    def place_troops(self, info, input):
        pass

    def attack_transfer(self, info, input):
      world = info['world']
      your_bot = info['your_bot']
      super_regions = []
      for id in range(1, 6):

        super_region = world.get_super_region_by_id(id)
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
          for neighbour in region.neighbours:
            if neighbour.super_region != id:
              neighbour_found = False
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
        total_neighbour_regoins = neighbour_enemy_regions + neighbour_owned_regions + neighbour_neutral_regions
        total_troops = owned_troops + enemy_troops

        if total_troops != 0:
          immediate_thread_rate = (neighbour_enemy_troops - (owned_troops / 2)) / total_troops * 10
          own_occupation_rate = owned_regions / total_regions * 10
          enemy_occupation_rate = enemy_regions / total_regions * 10
          super_region_value = (immediate_thread_rate + own_occupation_rate) / 2 - (enemy_occupation_rate / 2)
        else:
          super_region_value = 0

        super_regions.append({id : super_region_value})
        
      return super_regions
