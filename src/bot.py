#---------------------------------------------------------------------#
# Warlight AI Challenge - Starter Bot                                 #
# ============                                                        #
#                                                                     #
# Last update: 20 Mar, 2014                                           #
#                                                                     #
# @author Jackie <jackie@starapple.nl>                                #
# @version 1.0                                                        #
# @license MIT License (http://opensource.org/licenses/MIT)           #
#---------------------------------------------------------------------#

from StrategyLayer import StrategyLayer
from TacticsLayer import TacticsLayer
from MicroLayer import MicroLayer

from util import Map, Region, SuperRegion

from math import fmod, pi
from sys import stderr, stdin, stdout
from time import clock
from json import loads
import pprint

pp = pprint.PrettyPrinter(indent=2,stream=stderr)



class Bot(object):
    '''
    Main bot class
    '''
    def __init__(self, *layers):
        '''
        Initializes a map instance and an empty dict for settings, as well as a list of AI layers
        '''
        self.settings = {}
        self.map = Map()
        self.layers = layers
        self.n = len(layers)
        self.round_number = 1

    def run(self):
        '''
        Main loop

        Keeps running while being fed data from stdin.
        Writes output to stdout, remember to flush!
        '''
        while not stdin.closed:
            try:
                rawline = stdin.readline()

                # End of file check
                if len(rawline) == 0:
                    break

                line = rawline.strip()

                # Empty lines can be ignored
                if len(line) == 0:
                    continue

                parts = line.split()

                command = parts[0]

                # All different commands besides the opponents' moves
                if command == 'settings':
                    self.update_settings(parts[1:])

                elif command == 'setup_map':
                    self.setup_map(parts[1:])

                elif command == 'update_map':
                    self.update_map(parts[1:])

                elif command == 'pick_starting_regions':
                    stdout.write(self.pick_starting_regions(parts[1], parts[2:]) + '\n')
                    stdout.flush()

                elif command == 'go':

                    sub_command = parts[1]

                    if sub_command == 'place_armies':

                        stdout.write(self.place_armies(parts[2]) + '\n')
                        stdout.flush()

                    elif sub_command == 'attack/transfer':

                        stdout.write(self.attack_transfer(parts[2]) + '\n')
                        stdout.flush()

                    else:
                        stderr.write('Unknown sub command: %s\n' % (sub_command))
                        stderr.flush()

                elif command == 'opponent_moves':
                    pass

                else:
                    stderr.write('Unknown command: %s\n' % (command))
                    stderr.flush()
            except EOFError:
                return

    def update_settings(self, options):
        '''
        Method to update game settings at the start of a new game.
        '''
        key, value = options
        self.settings[key] = value

    def setup_map(self, options):
        '''
        Method to set up essential map data given by the server.
        '''
        map_type = options[0]

        for i in range(1, len(options), 2):

            if map_type == 'super_regions':

                super_region_id = options[i]
                super_region_worth = int(options[i + 1])

                super_region = SuperRegion(super_region_id, super_region_worth)
                self.map.super_regions.append(super_region)

            elif map_type == 'regions':

                region_id = options[i]
                super_region_id = options[i + 1]

                super_region = self.map.get_super_region_by_id(super_region_id)
                region = Region(region_id, super_region)

                self.map.regions.append(region)
                super_region.regions.append(region)

            elif map_type == 'neighbors':

                region_id = options[i]
                neighbour_list = options[i+1]

                region = self.map.get_region_by_id(region_id)
                neighbours = [self.map.get_region_by_id(region_id) for region_id in neighbour_list.split(',')]

                for neighbour in neighbours:
                    region.neighbours.append(neighbour)
                    neighbour.neighbours.append(region)

        if map_type == 'neighbors':

            for region in self.map.regions:

                if region.is_on_super_region_border:
                    continue

                for neighbour in region.neighbours:

                    if neighbour.super_region.id != region.super_region.id:

                        region.is_on_super_region_border = True
                        neighbour.is_on_super_region_border = True

    def update_map(self, options):
        '''
        Method to update our map every round.
        '''
        stderr.write('Round '+str(self.round_number)+'\n\n')
        for region in self.map.regions:
            region.is_fog = True

        for i in range(0, len(options), 3):
            region_id = options[i]
            region_owner_id = options[i + 1]
            region_troop_count = int(options[i + 2])

            region = self.map.get_region_by_id(region_id)
            region.owner = region_owner_id
            region.troop_count = region_troop_count
            region.is_fog = False
        self.round_number += 1

    def pick_starting_regions(self, time, regions):
        '''
        Method to select our initial starting regions.

        '''

        info = dict()
        info['world'] = self.map
        info['your_bot'] = self.settings['your_bot']
        info['regions'] = regions
        info['time'] = int(time) * 1.0 / self.n

        result = self.call_layers('pick_starting_regions','picked_regions', info)

        if result.has_key('picked_regions'):
            picked_regions = result['picked_regions']
            output = ' '.join(picked_regions)
            stderr.write('picked_regions: '+output+'\n')
            return output
        else:
            return ''

    def place_armies(self, time):
        '''
        Method to place our troops.

        '''

        your_bot = self.settings['your_bot']

        info = dict()
        info['world'] = self.map
        info['your_bot'] = self.settings['your_bot']
        info['starting_armies'] = int(self.settings['starting_armies'])
        info['time'] = int(time) * 1.0 /self.n

        result = self.call_layers('place_armies', 'placements', info)

        if result.has_key('placements'):
            placements = result['placements']
            output = ', '.join(['%s place_armies %s %d' % (your_bot, placement[0],
            placement[1]) for placement in placements])
            stderr.write('placements: '+ output+'\n')
            return output
        else:
            return ''

    def attack_transfer(self, time):
        '''
        Method to attack another region or transfer troops to allied regions.

        '''

        your_bot = self.settings['your_bot']

        info = dict()
        info['world'] = self.map
        info['your_bot'] = self.settings['your_bot']
        info['time'] = int(time) * 1.0 / self.n

        result = self.call_layers('attack_transfer', 'attack_transfers', info)

        if result.has_key('attack_transfers'):
            attack_transfers = result['attack_transfers']
            output = ', '.join(['%s attack/transfer %s %s %s' % (your_bot, attack_transfer[0],
            attack_transfer[1], attack_transfer[2]) for attack_transfer in attack_transfers])
            stderr.write('attack_transfers: '+output+'\n')
            return output
        else:
            return ''

    def call_layers(self, action_name, required_output, info):
        inp_command_dict = dict()
        out_command_dict = dict()
        n = len(self.layers)
        for i, layer in enumerate(self.layers):
            method = getattr(layer, action_name)
            out_command_dict = method(info, inp_command_dict) or {}
            stderr.write('method '+action_name+', '+['Strategy', 'Tactics', 'Micro'][i]+'Layer')
            if out_command_dict:
                # if layer gave output, give it as input to the next layer
                inp_command_dict = out_command_dict
                pp.pprint(out_command_dict)
                stderr.write('\n')
            else:
                # else do nothing, the input layer continues to the next layer
                stderr.write('Empty return value from layer, skipping.\n')

            # if an earlier layer takes the decision, return immediately
            if out_command_dict.has_key(required_output):
                return out_command_dict

        # return the last output as the final command
        return out_command_dict


if __name__ == '__main__':
    '''
    Not used as module, so run
    '''
    Bot(StrategyLayer(), TacticsLayer(), MicroLayer()).run()