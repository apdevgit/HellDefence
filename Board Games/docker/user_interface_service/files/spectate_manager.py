from copy import deepcopy

class SpectateManager:
    def __init__(self):
        self.__playSpectatedBy = {} # {play_id: set([player1_sid, player2_sid])}
        self.__playerSpectates = {} # {player_sid, play_id}
        self.__games_to_unregister_from_spectate = []
        self.__last_spectator_token = None # Caching a valid token to  for authorizatino when we request spectate unregister from a play_master

    def AddSpectate(self, player_sid, play_id, access_token):
        if self.PlayerSpectates(player_sid):
            self.RemoveSpectator(player_sid)

        self.__playerSpectates[player_sid] = play_id
        spectator_list = self.__playSpectatedBy.get(play_id)

        if spectator_list != None:
            self.__playSpectatedBy[play_id].add(player_sid)
        else:
            self.__playSpectatedBy[play_id] = set([player_sid])

        self.__last_spectator_token = access_token

        if play_id in self.__games_to_unregister_from_spectate:
            self.__games_to_unregister_from_spectate.remove(play_id)

    def RemoveSpectator(self, player_sid):
        play_id = self.__playerSpectates.get(player_sid)
        if play_id == None:
            return

        spectators = self.__playSpectatedBy.get(play_id)
        if player_sid in spectators:
            spectators.remove(player_sid)
            del self.__playerSpectates[player_sid]

            if len(spectators) == 0:
                del self.__playSpectatedBy[play_id]
                self.__games_to_unregister_from_spectate.append(play_id)

    def GetAValidToken(self):
        return self.__last_spectator_token

    def PlayerSpectates(self, player_sid):
        return self.__playerSpectates.get(player_sid) != None

    def HasGamesToUnregister(self):
        return len(self.__games_to_unregister_from_spectate) > 0

    def GetGamesToUnregisterFromSpectate(self):
        return deepcopy(self.__games_to_unregister_from_spectate)

    def ConfirmGameIsUnregisteredAndDelete(self, play_id):
        if play_id in self.__games_to_unregister_from_spectate:
            self.__games_to_unregister_from_spectate.remove(play_id)

    


    