from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random, get_other_player, get_super_region_name, get_region_name, format_region

from sys import stderr

class TacticsLayer(BotLayer):

  def __init__(self):
    self.opponent = None
    self.our_player = None
    self.map = None
    self.round = 1
    self.behaviour = "defensive"
    self.owned_regions = 3
    self.def_mult = 3
    self.att_mult = 5
    self.threshold = 0.4

  def pick_starting_regions(self, info, input):
    pass

  def place_armies(self, info, input):
    self.map = info['world']
    self.our_player = info['your_bot']
    self.opponent = get_other_player(self.our_player)



    continents = sorted(input['continents'], key=lambda x:x[1],reverse=True)

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

    new_continent_attack = False

    for continent_tuple in continents:

      continent_id = continent_tuple[0]
      value        = continent_tuple[1]
      continent    = self.map.get_super_region_by_id(continent_id)

     ### CHECK INVADE #######################
      if value == 0:                         #
        for region in continent.regions:
          if self.invade(region):
            inp.append( ( region.id, 10, 'attack') )
            stderr.write("Invade " + format_region(region.id) + "\n")
       

      threshold = float(self.get_number_owned_regions(continent)) / float(len(continent.regions))
      stderr.write(get_super_region_name(continent_id) + ": " + str(value) + " - " + str(threshold) + "\n")
      ## Do not attack two NEWish continents in the same round
      if self.get_number_owned_regions(continent) == 0:
        if new_continent_attack:
          stderr.write("Skipping\n");
          continue
        else:
          stderr.write("Setting new continent attack to false\n")
          new_continent_attack = True
      ## set continent as new if just started to attack it
      if threshold < self.threshold:
        stderr.write("Setting new continent attack to false\n")
        new_continent_attack = True
      
      for region in continent.regions:
        if region.is_fog:
          continue

        # ATTACK: check ADJACENT regions not owned in given continent
        priority = value * self.attack_value_multiplier(region)

        if region.owner == 'neutral':
          inp.append( (region.id, priority, 'attack') )
          stderr.write("\tAttack: " + format_region(region.id) + " " + str(priority) + "\n")

        elif region.owner == self.opponent:
#          def_troops = region.troop_count
#          att_troops = self.get_max_attacking_troops(region)
#          if att_troops > def_troops:
#            priority *= 2
#            stderr.write("attmult: ")
          inp.append( (region.id, priority, 'attack') )
          stderr.write("\tAttack: " + format_region(region.id) +  " " + str(priority) + "\n")

        else:
          # DEFEND: check border regions
          if self.border(region):
            if self.in_danger(region):
              priority = value * self.defend_value_multiplier(region)
              inp.append( (region.id, priority, 'defend') )
            else:
              inp.append( (region.id, 0, 'defend') )
            stderr.write("\tDefend: " + format_region(region.id) +  " " + str(priority) + "\n")

      stderr.write("\n")

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
    # limit exposure
    confining = 0
    for r in region.neighbours:
      if r.owner == self.our_player:
        confining +=1

    if confining == 0:
      confining = 1

    mult = 1
    # prefer attacking the enemy over netural regions
    if region.owner == self.opponent:
      mult = self.att_mult

    return mult * confining

  # Give added value to the region defense if the region is on the super_region border
  # and we own more than half the regions in the continent to defend
  def defend_value_multiplier(self, region):
    super_region = region.super_region
    owned_regions = float(self.get_number_owned_regions(super_region))
    tot_regions = float(len(super_region.regions))
    percentage = owned_regions / tot_regions

    stderr.write("defend mult: " + get_region_name(region.id) + ": " + str(owned_regions) + "/" + str(tot_regions) + " = " + str(percentage))
#    if percentage > 0.5:
#      stderr.write("applying defend mult")
#      return 2

    return percentage*self.def_mult


  def get_number_owned_regions(self, super_region):
    sum = 0
    for region in super_region.regions:
      if region.owner == self.our_player:
        sum +=1
    return sum

  def get_owned_regions(self):
    cnt = 0
    for region in self.map.regions:
      if region.owner == self.our_player:
        cnt += 1
    return cnt

  def in_danger(self, region):
    troops = region.troop_count
    for r in region.neighbours:
      if r.troop_count > troops:
        return True
    return False

  def we_have_regions(self, super_region):
    for region in super_region.regions:
      if not region.is_fog and region.owner == self.our_player:
        return True
    return False

  def invade(self, region):
    super_region = region.super_region

    if region.is_fog or region.owner != self.opponent or not region.is_on_super_region_border or self.we_have_regions(super_region):
      return False

    troops = region.troop_count
    our_max_troops = 0

    for r in region.neighbours:
      if r.is_fog or r.owner != self.our_player or r.super_region == super_region:
        continue
      # starting by being conservative
      if r.troop_count < troops:
        return False
      elif r.troop_count > our_max_troops:
        our_max_troops = r.troop_count

    return True


  def get_max_attacking_troops(self, region):
    troops = 0
    for r in region.neighbours:
      if not r.is_fog and r.owner == self.our_player:
        troops += (r.troop_count - 1)
    return troops

