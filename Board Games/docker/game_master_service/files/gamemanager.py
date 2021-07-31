from game_concepts import Tournament, PlayList, Play, GameType, TournamentInfo
from copy import deepcopy
from http_status import HttpStatus
import random
import requests



class GameManager():
    def __init__(self, administer_play_id_callback, administer_tournament_id_callback):
        self.__practice_play_register = PlayerPracticePlayRegister(administer_play_id_callback)
        self.__tournament_register = PlayerTournamentRegister(administer_tournament_id_callback, administer_play_id_callback, self.PlayerOutTournamentCallback)
        self.__playerTokenHeader = {} # {player_id: header}
        self.__playerUserNames = {} # {player_id: username}

        self.__playerToUIUrl = {} # {player_id: ui_url}                 ui_url: url from ui with which player is communicating.
        self.__playerToPlayId = {} # {player_id: play_id}
        self.__playToPlayMasterUrl = {} # {play_id, play_master_url}    play_master_url: url of playmaster in which game is hosted.
        self.__play_master_urls = []

    def SetPlayMasterURLs(self, urls):
        self.__play_master_urls = urls

    def GetPlayMasterHostUrl(self, play_id):
        return self.__playToPlayMasterUrl.get(play_id)

    def SetPlayMasterHostUrl(self, play_id, pm_url):
        if self.__playToPlayMasterUrl.get(play_id) != None:
            self.__playToPlayMasterUrl[play_id] = pm_url

    def GetPlayersGamePlayMasterHostUrl(self, player_id):
        play_id = self.__playerToPlayId.get(player_id)
        if play_id == None:
            return None
        return self.__playToPlayMasterUrl.get(play_id)

    def __Update(self):
        if not len(self.__play_master_urls) > 0:
            return
        
        plays = self.GetAllPlaysThatNeedConfirmation()
        for play in plays:
            dictToSend = {'play_id':play.id, 'player1_id':play.player1, 'player2_id':play.player2, \
                'player1_username': self.__playerUserNames.get(play.player1), 'player2_username': self.__playerUserNames.get(play.player2),\
                    'tournament_id': play.tournament_id, 'phase': play.phase, 'player1_ui_url': self.__playerToUIUrl.get(play.player1), 'player2_ui_url': self.__playerToUIUrl.get(play.player2)}

            gametype_str = GameType.FromEnumToString(play.gametype).lower()
            playmaster_url = self.__play_master_urls[random.randint(0, len(self.__play_master_urls) - 1)]
            try:
                res = requests.post(playmaster_url + 'games/{}/register'.format(gametype_str), json=dictToSend, headers=self.__playerTokenHeader[play.player1])
                print("\nSent game {} to playmaster.".format(play.id))
                #res.raise_for_status()
            except requests.exceptions.RequestException as e:
                return str(e), HttpStatus.request_timetout_408.value

            if res.status_code == HttpStatus.created_201.value:
                self.ConfirmPlayCreation(play.id)
                self.__playerToPlayId[play.player1] = play.id
                self.__playerToPlayId[play.player2] = play.id
                self.__playToPlayMasterUrl[play.id] = playmaster_url
                if play.tournament_id == None:
                    print("\nPlayer {} removed in from plays. token/usr deleted.".format(play.player1))
                    print("\nPlayer {} removed from plays. token/usr deleted.\n".format(play.player2))
                    del self.__playerTokenHeader[play.player1]
                    del self.__playerTokenHeader[play.player2]
            else:
                print("Bad Play Confirmation answer from the PlayMaster: \n {}".format(res.text))
        

    def AddPlayerInPracticePlayQueue(self, player_id, gametype, username, player_token_header, ui_url):
        if self.PlayerExists(player_id):
            return False
        success = self.__practice_play_register.AddPlayer(player_id, gametype)
        if success:
            self.__practice_play_register.PairPlayersAttempt()
            print("\nPlayer {} registered in practice play. token/usr saved.\n".format(player_id))
            self.__playerTokenHeader[player_id] = player_token_header
            self.__playerUserNames[player_id] = username

            self.__playerToUIUrl[player_id] = ui_url

            self.__Update()
        return success

    # TODO: careful here as well
    def RemovePlayerFromPracticePlayQueue(self, player_id):
        self.__practice_play_register.RemovePlayer(player_id)

    def CreateTournament(self, max_players, gametype, creator_id):
        success = self.__tournament_register.CreateTournament(max_players, gametype, creator_id)
        self.__Update()
        return success

    def RegisterPlayerInTournament(self, player_id, tournament_id, username, player_token_header, ui_url):
        success = self.__tournament_register.RegisterPlayerInTournament(player_id, tournament_id)
        if success:
            print("\nPlayer {} registered in tournament. token/usr saved.\n".format(player_id))
            self.__playerTokenHeader[player_id] = player_token_header
            self.__playerUserNames[player_id] = username
            self.__playerToUIUrl[player_id] = ui_url
            self.__Update()
        return success
    
    def UnregisterPlayerFromTournament(self, player_id):
        return self.__tournament_register.UnregisterPlayerFromTournament(player_id)

    def PlayerExists(self, player_id):
        return self.__practice_play_register.PlayerExists(player_id) or self.__tournament_register.PlayerExists(player_id)

    def ConfirmPlayCreation(self, play_id):
        if self.__practice_play_register.PlayNeedsCreateConfirmation(play_id):
            return self.__practice_play_register.ConfirmPlayCreatedOnPlayMaster(play_id)
        else:
            return self.__tournament_register.ConfirmPlayCreatedOnPlayMaster(play_id)

    def UpdatePlayResult(self, play):
        if play.tournament_id == None:
            self.__practice_play_register.UpdatePlayResult(play.id, play.winner, play.isADraw)
            del self.__playerToUIUrl[play.player1]
            del self.__playerToUIUrl[play.player2]
        else:
            self.__tournament_register.UpdatePlayResult(play)
        del self.__playerToPlayId[play.player1]
        del self.__playerToPlayId[play.player2]
        del self.__playToPlayMasterUrl[play.id]
        self.__Update()
    
    def GetOpenTournamentsInfo(self):
        return self.__tournament_register.GetOpenTournamentsInfo()

    def GetOpenTournamentsInfoOfGametype(self, gametype):
        return self.__tournament_register.GetOpenTournamentsInfoOfGametype(gametype)

    def GetAllPlaysThatNeedConfirmation(self):
        plays = []
        plays.extend(self.__practice_play_register.GetPlaysThatNeedCreatedConfirmation())
        plays.extend(self.__tournament_register.GetPlaysThatNeedCreationOnPlayMaster())
        return deepcopy(plays)

    def ThereAreFinishedPlays(self):
        return self.__practice_play_register.ThereAreFinishedPlays() or self.__tournament_register.ThereAreFinishedTournaments()

    def GetAllActivePlays(self):
        plays = []
        plays.extend(self.__practice_play_register.GetAllActivePlays())
        plays.extend(self.__tournament_register.GetAllActivePlays())
        for play in plays:
            play.UpdateUsernames(self.__playerUserNames.get(play.player1), self.__playerUserNames.get(play.player2))
        return plays

    def GetAllActivePlaysToJson(self):
        plays_json = []
        plays = []
        plays.extend(self.__practice_play_register.GetAllActivePlays())
        plays.extend(self.__tournament_register.GetAllActivePlays())
        for play in plays:
            play.UpdateUsernames(self.__playerUserNames.get(play.player1), self.__playerUserNames.get(play.player2))
            plays_json.append(play.GetJsonRepresentation())

        return {'plays': plays_json}

    def FindActivePlay(self, play_id):
        play = self.__practice_play_register.FindActivePlay(play_id)
        if play == None:
            play = self.__tournament_register.FindActivePlay(play_id)
        return play

    def GetAndRemoveFinishedTournamentInfoAndFinishedPlays(self):
        plays = []
        tournaments_info = []
        if self.__tournament_register.ThereAreFinishedTournaments():
            tournaments_info, plays = self.__tournament_register.GetAndRemoveFinishedTournamentInfoAndPlays()
        if self.__practice_play_register.ThereAreFinishedPlays():
            plays.extend(self.__practice_play_register.GetAndRemoveFinishedPlays())

        for play in plays:
            if play.tournament_id == None:
                del self.__playerUserNames[play.player1]
                del self.__playerUserNames[play.player2]
        self.__Update()
        return tournaments_info, plays

    # Returns None if player in play not found
    def GetPlayersCurrentPlay(self, player_id):
        if self.__practice_play_register.PlayerExists(player_id):
            return self.__practice_play_register.GetPlayersCurrentPlay(player_id)
        return self.__tournament_register.GetPlayersCurrentPlay(player_id)

    def PlayerOutTournamentCallback(self, player_id):
        print("\nPlayer {} removed from tournament. token/usr deleted.\n".format(player_id))
        del self.__playerUserNames[player_id]
        del self.__playerTokenHeader[player_id]
        del self.__playerToUIUrl[player_id]


class PlayerPracticePlayRegister():
    def __init__(self, administer_play_id_callback):
        assert(administer_play_id_callback != None)
        self.__registered_player_list_of_gametype = {} # {gametype1: [p1,p2,p3], gametype2: [p4,p5,p6] ...}
        self.__registered_player_list_of_gametype[GameType.TIC_TAC_TOE] = []
        self.__registered_player_list_of_gametype[GameType.CHESS] = []
        
        self.__registered_player_gametype = {} # {player_id: gametype}
        self.__players_playing = []

        self.__plays_to_be_confirmed_from_play_master = {}  # Plays that are not confirmed to be created on PlayMaster side. ({play_id: play})
        self.__active_plays = {} # {play_id: play}
        self.__finished_plays = {} # {play_id: play}

        self.__administer_play_id_callback = administer_play_id_callback

    def AddPlayer(self, player_id, gametype):
        assert(gametype in self.__registered_player_list_of_gametype.keys())
        if not self.PlayerExists(player_id):
            self.__registered_player_gametype[player_id] = gametype
            self.__registered_player_list_of_gametype[gametype].append(player_id)
            return True
        return False

    # TODO: need to be careful here with this
    def RemovePlayer(self, player_id):
        if self.PlayerExists(player_id):
            gametype = self.__registered_player_gametype[player_id]
            del self.__registered_player_gametype[player_id]
            self.__registered_player_list_of_gametype[gametype].remove(player_id)

    def PlayerExists(self, player_id):
        return self.__registered_player_gametype.get(player_id) != None or player_id in self.__players_playing

    def GetRegisteredPlayerCount(self, gametype):
        assert(gametype in self.__registered_player_list_of_gametype.keys())
        return len(self.__registered_player_list_of_gametype[gametype])

    def PairPlayersAttempt(self):
        for gametype in self.__registered_player_list_of_gametype.keys():
            if self.HasEnoughPlayersForAPair(gametype):
                self.PairPlayersOfGameType(gametype)

    def HasEnoughPlayersForAPair(self, gametype):
        return self.GetRegisteredPlayerCount(gametype) > 1

    def PairPlayersOfGameType(self, gametype):
        
        if not (self.HasEnoughPlayersForAPair(gametype)):
            return
        play_id = self.__administer_play_id_callback(gametype)
        if not (play_id):
            return

        player1 = self.__PopRegisteredPlayer(gametype)
        player2 = self.__PopRegisteredPlayer(gametype)
        self.__players_playing.extend([player1, player2])
        play = Play(play_id, player1, player2, gametype)
        self.__plays_to_be_confirmed_from_play_master[play.id] = play

    def ConfirmPlayCreatedOnPlayMaster(self, play_id):
        if self.PlayNeedsCreateConfirmation(play_id):
            self.__active_plays[play_id] = self.__plays_to_be_confirmed_from_play_master.pop(play_id)
            return True
        return False

    def UpdatePlayResult(self, play_id, winner_id, isADraw):
        assert(self.__active_plays.get(play_id) != None)
        play = self.__active_plays[play_id]
        self.__active_plays[play_id].UpdatePlayResult(winner_id, isADraw)
        self.__players_playing.remove(play.player1)
        self.__players_playing.remove(play.player2)
        self.__finished_plays[play_id] = self.__active_plays.pop(play_id)

    def GetPlaysThatNeedCreatedConfirmation(self):
        return deepcopy(list(self.__plays_to_be_confirmed_from_play_master.values()))

    def ThereArePlaysToConfirmCreation(self):
        return len(self.__plays_to_be_confirmed_from_play_master) > 0

    def PlayNeedsCreateConfirmation(self, play_id):
        return self.__plays_to_be_confirmed_from_play_master.get(play_id) != None

    def ThereArePlaysInProgress(self):
        return len(self.__active_plays) > 0

    def ThereAreFinishedPlays(self):
        return len(self.__finished_plays) > 0

    def __PopRegisteredPlayer(self, gametype):
        if self.GetRegisteredPlayerCount(gametype) > 0:
            player = self.__registered_player_list_of_gametype[gametype].pop()
            del self.__registered_player_gametype[player]
            return player
        return None

    def GetAllActivePlays(self):
        return deepcopy(list(self.__active_plays.values()))

    def FindActivePlay(self, play_id):
        return self.__active_plays.get(play_id)

    def GetPlayersGameOfInterest(self, player_id):
        assert(self.PlayerExists(player_id))
        return self.__registered_player_gametype[player_id]
    
    def GetAndRemoveFinishedPlays(self):
        plays = deepcopy(list(self.__finished_plays.values()))
        self.__finished_plays = {}
        return plays
    
    def GetPlayersCurrentPlay(self, player_id):
        if player_id in self.__players_playing:
            for play in self.__active_plays.values():
                if play.PlayerExists(player_id):
                    return deepcopy(play)
        return None



class PlayerTournamentRegister():
    def __init__(self, administer_tournament_id_callback, administer_play_id_callback, inform_game_manager_player_out_of_tournament_callback):
        assert(administer_tournament_id_callback != None and administer_play_id_callback != None)
        self.__open_tournaments = {}        #{tournament_id: tournament}
        self.__started_tournaments = {}     # >>
        self.__finished_tournaments = {}    # >>
        
        self.__registered_players = {} # used to represent registered and also *active* players ({player_id: tournament_id})

        self.__administer_tournament_id_callback = administer_tournament_id_callback
        self.__administer_play_id_callback = administer_play_id_callback
        self.inform_game_manager_player_out_of_tournament_callback = inform_game_manager_player_out_of_tournament_callback
    
    # Injecting it in a tournament class a callback, we get updated on which players are out of the tournament
    def __player_out_of_tournament_callback(self, player_id):
        assert(self.PlayerExists(player_id))
        self.inform_game_manager_player_out_of_tournament_callback(player_id)
        del self.__registered_players[player_id]
    
    def RegisterPlayerInTournament(self, player_id, tournament_id):
        tournament = self.__open_tournaments.get(tournament_id)
        if tournament != None and not self.PlayerExists(player_id):
            if tournament.RegisterPlayer(player_id):
                self.__registered_players[player_id] = tournament._id
                if tournament.Started():
                    self.__started_tournaments[tournament_id] = tournament
                    del self.__open_tournaments[tournament_id]
                return True
        return False
    
    def UnregisterPlayerFromTournament(self, player_id):
        assert(self.PlayerExists(player_id))
        tournament = self.__open_tournaments.get(self.__registered_players[player_id])
        if tournament != None:
            if tournament.UnregisterPlayer(player_id):
                del self.__registered_players[player_id]
                return True
        return False

    def PlayerExists(self, player_id):
        return self.__registered_players.get(player_id) != None

    def CreateTournament(self, max_players, gametype, creator_id):
        tournament_id = self.__administer_tournament_id_callback(max_players, gametype, creator_id)
        assert(tournament_id != None)
        tr = Tournament(tournament_id, max_players, gametype, creator_id, self.__administer_play_id_callback, self.__player_out_of_tournament_callback)
        self.__open_tournaments[tr._id] = tr
        return tr.GetTournamentInfo()

    def GetOpenTournamentsInfo(self):
        return [tournament.GetTournamentInfo() for tournament in self.__open_tournaments.values()]
    
    def GetOpenTournamentsInfoOfGametype(self, gametype):
        tournaments = []
        for tournament in self.__open_tournaments.values():
            if tournament._gametype == gametype:
                tournaments.append(tournament.GetTournamentInfo())
        return tournaments

    def ThereAreFinishedTournaments(self):
        return len(self.__finished_tournaments) > 0

    def GetPlaysThatNeedCreationOnPlayMaster(self):
        plays = []
        for tournament in self.__started_tournaments.values():
            if tournament.WaitingForConfirmation():
                plays.extend(tournament.GetPlaysToBeCreatedOnPlayMaster())
        return plays

    def PlaysNeedToBeSentToPlayMasterForCreation(self):
        for tournament in self.__started_tournaments.values():
            if tournament.WaitingForConfirmation():
                return True
        return False

    def ConfirmPlayCreatedOnPlayMaster(self, play_id):
        success, tournament = self.PlayNeedsCreateConfirmation(play_id)
        if success:
            tournament.ConfirmPlaySentToPlayMaster(play_id)
            return True
        return False

    def PlayNeedsCreateConfirmation(self, play_id):
        for tournament in self.__started_tournaments.values():
            if tournament.PlayNeedsToBeConfirmed(play_id):
                return True, tournament
        return False, None

    def UpdatePlayResult(self, play):
        assert(self.__started_tournaments.get(play.tournament_id) != None)
        tournament = self.__started_tournaments.get(play.tournament_id)
        tournament.ReceiveFinishedPlayResultAndUpdate(play.id, play.winner, play.isADraw)
        if tournament.IsOver():
            self.__finished_tournaments[tournament._id] = tournament
            del self.__started_tournaments[tournament._id]

    def GetAndRemoveFinishedTournamentInfoAndPlays(self):
        tournaments_info = []
        plays = []
        for tournament in self.__finished_tournaments.values():
            tournaments_info.append(tournament.GetTournamentInfo())
            plays.extend(tournament.RetrieveAllPlayRecords())
        self.__finished_tournaments = {}
        return tournaments_info, plays
        
    def GetAllActivePlays(self):
        plays = []
        for tournament in self.__started_tournaments.values():
            plays.extend(tournament.GetAllActivePlays())
        return plays

    def FindActivePlay(self, play_id):
        for tournament in self.__started_tournaments.values():
            play = tournament.FindActivePlay(play_id)
            if play != None:
                return play
        return None

    def GetPlayersCurrentPlay(self, player_id):
        if self.__registered_players.get(player_id) != None:
            for tournament in self.__started_tournaments.values():
                if tournament.PlayerExists(player_id):
                    return tournament.GetPlayersCurrentPlay(player_id)
        return None