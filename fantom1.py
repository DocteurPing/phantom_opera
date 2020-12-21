import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler
from nodes import RootNode
from compute_gain import ghost_gain, inspector_gain

import protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/fantom.log"):
    os.remove("./logs/fantom.log")
file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
fantom_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
fantom_logger.addHandler(stream_handler)


class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.game_state = None
        self.intents = {
            4: [ghost_gain, inspector_gain, inspector_gain, ghost_gain],
            3: [ghost_gain, ghost_gain, inspector_gain],
            2: [ghost_gain, inspector_gain],
            1: [ghost_gain]
        }
        self.questions = {
            "select character": self.select_char,
            "select position": self.select_pos,
            "activate red power": 1
        }

    def select_char(self, options):
        self.game_state['options'] = options
        self.game_state['compute_gain'] = self.intents[len(options)]
        self.tree = RootNode(self.game_state)
        return self.tree.best.options_index

    def select_pos(self, options) -> int:
        index = options.index(self.tree.get_move_target())
        return index

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        self.game_state = question["game state"]
        response_index = random.randint(0, len(data) - 1)
        question_type = question['question type']
        for question in self.questions:
            if (question_type.startswith(question)) and self.questions[question] is not None:
                response_index = self.questions[question](data)
        # log
        fantom_logger.debug("|\n|")
        fantom_logger.debug("fantom answers")
        fantom_logger.debug(f"game state--------- {self.game_state}")
        fantom_logger.debug(f"data -------------- {data}")
        fantom_logger.debug(f"response index ---- {response_index}")
        fantom_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()

p.run()
