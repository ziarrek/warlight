# get other players name, assumes two constant name: player1, player2

def get_super_region_name(id):
  if   id == '1': return 'North America'
  elif id == '2': return 'South America'
  elif id == '3': return 'Europe'
  elif id == '4': return 'Africa'
  elif id == '5': return 'Asia'
  elif id == '6': return 'Australia'

def get_region_name(id):
  if   id == '1': return 'Alaska'
  elif id == '2': return 'Northwest Territory'
  elif id == '3': return 'Greenland'
  elif id == '4': return 'Alberta'
  elif id == '5': return 'Ontario'
  elif id == '6': return 'Quebec'
  elif id == '7': return 'Western United States'
  elif id == '8': return 'Eastern United States'
  elif id == '9': return 'Central America'
  elif id == '10': return 'Venezuela'
  elif id == '11': return 'Peru'
  elif id == '12': return 'Brazil'
  elif id == '13': return 'Argentina'
  elif id == '14': return 'Iceland'
  elif id == '15': return 'Great Britain'
  elif id == '16': return 'Scandinavia'
  elif id == '17': return 'Ukraine'
  elif id == '18': return 'Western Europe'
  elif id == '19': return 'Northern Europe'
  elif id == '20': return 'Southern Europe'
  elif id == '21': return 'North Africa'
  elif id == '22': return 'Egypt'
  elif id == '23': return 'East Africa'
  elif id == '24': return 'Congo'
  elif id == '25': return 'South Africa'
  elif id == '26': return 'Madagascar'
  elif id == '27': return 'Ural'
  elif id == '28': return 'Siberia'
  elif id == '29': return 'Yakutsk'
  elif id == '30': return 'Kamchatka'
  elif id == '31': return 'Irkutsk'
  elif id == '32': return 'Kazakhstan'
  elif id == '33': return 'China'
  elif id == '34': return 'Mongolia'
  elif id == '35': return 'Japan'
  elif id == '36': return 'Middle East'
  elif id == '37': return 'India'
  elif id == '38': return 'Siam'
  elif id == '39': return 'Indonesia'
  elif id == '40': return 'New Guinea'
  elif id == '41': return 'Western Australia'
  elif id == '42': return 'Eastern Australia'

def format_region(id):
  return get_region_name(id)+'('+str(id)+')'

def format_super_region(id):
  return get_super_region_name(id)+'('+str(id)+')'

def format_move(source, target, troop_count):
  return 'Move '+str(troop_count)+' troops from '+format_region(source)+' to '+format_region(target)

def format_placement(region_id, troop_count):
  return 'Place '+str(troop_count)+' troops on '+format_region(region_id)

def get_other_player(player_name):
    return 'player2' if player_name == 'player1' else 'player1'

class Map(object):
    '''
    Map class
    '''
    def __init__(self):
        '''
        Initializes empty lists for regions and super regions.
        '''
        self.regions = []
        self.super_regions = []

    def get_region_by_id(self, region_id):
        '''
        Returns a region instance by id.
        '''
        return [region for region in self.regions if region.id == region_id][0]

    def get_super_region_by_id(self, super_region_id):
        '''
        Returns a super region instance by id.
        '''
        return [super_region for super_region in self.super_regions if super_region.id == super_region_id][0]

    def get_owned_regions(self, owner):
        '''
        Returns a list of region instances owned by `owner`.
        '''
        return [region for region in self.regions if region.owner == owner]

class SuperRegion(object):
    '''
    Super Region class
    '''
    def __init__(self, super_region_id, worth):
        '''
        Initializes with an id, the super region's worth and an empty lists for
        regions located inside this super region
        '''
        self.id = super_region_id
        self.worth = worth
        self.regions = []

class Region(object):
    '''
    Region class
    '''
    def __init__(self, region_id, super_region):
        '''
        '''
        self.id = region_id
        self.owner = 'fog'
        self.neighbours = []
        self.troop_count = 2
        self.super_region = super_region
        self.is_on_super_region_border = False
        self.is_fog = True

class Random(object):
    '''
    Random class
    '''
    @staticmethod
    def randrange(min, max):
        '''
        A pseudo random number generator to replace random.randrange

        Works with an inclusive left bound and exclusive right bound.
        E.g. Random.randrange(0, 5) in [0, 1, 2, 3, 4] is always true
        '''
        return min + int(fmod(pow(clock() + pi, 2), 1.0) * (max - min))

    @staticmethod
    def shuffle(items):
        '''
        Method to shuffle a list of items
        '''
        i = len(items)
        while i > 1:
            i -= 1
            j = Random.randrange(0, i)
            items[j], items[i] = items[i], items[j]
        return items
