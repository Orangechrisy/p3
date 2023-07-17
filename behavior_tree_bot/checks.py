import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)


# check if we can win
def check_win(state):
    attacker = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    weakest = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
    # exit if there are no planets
    if attacker is None or weakest is None:
        return False
    # check if we can win if we can this will return true
    return attacker.num_ships > weakest.num_ships


# check if we need to send backup
def check_backup_needed(state):
    # get all enemy planets
    en = [fleet.destination_planet for fleet in state.enemy_fleets()]
    if not en:
        return False

    # check how strong the ship is that is attacking
    def strength_check(s):
        return s.num_ships \
            + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == s.ID) \
            - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == s.ID)
    # check if we need to send backup
    for planet in state.my_planets():
        if planet.ID in en:
        # if we are stronger than the enemy planet then we return true
            if strength_check(planet) <= 0:
                return True
    # we need to send backup
    return False


# check who has the largest fleet
def check_largest_fleet(state):
    # return that my number of ships is greater than the enemy ships
    return sum(planet.num_ships for planet in state.my_planets()) \
        + sum(fleet.num_ships for fleet in state.my_fleets()) \
        > sum(planet.num_ships for planet in state.enemy_planets()) \
        + sum(fleet.num_ships for fleet in state.enemy_fleets())  


# check if any neutral or enemy planets are available
# enemy planets
def is_enemy(state):
    return any(state.enemy_planets())

# neutral planets
def is_neutral(state):
    return any(state.neutral_planets())