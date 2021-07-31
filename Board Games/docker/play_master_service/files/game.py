import enum
from game_concepts import GameType


class Game():
    def __init__(self, play_id):
        self.play_id = play_id
        self.players = []
        self.gametype = None

    def GetType(self):
        return self.gametype

    def AssertGameType(self, gametype):
        assert(self.gametype == gametype)

    def PlayerExists(self, player_id):
        return player_id in self.players

    