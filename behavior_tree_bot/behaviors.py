import sys

sys.path.insert(0, '../')
from planet_wars import issue_order
import logging


# attack strategy methods:

def attack(state):
    def strength(p):
        return p.num_ships \
            + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
            - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    if not enemy_planets:
        return False

    target_planets = iter(sorted(enemy_planets, key=lambda p: p.num_ships))
    target_planet = next(target_planets)

    # only select planets that have not targeted
    my_planets = [planet for planet in state.my_planets() if strength(planet) > 0]
    if not my_planets:
        return False

    my_planets = iter(sorted(my_planets, key=lambda p: state.distance(target_planet.ID, p.ID)))
    my_planet = next(my_planets)

    try:
        while True:
            required_ships = target_planet.num_ships + \
                             state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return False


# Weaken enemy planets (iterate on attack weakest)

def attack_weakest(state):
    def strength(p):
        return p.num_ships \
            + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
            - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    def enemy_strength(p):
        return p.num_ships \
            - sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
            + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    my_planets = [planet for planet in state.my_planets() if strength(planet) > 0]
    strongest_planet = max(my_planets, key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=enemy_strength)

    if not strongest_planet or not weakest_planet:
        return False

    ships_required = strongest_planet.num_ships / 2
    return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_required)


'''def reinforce_attack(state):
    # (1) If we currently don't have a fleet in flight, abort plan.
    if len(state.my_fleets()) < 1:
        return False

    # (2) If the enemy currently doesn't have a fleet in flight, abort plan.
    if len(state.enemy_fleets()) < 1:
        return False

    target_planet = None
    for my_ship in state.my_fleets():
        for enemy_ship in state.enemy_fleets():
            if my_ship.destination_planet is enemy_ship.destination_planet:
                target_planet = my_ship.destination_planet

    if not target_planet:
        return False

    logging.info('\n' + "reinforcements identified target planet")
    def strength(p):
        return p.num_ships \
            + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
            - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    def enemy_strength(p):
        return p.num_ships \
            - sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
            + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    # only select planets that have not targeted
    my_planets = [planet for planet in state.my_planets() if strength(planet) > 0]
    if not my_planets:
        return False

    logging.info('\n' + "reinforcements available planets")

    my_planets = iter(sorted(my_planets, key=lambda p: state.distance(target_planet, p.ID)))
    my_planet = next(my_planets)

    get_planet = {planet.ID: planet for planet in [*state.my_planets(), *state.enemy_planets(), *state.neutral_planets()]}
    planet = get_planet[target_planet]

    try:
        while True:
            logging.info('\n' + "reinforcements going through try loop")
            required_ships = enemy_strength(planet) + enemy_ship.turns_remaining * planet.growth_rate + 1

            if my_planet.num_ships > required_ships > 0:
                logging.info('\n' + "reinforcements returning order")
                return issue_order(state, my_planet.ID, target_planet, required_ships)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        logging.info('\n' + "reinforcements false")
        return False'''


# spread stuff
def spread_to_lowcost(state):
    def check_strength(s):
        return s.num_ships \
            + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == s.ID) \
            - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == s.ID)

    def check_neutral_strength(s):
        return s.num_ships \
            - sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == s.ID) \
            + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == s.ID)

    neutral_planets = [planet for planet in state.neutral_planets() if check_neutral_strength(planet) > 0]
    if not neutral_planets:
        return False

    # check targets
    targets = [fleet.destination_planet for fleet in state.enemy_fleets()]
    my_fleet = [planet for planet in state.my_planets() if planet.ID not in targets]

    if not my_fleet:
        return False

    attack_ship = max(my_fleet, key=check_strength)

    target = min(neutral_planets, key=lambda x: (check_neutral_strength(x) * state.distance(attack_ship.ID, x.ID)))

    req = check_neutral_strength(target) + 1

    if attack_ship.num_ships > req:
        return issue_order(state, attack_ship.ID, target.ID, req)
    else:
        return False

    # defensive strategy methods:


def backup(state):
    def check_strength(s):
        return s.num_ships \
            + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == s.ID) \
            - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == s.ID) \
            + min(fleet.turns_remaining for fleet in state.enemy_fleets() if
                  fleet.destination_planet == s.ID) * s.growth_rate

    def get_dist(planet):
        return state.distance(planet.ID, need_backUp.ID)

    targets = [planets.destination_planet for planets in state.enemy_fleets()]

    backup_planets = []
    for planet in state.my_planets():
        if planet.ID in targets:
            if check_strength(planet) <= 0:
                backup_planets.append(planet)
    if not backup_planets:
        return False

    need_backUp = min(backup_planets, key=check_strength)
    en = max((planet for planet in state.enemy_fleets() if planet.destination_planet == need_backUp.ID),
             key=lambda x: x.num_ships)

    attack_ships = state.my_planets()
    attack_ships.remove(need_backUp)
    attack_ships = iter(sorted(attack_ships, key=get_dist))

    try:
        cur_unit = next(attack_ships)
        while True:
            req = 1 - check_strength(need_backUp)
            if req <= 0:
                return False

            if cur_unit.num_ships > req:
                return issue_order(state, cur_unit.ID, need_backUp.ID, req)
            else:
                cur_unit = next(attack_ships)
    except StopIteration:
        return False
