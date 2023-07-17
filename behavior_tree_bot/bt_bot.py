#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect

logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():
    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    # Attack Sequence
    Attack_sequence = Selector(name='Attack Strategy')
    attack_plan = Sequence(name='Attacking')
    attack_check = Check(check_win)
    attack_action = Action(attack)
    attack_plan.child_nodes = [attack_check, attack_action]

    weakening_sequence = Sequence(name="Weaken_Enemy_Strategy")
    weakening_check = Check(is_enemy)
    weakening_action = Action(attack_weakest)
    weakening_sequence.child_nodes = [weakening_check, weakening_action]

    Attack_sequence.child_nodes = [attack_plan, weakening_sequence]

    # Spread Plan
    spread_plan = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(is_neutral)
    spread_action = Action(spread_to_lowcost)
    spread_plan.child_nodes = [neutral_planet_check, spread_action]

    # Potential defensive plan
    defensive_plan = Sequence(name='Defensive Strategy')
    defend_check = Check(check_backup_needed)
    defend_action = Action(backup)
    defensive_plan.child_nodes = [defend_check, defend_action]

    root.child_nodes = [defensive_plan, Attack_sequence, spread_plan]

    logging.info('\n' + root.tree_to_string())
    return root


# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)


if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")