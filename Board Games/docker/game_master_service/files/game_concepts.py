import enum
import collections
from random import shuffle as RandomShuffle
from copy import deepcopy


# func source: https://www.geeksforgeeks.org/program-to-find-whether-a-no-is-power-of-two/
def isPowerOfTwo(n): 
    if (n == 0): 
        return False
    while (n != 1): 
            if (n % 2 != 0): 
                return False
            n = n // 2
    return True


class TournamentState(enum.Enum):
    WAITING_FOR_PLAYERS = 0
    BEFORE_ROUND_START = 1
    ROUND_IN_PROGRESS = 2
    ROUND_FINISHED = 3
    FINISHED = 4



class GameType(enum.Enum):
    TIC_TAC_TOE = 0
    CHESS = 1

    @staticmethod
    def Convertable(gametype_string):
        return gametype_string in ["tic-tac-toe", "chess"]
    
    @staticmethod
    def FromStringToEnum(gametype):
        if gametype == "chess":
            return GameType.CHESS
        if gametype == "tic-tac-toe":
            return GameType.TIC_TAC_TOE
        return None

    @staticmethod
    def FromEnumToString(gametype):
        if gametype == GameType.CHESS:
            return "chess"
        if gametype == GameType.TIC_TAC_TOE:
            return "tic-tac-toe"
        return None

GameTypeToStringDict = {
    GameType.TIC_TAC_TOE: "tic-tac-toe",
    GameType.CHESS: "chess"
}

class Play():
    def __init__(self, id, player1_id, player2_id, gametype, tournament_id = None, phase = None):
        self.id = id
        self.player1 = player1_id
        self.player2 = player2_id
        self.gametype = gametype
        self.tournament_id = tournament_id
        self.phase = phase
        self.isADraw = None
        self.winner = None
        self.player1_username = None
        self.player2_username = None


    def IsInTournament(self):
        return self.tournament_id != None

    def UpdatePlayResult(self, winner_id, isADraw):
        self.winner = winner_id
        self.isADraw = isADraw

    def GetWinner(self):
        if self.isADraw:
            return None
        return self.winner

    def GetLoser(self):
        if self.isADraw:
            return None
        return self.player1 if self.player2 == self.winner else self.player2
    
    def IsOver(self):
        return self.isADraw or self.winner != None

    def PlayerExists(self, player_id):
        return self.player1 == player_id or self.player2 == player_id

    def UpdateUsernames(self, player1_username, player2_username):
        self.player1_username = player1_username
        self.player2_username = player2_username

    def GetJsonRepresentation(self):
        return {'play_id':self.id, 'player1_id': self.player1, 'player2_id': self.player2, 'gametype': GameTypeToStringDict[self.gametype], 'tournament_id': self.tournament_id,\
            'phase': self.phase, 'isADraw': self.isADraw, 'winner_id': self.winner, 'player1_username': self.player1_username, 'player2_username': self.player2_username}

    def __str__(self):
        return "| id={0} | player1={1} | player2={2} | tournament_id={3} | phase={4} | isADraw={5} | winner={6}".\
            format(self.id, self.player1, self.player2, self.tournament_id, self.phase, self.isADraw, self.winner)

    

class PlayList():
    def __init__(self):
        self.plays = {}

    def AddPlay(self, play):
        self.plays[play.id] = play

    def PopPlay(self, play_id):
        return self.plays.pop(play_id, False)

    def PlayExists(self, play_id):
        return self.plays.get(play_id) != None

    def Size(self):
        return len(self.plays)
        

class TournamentInfo():
    def __init__(self, id, registred_players_count, max_players, gametype, creator_id):
        self.id = id
        self.registered_players_count = registred_players_count
        self.max_players = max_players
        self.gametype = gametype
        self.creator = creator_id

    def GetJsonRepresentation(self):
        return {'id': self.id, 'registered_players_count': self.registered_players_count, 'participants_num': self.max_players,\
            'gametype': GameTypeToStringDict[self.gametype], 'creator_id': self.creator}

class Tournament():
    def __init__(self, id, max_players, gametype, creator_id, administer_play_id_callback, player_out_of_tournament_notification_callback = None):
        assert(max_players >= 4 and isPowerOfTwo(max_players))
        self._id = id
        self._max_players = max_players
        self._gametype = gametype
        self._creator_id = creator_id

        self._registered_players_count = 0
        self.__plays_to_be_created = PlayList()
        self.__created_plays = PlayList()
        self.__completed_plays = PlayList()

        self.__player_ids = []
        self.__active_players = []
        self.__players_playing = []
        self.__round_winners = []
        self.__round_losers = []
        self.__round_players_with_draw = []

        self.__isFinals = False
        self.__players_in_semifinal = []
        self.__state = TournamentState.WAITING_FOR_PLAYERS

        self.__plays_confirmed = False
        self.__playersPaired_and_PlaysCreated = False
        self.__round_finished = False
        self.__draw_handle_active = False
        self.__administer_play_id_callback = administer_play_id_callback
        self.__player_out_of_tournament_notification_callback = player_out_of_tournament_notification_callback

    def RegisterPlayer(self, player_id):
        if player_id not in self.__player_ids and not self.IsFull():
            self.__player_ids.append(player_id)
            self._registered_players_count += 1
            self.__CheckAndUpdateTournamentStatus()
            return True
        return False

    def UnregisterPlayer(self, player_id):
        if player_id in self.__player_ids and self.__state == TournamentState.WAITING_FOR_PLAYERS:
            self.__player_ids.remove(player_id)
            self._registered_players_count -= 1
            return True
        return False
        
    def GetTournamentInfo(self):
        return TournamentInfo(self._id, self._registered_players_count, self._max_players, self._gametype, self._creator_id)

    def IsFull(self):
        return self._max_players == self._registered_players_count

    def IsOver(self):
        return self.__state == TournamentState.FINISHED

    def Started(self):
        return self.__state != TournamentState.WAITING_FOR_PLAYERS

    def WaitingForConfirmation(self):
        return self.__state == TournamentState.BEFORE_ROUND_START

    def GetPlaysToBeCreatedOnPlayMaster(self):
        return deepcopy(list(self.__plays_to_be_created.plays.values()))

    def GetAllActivePlays(self):
        return deepcopy(list(self.__created_plays.plays.values()))

    def GetPlayersCurrentPlay(self, player_id):
        for play in self.__created_plays.plays.values():
            if play.PlayExists(player_id):
                return deepcopy(play)
        return None

    def FindActivePlay(self, play_id):
        return self.__created_plays.plays.get(play_id)

    @DeprecationWarning
    def ConfirmPlaysAreSentToPlayMaster(self):
        if self.__state == TournamentState.BEFORE_ROUND_START:

            if not self.__draw_handle_active:
                for play in self.__plays_to_be_created.plays.values():
                    self.__players_playing.append(play.player1)
                    self.__players_playing.append(play.player2)

            self.__created_plays.plays.update(self.__plays_to_be_created.plays)
            self.__plays_to_be_created = PlayList()

            self.__plays_confirmed = True

            self.__CheckAndUpdateTournamentStatus()

    def ConfirmPlaySentToPlayMaster(self, play_id):
        assert(self.__plays_to_be_created.plays.get(play_id) != None)
        if self.__state == TournamentState.BEFORE_ROUND_START:

            if not self.__draw_handle_active:
                play = self.__plays_to_be_created.plays[play_id]
                self.__players_playing.append(play.player1)
                self.__players_playing.append(play.player2)

            self.__created_plays.AddPlay(self.__plays_to_be_created.PopPlay(play_id))

            if self.__plays_to_be_created.Size() == 0:
                self.__plays_confirmed = True
                self.__CheckAndUpdateTournamentStatus()

    def ReceiveFinishedPlayResultAndUpdate(self, play_id, winner_id, isADraw):
        assert(self.__created_plays.PlayExists(play_id))
        if not (self.__state == TournamentState.ROUND_IN_PROGRESS or self.__draw_handle_active):
            return

        if self.__created_plays.PlayExists(play_id):
            play = self.__created_plays.plays[play_id]
            play.UpdatePlayResult(winner_id, isADraw)

            self.__completed_plays.AddPlay(self.__created_plays.PopPlay(play_id))

            if isADraw:
                self.__round_players_with_draw.append(play.player1)
                self.__round_players_with_draw.append(play.player2)
                self.__draw_handle_active = True
            else:
                self.__players_playing.remove(play.player1)
                self.__players_playing.remove(play.player2)
                self.__round_winners.append(play.GetWinner())
                self.__round_losers.append(play.GetLoser())

                if len(self.__active_players) == 4 and not self.__isFinals:
                    pass # The only case we don't remove any loser from active players, because we need them in semifinals
                else:
                    self.__RemoveFromActivePlayers(play.GetLoser())

                if self.__isFinals: # In finals we also remove winners from active players
                    self.__RemoveFromActivePlayers(play.GetWinner())

                if len(self.__players_playing) == 0:
                    self.__round_finished = True
                    self.__draw_handle_active = False
                    if self.__isFinals and len(self.__round_winners) == 2:
                        self.__ChangeState(TournamentState.FINISHED)

        
        self.__CheckAndUpdateTournamentStatus()

    def PlayNeedsToBeConfirmed(self, play_id):
        return self.__plays_to_be_created.plays.get(play_id) != None

    def GetActivePlayers(self):
        return deepcopy(self.__active_players)

    def RetrieveAllPlayRecords(self):
        return deepcopy(list(self.__completed_plays.plays.values()))

    def __CheckAndUpdateTournamentStatus(self):
        if self.__state == TournamentState.WAITING_FOR_PLAYERS:
            if self.IsFull():
                self.__round_winners = deepcopy(self.__player_ids)
                self.__active_players = deepcopy(self.__player_ids)
                self.__PairPlayersAndCreateRespectivePlays()
                self.__ChangeState(TournamentState.BEFORE_ROUND_START)
        if self.__state == TournamentState.BEFORE_ROUND_START and self.__plays_confirmed:
            self.__ChangeState(TournamentState.ROUND_IN_PROGRESS)
            self.__plays_confirmed = False
            self.__draw_handle_active = False
        if self.__state == TournamentState.ROUND_IN_PROGRESS:
            if self.__draw_handle_active:
                self.__ChangeState(TournamentState.BEFORE_ROUND_START)
                self.__PairPlayersAndCreateRespectivePlays()
            elif self.__round_finished:
                self.__isFinals = len(self.__round_winners) == 2
                self.__PairPlayersAndCreateRespectivePlays()
                self.__ChangeState(TournamentState.BEFORE_ROUND_START)
                self.__round_finished = False
        if self.__state == TournamentState.ROUND_FINISHED:
            pass
        if self.__state == TournamentState.FINISHED:
            pass
    
    def __GetNewPlayId(self, gametype):
        return self.__administer_play_id_callback(gametype)

    def __CreatePlay(self, player1_id, player2_id, phase = None):                     # phase 1 for finals, phase 2 for 3rd and 4th place
        play_id = self.__GetNewPlayId(self._gametype)
        assert(play_id != None)
        play = Play(play_id, player1_id, player2_id, self._gametype, self._id, phase)
        return play

    def __ChangeState(self, new_state):
        self.__state = new_state

    def __RemoveFromActivePlayers(self, player_id):
        self.__active_players.remove(player_id)
        if self.__player_out_of_tournament_notification_callback != None:
            self.__player_out_of_tournament_notification_callback(player_id)

    def __PairPlayersAndCreateRespectivePlays(self):
        
        if not self.__draw_handle_active:
            RandomShuffle(self.__round_winners)
            
            phase = None
            if self.__isFinals:
                phase = 2
                player1 = self.__round_losers.pop(0)
                player2 = self.__round_losers.pop(0)
                play = self.__CreatePlay(player1, player2, phase)
                self.__plays_to_be_created.AddPlay(play)
                self.__players_in_semifinal.append(player1)
                self.__players_in_semifinal.append(player2)
                phase = 1

            if len(self.__round_winners) == 4:
                phase = 4 # used for browser's client-side notifications purpose

            while(len(self.__round_winners) > 1):
                player1 = self.__round_winners.pop(0)
                player2 = self.__round_winners.pop(0)
                play = self.__CreatePlay(player1, player2, phase)
                self.__plays_to_be_created.AddPlay(play)

        else:
            phase = None
            while(len(self.__round_players_with_draw) != 0):
                player1 = self.__round_players_with_draw.pop(0)
                player2 = self.__round_players_with_draw.pop(0)
                if self.__isFinals:
                     phase = 2 if player1 in self.__players_in_semifinal else 1
                play = self.__CreatePlay(player1, player2, phase)
                self.__plays_to_be_created.AddPlay(play)

        self.__round_losers = []
        self.__playersPaired_and_PlaysCreated = True

        


