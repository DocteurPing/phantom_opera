from collections import defaultdict


def get_rooms_list(gamestate: dict) -> dict:
    tmp = defaultdict(lambda: [0, 0])
    for character in gamestate['characters']:
        tmp[character['position']][0] += 1
        if character['suspect'] is True:
            tmp[character['position']][1] += 1
    return tmp


def get_groups_total(gamestate):
    total = 0
    for room, nbs in get_rooms_list(gamestate).items():
        if nbs[0] == 1 or room == gamestate['shadow']:
            total -= nbs[1]
        else:
            total += nbs[1]
    return total


def inspector_gain(gamestate):
    total = get_groups_total(gamestate)
    return 8 - abs(total) if total < 0 else 8 - total + .1


def inspector_ghost_gain(gamestate):
    total = get_groups_total(gamestate)
    return abs(total) + .1 if total < 0 else total


def ghost_gain(gamestate) -> int:
    if 'fantom' not in gamestate:
        return inspector_ghost_gain(gamestate)
    ghost = next((item for item in gamestate['characters'] if item["color"] == gamestate['fantom']), None)
    isolated = 0
    grouped = 0
    room_list = get_rooms_list(gamestate)
    ghost_room = room_list[ghost['position']]
    is_ghost_isolated = ghost_room[0] == 1 or ghost['position'] == gamestate['shadow']
    for id, nbs in room_list.items():
        if nbs[0] == 1 or id == gamestate['shadow']:
            isolated += nbs[1]
        else:
            grouped += nbs[1]
    if is_ghost_isolated is True:
        return (isolated - grouped) + 0.1
    else:
        return grouped - isolated
