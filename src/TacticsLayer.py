from BotLayer import BotLayer

from util import Map, Region, SuperRegion, Random

class TacticsLayer(BotLayer):

  def __init__(self):
    pass

  def pick_starting_regions(self, info, input):
    pass

  def place_troops(self, info, input):
    continent_id = 1 # continent with highest priority
    
    map       = info['world']
    continent = map.get_super_region_by_id(continent_id)

    inp = []

    for continent in input['continents']:
      continent_id = continent[0]
      for region in continent.regions:
        # ATTACK: check ADJACENT regions not owned in given continent
        if region.owner == 'neutral':
          inp.append( (region.id, 5, 'attack') )
      
        elif region.owner == 'oppenent':
          inp.append( (region.id, 10, 'attack') )

        else:
          # DEFEND: check frontal regions
          for r in region.neighbours:
            if r.owner == 'opponent':
              inp.append( (region, 3, 'defend') )
    
      return inp

  def attack_transfer(self, info, input):
    if info.has_key('cmd_for_lower_layer'):
      return {
	'you_decide': False,
	'troops': [3,4,5]
      }
    else:
      return {'you_decide': True}
