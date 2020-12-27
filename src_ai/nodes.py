from copy import deepcopy as dcpy

PATH = [
    (1, 4),
    (0, 2),
    (1, 3),
    (2, 7),
    (0, 5, 8),
    (4, 6),
    (5, 7),
    (3, 6, 9),
    (4, 9),
    (7, 8)
]
SECRET_PATH = [
    (1, 4),
    (0, 2, 5, 7),
    (1, 3, 6),
    (2, 7),
    (0, 5, 8, 9),
    (4, 6, 1, 8),
    (5, 7, 2, 9),
    (3, 6, 9, 1),
    (4, 9, 5),
    (7, 8, 4, 6)
]


# Basic Node
class Node:
    def __init__(self):
        self.options = []
        self.score = 0
        self.is_root = False
        self.best = None
        self.next = None

    def best_gain(self):
        return self.score if self.best is None else self.best.best_gain()

    def get_move_target(self):
        return None if self.best is None else self.best.get_move_target()


# Possibility of movement for a character
class MoveNode(Node):

    def __init__(self, gamestate: dict, charid: int, pos: int):
        Node.__init__(self)
        self.gamestate = dcpy(gamestate)
        self.pos = pos
        self.character = self.gamestate['characters'][charid]
        self.character['position'] = self.pos
        self.gain = self.gamestate['compute_gain'].pop(0)(self.gamestate)
        if len(self.gamestate['options']) > 0:
            self.next = self.gamestate['root_node'](self.gamestate)

    def get_best_gain(self):
        return self.next.get_best_gain() if self.next is not None else self.gain

    def get_move_target(self):
        return self.pos


def get_character_id(characters: list, character_color: str) -> tuple:
    for id, character in enumerate(characters):
        if character['color'] == character_color:
            return id, character
    return -1, None


# Node for each character
class CharacterNode(Node):

    def __init__(self, gamestate, character_color: str):
        Node.__init__(self)
        self.is_root = True
        self.gamestate = dcpy(gamestate)
        self.id, self.character = get_character_id(
            self.gamestate['characters'],
            character_color
        )
        self.gamestate['options'].pop(
            next(id for id, ch in enumerate(
                self.gamestate['options']) if ch['color'] == character_color)
        )
        self.gain = 0

    def update_best_node(self, tmp):
        if self.best is None or tmp.score > self.best.score:
            self.best = tmp
            self.gain = tmp.score


class RootNode(Node):

    def __init__(self, game_state):

        super().__init__()
        self.is_root = True
        game_state['root_node'] = RootNode
        self.predictions = []
        self.best = None

        for id, character in enumerate(game_state['options']):
            colors = character['color']
            paths = SECRET_PATH[character['position']] if colors is 'pink' else PATH[character['position']]
            if character['position'] in game_state['blocked']:
                paths = [r for r in paths if r not in game_state['blocked']]
            tmp = CharacterNode(game_state, colors)
            for path in paths:
                mn = MoveNode(tmp.gamestate, tmp.id, path)
                tmp.update_best_node(mn)
                self.options.append(mn)
            tmp.options_index = id
            if self.best is None or abs(tmp.best_gain()) < abs(self.best.best_gain()):
                self.best = tmp
            self.predictions.append(tmp)
