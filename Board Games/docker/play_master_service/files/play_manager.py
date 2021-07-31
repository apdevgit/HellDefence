from game import Game, GameType
from tic_tac_toe import TicTacToeGame
from chess import Chess


class PlayManager():
    def __init__(self):
        self.registeredGames = {}       # {play_id: game}
        self.playerCurrentGame = {}     # {player_id: play_id}
        self.playerUIUrl = {}           # {player_id: ui_url}
        self.playSpectators = {}        # {play_id: set(ui_url1, ui_url2, ...)}

    def GetState(self):
        state = {}
        state['player_current_game'] = self.playerCurrentGame
        state['player_ui_url'] = self.playerUIUrl
        state['player_spectators'] = {k:list(v) for k,v in self.playSpectators.items()}
        return state

    def LoadState(self, state_json, play_id_to_game):
        player_current_game = state_json.get('player_current_game')
        play_spectators = state_json.get('player_spectators')
        player_ui_url = state_json.get('player_ui_url')

        player_current_game = {int(k):v for k,v in player_current_game.items()}
        play_spectators = {int(k):set(v) for k,v in play_spectators.items()}
        player_ui_url = {int(k):v for k,v in player_ui_url.items()}

        self.registeredGames = play_id_to_game
        self.playerCurrentGame = player_current_game
        self.playerUIUrl = player_ui_url
        self.playSpectators = play_spectators

    def RegisterGame(self, play_id, player1_ui_url, player2_ui_url, game):
        self.registeredGames[play_id] = game
        self.playerCurrentGame[game.player1] = play_id
        self.playerCurrentGame[game.player2] = play_id
        self.playerUIUrl[game.player1] = player1_ui_url
        self.playerUIUrl[game.player2] = player2_ui_url
        
    def RemoveGame(self, play_id):
        if self.PlayExists(play_id):
            del self.registeredGames[play_id]
        if self.playSpectators.get(play_id) != None:
            del self.playSpectators[play_id]

    def RemovePlayersOfGame(self, play_id):
        if self.PlayExists(play_id):
            players = self.registeredGames[play_id].players
            for p in players:
                del self.playerCurrentGame[p]
                del self.playerUIUrl[p]

    def PlayExists(self, play_id):
        return self.registeredGames.get(play_id) != None

    def PlayerIsInPlayingAGame(self, player_id):
        return self.playerCurrentGame.get(player_id) != None

    def GetGameFromId(self, play_id):
        return self.registeredGames.get(play_id)

    def GetGameFromPlayer(self, player_id):
        play_id = self.playerCurrentGame.get(player_id)
        return self.registeredGames.get(play_id)

    def AddSpectator(self, play_id, ui_url):
        if self.playSpectators.get(play_id) == None:
            self.playSpectators[play_id] = set([ui_url])
        else:
            self.playSpectators[play_id].add(ui_url)

    def RemoveSpectator(self, play_id, ui_url):
        spectators = self.playSpectators.get(play_id)
        if spectators != None:
            if ui_url in spectators:
                self.playSpectators[play_id].remove(ui_url)
            if len(self.playSpectators[play_id]) == 0:
                del self.playSpectators[play_id]
            
    def GetGameUIsRecipients(self, play_id):
        recipients = set()
        game = self.registeredGames.get(play_id)
        if game == None:
            return []
        recipients.add(self.playerUIUrl[game.player1])
        recipients.add(self.playerUIUrl[game.player2])
        spectators = self.playSpectators.get(play_id)
        if spectators != None:
            recipients.update(spectators)
        return recipients

    def GetPlayerUIUrl(self, player_id):
        return self.playerUIUrl.get(player_id)

    def UpdatePlayerUIUrl(self, player_id, ui_url):
        self.playerUIUrl[player_id] = ui_url


