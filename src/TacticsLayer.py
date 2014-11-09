from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random, get_other_player

class TacticsLayer(BotLayer):

  def __init__(self):
    self.opponent = None
    self.our_player = None

  def pick_starting_regions(self, info, input):
    pass

  def place_armies(self, info, input):
    self.our_player = info['your_bot']
    self.opponent = get_other_player(self.our_player)

    continents = input['continents']


    map = info['world']

    inp = []

    # iterate through continents in the list
    for continent_tuple in continents:

      continent_id = continent_tuple[0]
      continent    = map.get_super_region_by_id(continent_id)

      for region in continent.regions:
        if region.is_fog:
          continue

        # ATTACK: check ADJACENT regions not owned in given continent
        if region.owner == 'neutral':
          inp.append( (region.id, 5, 'attack') )

        
        elif region.owner == self.opponent:
          inp.append( (region.id, 10, 'attack') )

        else:
          # DEFEND: check border regions
          if self.border(region):
              inp.append( (region, 3, 'defend') )

    return {'regions' : inp}


  def attack_transfer(self, info, input):
    pass

  #############################################################

  def border(self, region):
    for r in region.neighbours:
      if r.owner == self.opponent:
        return True

    return False
