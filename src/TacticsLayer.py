from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random, get_other_player, get_super_region_name, get_region_name

from sys import stderr

class TacticsLayer(BotLayer):

  def __init__(self):
    self.opponent = None
    self.our_player = None
    self.map = None
    self.round = 1

  def pick_starting_regions(self, info, input):
    pass

  def place_armies(self, info, input):
    self.our_player = info['your_bot']
    self.opponent = get_other_player(self.our_player)

    continents = sorted(input['continents'], key=lambda x:x[1],reverse=True)

    self.map = info['world']
    #continents = sorted(self.getSuperRegions(), key=lambda x:x[1],reverse=True)

    # check for all zeros
#    deadlocks = 0
#
#    for c in continents:
#      continent = self.map.get_super_region_by_id(c[0])
#      if self.get_number_owned_regions(continent) == len(continent.regions) or c[1] == 0:
#        deadlocks += 1
#
#    
#    if deadlocks == len(continents):
#      conts = []
#      for c in continents:
#        if c[1] == 0:
#          conts.append((c[0], 1))
#        else:
#          conts.append((c[0],c[1]))
#      continents = conts
#
    inp = []

    stderr.write('\nRound ' + str(self.round) + '\n')
    self.round += 1
    # iterate through continents in the list

    for continent_tuple in continents:
      
      continent_id = continent_tuple[0]
      value        = continent_tuple[1]
      continent    = self.map.get_super_region_by_id(continent_id)
      
      
      stderr.write(get_super_region_name(continent_id) + ": " + str(value) + "\n")

      if value == 0:
        continue

      for region in continent.regions:
        if region.is_fog:
          continue

        # ATTACK: check ADJACENT regions not owned in given continent
        priority = value * self.attack_value_multiplier(region)

        if region.owner == 'neutral':
          inp.append( (region.id, priority, 'attack') )
#          stderr.write("\tAttack: " + get_region_name(region.id) + " " + str(priority) + "\n")


        elif region.owner == self.opponent:
          inp.append( (region.id, priority, 'attack') )
 #         stderr.write("\tAttack: " + get_region_name(region.id) +  " " + str(priority) + "\n")

        else:
          # DEFEND: check border regions
          if self.border(region):
            priority = value * self.defend_value_multiplier(region)
            inp.append( (region.id, value, 'defend') )
 #           stderr.write("\tDefend: " + get_region_name(region.id) +  " " + str(value) + "\n")

#      stderr.write("\n")

    return {'regions' : inp}


  def attack_transfer(self, info, input):
    pass

  #############################################################

  def border(self, region):
    for r in region.neighbours:
      if r.owner == self.opponent:
        return True

    return False

  def attack_value_multiplier(self, region):
    confining = 0

    for r in region.neighbours:
      if r.owner == self.our_player:
        confining +=1

    if confining > 0:
      return confining
    else:
      return 1

  def defend_value_multiplier(self, region):
    if not region.is_on_super_region_border:
      return 1

    super_region = region.super_region
    if float(self.get_number_owned_regions(super_region)) / float(len(super_region.regions)) > 0.5:
      return 2

    return 1

  def get_number_owned_regions(self, super_region):
    sum = 0
    for region in super_region.regions:
      if region.owner == self.our_player:
        sum +=1
    return sum
