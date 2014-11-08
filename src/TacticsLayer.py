from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random

class TacticsLayer(BotLayer):

  def __init__(self):
    pass

  def pick_starting_regions(self, info, input):
    pass

  def place_troops(self, info, input):

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
      
        elif region.owner == 'opponent':
          inp.append( (region.id, 10, 'attack') )

        else:
          # DEFEND: check border regions
          if border(region):
              inp.append( (region, 3, 'defend') )
    
      return {'regions' : inp}

  
  def attack_transfer(self, info, input):
    pass

  #############################################################

  def border(self, region):
    if not region.is_on_super_region_border:
      return False

    for r in region.neighbours:
      if r.owner == 'opponent':
        return True

    return False
