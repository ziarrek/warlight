from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random
from sys import stderr, stdout

class StrategyLayer(BotLayer):

    def __init__(self):
      self.super_region_data_list = []
      self.data_init = False
      self.initial_phase = True
      self.expand_protect_phase = False
      self.super_region_importance = [1, 0, 2, 1, -1, 0]

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

      stderr.write('picked_regions: '+' '.join(chosen_regions)+'\n\n')
      return {'picked_regions': chosen_regions}

    def place_armies(self, info, input):
      world = info['world']
      your_bot = info['your_bot']
      super_regions = []
      i = 0

      # Retriving information form the super regions
      for super_region in world.super_regions:

        super_region_data = SuperRegionData()
        if not self.data_init:
          self.super_region_data_list.append(super_region_data)
          super_region_data.id = super_region.id
        else:
          super_region_data = self.super_region_data_list[i]
          i += 1

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
          if neighbour.owner == 'neutral':
            neighbour_neutral_regions += 1
          elif neighbour.owner == your_bot:
            neighbour_owned_troops += neighbour.troop_count
            neighbour_owned_regions += 1
          else:
            neighbour_enemy_troops += neighbour.troop_count
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
        super_region_data.total_regions = total_regions
        super_region_data.total_troops = total_troops
        super_region_data.total_neighbour_regions = total_neighbour_regions
        

        if total_troops != 0:

          immediate_threat_rate = (neighbour_enemy_troops - (owned_troops / 2)) / total_troops * 10
          
          own_occupation_rate = owned_regions / total_regions * 10
          
          enemy_occupation_rate = enemy_regions / total_regions * 10
          
          super_region_value = (immediate_threat_rate + own_occupation_rate) / 2 - (enemy_occupation_rate / 2)
        else:
          super_region_value = 0

      #Ensures old data can stay (when implemented)
      self.data_init = True

      #Check if initial phase is done
      self.expand_protect_phase = False
      for super_region_data in self.super_region_data_list:
        if super_region_data.owned_regions == super_region_data.total_regions:
          self.initial_phase = False
          self.expand_protect_phase = True

      # Set phases for super regions 
      for super_region_data in self.super_region_data_list:
        super_region_data.value = 0
        if super_region_data.owned_regions > 0:
          super_region_data.phase = 3
        elif super_region_data.neighbour_owned_regions > 0:
          super_region_data.phase = 2
        elif super_region_data.owned_regions == super_region_data.total_regions:

          super_region_data.phase = 1
        else:
          super_region_data.phase = 4

      # PHASE Initial
      if self.initial_phase:
        focus_super_region = self.super_region_data_list[0]
        current_best_occupaction = 0
        for super_region_data in self.super_region_data_list:
          if current_best_occupaction < super_region_data.owned_regions:
            #stderr.write()
            focus_super_region = super_region_data
            current_best_occupaction = super_region_data.owned_regions
          if current_best_occupaction == super_region_data.owned_regions:
            if self.super_region_importance[int(float(focus_super_region.id))-1] < self.super_region_importance[int(float(super_region_data.id))-1]:
              focus_super_region = super_region_data
            
            #NOT IMPLEMENTED: Choose based on the list of preference and enemy occupation
          if super_region_data.owned_troops > 0:
            super_region_data.value = 2

        focus_super_region.value = 10 

      #PHASE expand and protect
      protection_level = 0
      if self.expand_protect_phase:

        # Choose focus region for expansion
        focus_super_region = self.super_region_data_list[0]
        for super_region_data in self.super_region_data_list:
          #Check if super region is under occupation by us
          if super_region_data.owned_regions != super_region_data.total_regions:
            if super_region_data.phase == 3:
              #check if the current focus region is under occupation by us
              if focus_super_region.phase == 2 or focus_super_region.phase == 4 or focus_super_region.phase == 1:
                focus_super_region = super_region_data
              elif focus_super_region.phase ==  3:
                # Check which super region has most troops
                if focus_super_region.owned_troops < super_region_data.owned_troops:
                  focus_super_region = super_region_data 
                # Check if the value of super region is generally more interesting than the current focus
                elif focus_super_region.owned_troops == super_region_data.owned_troops:
                  #stderr.write('\n id: ' +focus_super_region.id + ' val: ' + str(super_region_importance[int(float(focus_super_region.id))-1]) + ' | id: '+ str(super_region_data.id) + ' val: ' + str(self.super_region_importance[int(float(super_region_data.id))-1]))
                  if self.super_region_importance[int(float(focus_super_region.id))-1] < self.super_region_importance[int(float(super_region_data.id))-1]:
                    focus_super_region = super_region_data
            elif super_region_data.phase == 2:
              if focus_super_region.phase == 2:
                if self.super_region_importance[int(float(focus_super_region.id))-1] < self.super_region_importance[int(float(super_region_data.id))-1]:
                  focus_super_region = super_region_data
                elif focus_super_region.neighbour_owned_regions == 0 and super_region_data.neighbour_owned_regions > 0:
                  focus_super_region = super_region_data



        # Dividing super regions into protect or expand strategy
        # Protection is found first because the expansion is factored by the amount of expansion
        for super_region_data in self.super_region_data_list:
          # If super region is owned then protect
          if super_region_data.owned_regions == super_region_data.total_regions:
            #immediate_threat_rate = (super_region_data.neighbour_enemy_troops - (super_region_data.owned_troops / 2)) / super_region_data.total_troops * 10
            if super_region_data.neighbour_enemy_troops > 0 and super_region_data.neighbour_enemy_troops < 4:
              stderr.write('Defending')
              super_region_data.value = 5
              protection_level += 5
            if super_region_data.neighbour_enemy_troops > 4:
              stderr.write('Defending')
              super_region_data.value = 10
              protection_level += 10

        if protection_level > 10:
          protection_level = 10  
       
        '''
        for super_region_data in self.super_region_data_list:
       
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
        if focus_super_region.value <= 0:
          focus_super_region.value = 1

      
      stderr.write('continents_output: Init: '+ str(self.initial_phase) + ' '+ str(self.expand_protect_phase)+ '\n')
      for super_region_data in self.super_region_data_list:
        stderr.write('id: '+str(super_region_data.id))
        if super_region_data.value < 10:
          stderr.write(' val: 0'+str(super_region_data.value))
        else:
          stderr.write(' val: '+str(super_region_data.value))
        stderr.write(' phase: '+str(super_region_data.phase))
        if super_region_data.owned_troops < 10:
          stderr.write(' troops: 0'+str(super_region_data.owned_troops))
        else:
          stderr.write(' troops: '+str(super_region_data.owned_troops))

        if super_region_data.owned_regions < 10:
          stderr.write(' owned_region: 0'+str(super_region_data.owned_regions))
        else:
          stderr.write(' owned_region: '+str(super_region_data.owned_regions))

        if super_region_data.total_regions < 10:
          stderr.write(' total_regions: 0'+str(super_region_data.total_regions))
        else:
          stderr.write(' total_regions: '+str(super_region_data.total_regions))

        if super_region_data.neighbour_owned_troops < 10:
          stderr.write(' neigh_troops: 0'+str(super_region_data.neighbour_owned_troops))
        else:
          stderr.write(' neigh_troops: '+str(super_region_data.neighbour_owned_troops))

        if super_region_data.neighbour_owned_troops < 10:
          stderr.write(' neigh_enemy: 0'+str(super_region_data.neighbour_enemy_troops))
        else:
          stderr.write(' neigh_enemy: '+str(super_region_data.neighbour_enemy_troops))

        stderr.write('\n')
      stderr.write('\n\n')
      stderr.flush()
      

      for super_region_data in self.super_region_data_list:
        super_regions.append((super_region_data.id, super_region_data.value))

      

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
    self.total_neighbour_regions = 0

    self.importance = 0
    self.value = 0
    # Four phases, 1 Occupied, 2 In interest, 3 Occupation in progress, 4 Out of reach
    self.phase = 0

