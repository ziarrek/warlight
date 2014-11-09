from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random
from sys import stderr

class StrategyLayer(BotLayer):

    def __init__(self):
      super_region_data = []
      data_init = False
      initial_phase = True
      expand_protect_phase = False
      super_region_importance = [1, 0, 2, 1, -1, 0]

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

        super_region_data = SuperRegionData()
        if not data_init:
          super_region_data_list.append(super_region_data)
        else:
          for temp_super_region_data in super_region_data_list:
            if temp_super_region_data.id == focus_super_region.id:
              super_region_data = temp_super_region_data

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

        #Storing information in classs SuperRegionData
        super_region_data.owned_troops = owned_troops
        super_region_data.enemy_troops = enemy_troops 
        super_region_data.owned_regions = owned_regions
        super_region_data.enemy_regions = enemy_regions
        super_region_data.neutral_regions = neutral_regions
        super_region_data.neighbour_owned_troops = neighbour_owned_troops
        super_region_data.neighbour_enemy_troops = neighbour_enemy_troops
        super_region_data.neighbour_owned_regions = neighbour_owned_regions
        super_region_data.neighbour_enemy_regions = neighbour_enemy_regions
        super_region_data.neighbour_neutral_regions = neighbour_neutral_regions
'''
        if total_troops != 0:

          immediate_thread_rate = (neighbour_enemy_troops - (owned_troops / 2)) / total_troops * 10
          
          own_occupation_rate = owned_regions / total_regions * 10
          
          enemy_occupation_rate = enemy_regions / total_regions * 10
          
          super_region_value = (immediate_thread_rate + own_occupation_rate) / 2 - (enemy_occupation_rate / 2)
        else:
          super_region_value = 0

   '''     

      #Ensures old data can stay (when implemented)
      data_init = True

      #Check if initial phase is done
      expand_protect_phase = True
      for super_region_data in super_region_data_list:
        if super_region_data.owned_regions == super_region_data.total_regions:
          initial_phase = False
          expand_protect_phase = False

      for super_region_data in super_region_data_list:
        super_region_data.value = 0
        if super_region_data.owned_regions > 0:
          super_region_data.phase = 3
        elif super_region_neigbours.owned_regions > 0:
          super_region_data.phase = 2
        else:
          super_region_data.phase = 1

      # PHASE Initial
      if initial_phase:
        focus_super_region = SuperRegionData()
        current_best_occupaction = 0
        for super_region_data in super_region_data_list:
          if current_best_occupaction < super_region_data.owned_troops:
            focus_super_region = super_region_data
          if current_best_occupaction == super_region_data.owned_troops:
            pass
            #NOT IMPLEMENTED: Choose based on the list of preference and enemy occupation
          if super_region_data.owned_troops > 0:
            super_region_data.value = 2

        focus_super_region = 8  

      #PHASE expand and protect
      protection_level = 0
      if expand_protect_phase:


        # Choose focus region for expansion
        focus_super_region = super_region_data_list[0]
        for super_region_data in super_region_data_list:
          #Check if super region is under occupation by us
          if super_region_data.phase == 3:
            #check if the current focus region is under occupation by us
            if focus_super_region.phase == 2:
              focus_super_region = super_region_data
            elif focus_super_region ==  3:
              # Check which super region has most troops
              if focus_super_region.owned_troops < super_region_data.owned_troops:
                focus_super_region = super_region_data 
              # Check if the value of super region is generally more interesting than the current focus
              if super_region_importance[focus_super_region.id] < super_region_importance[super_region_data.id]:
                pass

          elif super_region_data.phase == 2 and focus_super_region == 2:

            if super_region_importance[focus_super_region.id] < super_region_importance[super_region_data.id]:
              focus_super_region = super_region_data



        # Dividing super regions into protect or expand strategy
        # Protection is found first because the expansion is factored by the amount of expansion
        for super_region_data in super_region_data_list:
          # If super region is owned then protect
          if super_region_data.owned_regions == super_region_data.total_regions:
            #immediate_thread_rate = (super_region_data.neighbour_enemy_troops - (super_region_data.owned_troops / 2)) / super_region_data.total_troops * 10
            if super_region_data.neighbour_enemy_troops > 0 and super_region_data.neighbour_enemy_troops < 4:
              super_region_data.value = 5
              protection_level += 5
            if super_region_data.neighbour_enemy_troops > 4:
              super_region_data.value = 10
              protection_level += 10

        if protection_level > 10:
          protection_level = 10  
       
'''
        for super_region_data in super_region_data_list:
       
          # If super region is not owned at all and is neighbouring owned territory.
          # Then the super region is in interest.
          if super_region_data.owned_regions == 0:
            if super_region_data.neighbour_owned_regions > 0:
              enemy_occupation_rate = 10 - super_region_data.enemy_regions / super_region_data.total_regions * 10
              
              pass #Not implemented


          # If super region is not completly owned. Then the super region is under occupation
          if super_region_data.owned_regions > 0:
            pass #Not imlemented
'''
        
        focus_super_region.value = 10 - protection_level
        for super_region_data in super_region_data_list:
          super_regions.append((super_region.id, super_region_value))


      return {
        'continents': super_regions
      }

    def attack_transfer(self, info, input):
      pass

class SuperRegionData(object):
  def __init__(self):
    self.id = 0

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

    self.total_regions = 0
    self.total_troops = 0
    self.total_neighbour_regoins = 0

    self.importance = 0
    self.value = 0
    # Four phases, 1 Occupied, 2 In interest, 3 Occupation in progress, 4 Out of reach
    self.phase = 0

