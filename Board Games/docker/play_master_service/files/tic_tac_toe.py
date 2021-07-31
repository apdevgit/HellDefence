from game import Game, GameType


class TicTacToeGame(Game):
    def __init__(self, play_id, player1_id, player2_id, player1_username, player2_username, tournament_id, phase):
        super().__init__(play_id)
        self.players = [player1_id, player2_id]
        self.gametype = GameType.TIC_TAC_TOE
        self.player1 = player1_id
        self.player2 = player2_id
        self.player1_username = player1_username
        self.player2_username = player2_username
        self.tournament_id = tournament_id
        self.phase = phase
        self.turn = 1
        self.squares = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def GetStateJson(self):
        return {'play_id': self.play_id, 'gametype': 'tic-tac-toe', 'squares': self.squares, 'player1': self.player1, 'player2': self.player2, \
            'player1_username': self.player1_username, 'player2_username': self.player2_username, 'tournament_id': self.tournament_id, \
                'phase': self.phase, 'turn': self.turn }

    def LoadStateFromJson(self, data_json):
        self.play_id = data_json.get('play_id')
        self.players = [data_json.get('player1'), data_json.get('player2')]
        self.squares = data_json.get('squares')
        self.player1 = data_json.get('player1')
        self.player2 = data_json.get('player2')
        self.player1_username = data_json.get('player1_username')
        self.player2_username = data_json.get('player2_username')
        self.tournament_id = data_json.get('tournament_id')
        self.phase = data_json.get('phase')
        self.turn = data_json.get('turn')

    def PlayTurn(self, square_index):
        if square_index not in range(9) or not self.SquareEmpty(square_index) or self.GameIsOver():
            return False

        # Put 1 when player1 plays and 10 when player2 plays
        mark = 1 if self.WhoPlays() == self.player1 else 10
        self.squares[square_index] = mark
        self.turn += 1
        return True

    def SquareEmpty(self, index):
        return self.squares[index] == 0

    def WhoPlays(self):
        return self.player1 if self.turn % 2 == 1 else self.player2

    def ThereIsAWinner(self):
        line_row_sums = []
        # Calculate Rows
        for row in range(3):
            line_row_sums.append(sum([self.squares[i] for i in range(row * 3, row * 3 + 3)]))
        # Calculate Columns
        for col in range(3):
            line_row_sums.append(sum([self.squares[i] for i in range(col,9,3)]))
        # Calculate Diagonals
        line_row_sums.append(self.squares[0] + self.squares[4] + self.squares[8])
        line_row_sums.append(self.squares[2] + self.squares[4] + self.squares[6])
        
        for value in line_row_sums:
            if value == 3 or value == 30:
                return True
        return False

    def GameIsOver(self):
        return self.ThereIsAWinner() or self.turn == 10

    def IsADraw(self):
        if self.turn == 10 and not self.ThereIsAWinner():
            return True
        return False
        
    def GetTheWinner(self):
        if self.ThereIsAWinner():
           return self.GetLastPlayerPlayed()
        return None

    def GetTheLoser(self):
        if self.ThereIsAWinner():
            return self.WhoPlays()
        return None

    def GetLastPlayerPlayed(self):
        if self.turn == 1:
            return None
        return self.player1 if self.WhoPlays() == self.player2 else self.player2

    def GetState(self):
        return {'player1_id': self.player1, 'player2_id': self.player2, 'gamestate': self.squares, 'gameover': self.GameIsOver(), 'phase': self.phase,\
             'winner': self.GetTheWinner(), 'gametype': GameType.FromEnumToString(self.gametype), 'isADraw': self.IsADraw(), 'tournament_id': self.tournament_id,\
                 'player1_username': self.player1_username, 'player2_username': self.player2_username, 'play_id': self.play_id, 'who_plays': self.WhoPlays()}
