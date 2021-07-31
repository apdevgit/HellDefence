from game import Game, GameType
import enum


class PieceType(enum.Enum):
    PAWN = 0
    ROOK = 1
    HORSE = 2
    BISHOP = 3
    QUEEN = 4
    KING = 5

class TeamColor(enum.Enum):
    WHITE = 0
    BLACK = 1

charToPieceType = {
    'p': PieceType.PAWN,
    'P': PieceType.PAWN,
    'r': PieceType.ROOK,
    'R': PieceType.ROOK,
    'h': PieceType.HORSE,
    'H': PieceType.HORSE,
    'b': PieceType.BISHOP,
    'B': PieceType.BISHOP,
    'q': PieceType.QUEEN,
    'Q': PieceType.QUEEN,
    'k': PieceType.KING,
    'K': PieceType.KING,
}

pieceTypeToCharUpper = {
    PieceType.PAWN : 'P',
    PieceType.ROOK : 'R',
    PieceType.HORSE : 'H',
    PieceType.BISHOP : 'B',
    PieceType.QUEEN : 'Q',
    PieceType.KING : 'K'
}

pieceTypeToRank = {
    PieceType.PAWN : 1,
    PieceType.ROOK : 4,
    PieceType.HORSE : 2,
    PieceType.BISHOP : 3,
    PieceType.QUEEN : 5,
    PieceType.KING : 6
}

chessColumnToIndex = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7
}

startingBoardString = [['0' for c in range(8)] for r in range(8)]
startingBoardString[0] = ['R', 'H', 'B', 'Q', 'K', 'B', 'H', 'R']
startingBoardString[1] = ['P' for t in range(8)]
startingBoardString[6] = ['p' for t in range(8)]
startingBoardString[7] = ['r', 'h', 'b', 'q', 'k', 'b', 'h', 'r']


class Piece():
    def __init__(self, pieceType, teamColor):
        self.pieceType = pieceType
        self.teamColor = teamColor

    @classmethod
    def CreateFromChar(cls, character):
        pieceType = charToPieceType.get(character)
        if pieceType == None:
            return None
        teamColor = TeamColor.WHITE if character.isupper() else TeamColor.BLACK
        return cls(pieceType, teamColor)
    

    def GetCharCode(self):
        char = pieceTypeToCharUpper[self.pieceType]
        return char if self.teamColor == TeamColor.WHITE else char.lower()


    def IsEnemyWith(self, piece):
        return self.teamColor != piece.teamColor


    def IsWhite(self):
        return self.teamColor == TeamColor.WHITE
    

    def IsBlack(self):
        return self.teamColor == TeamColor.BLACK


    def GetRank(self):
        return pieceTypeToRank[self.pieceType]


class Move():
    def __init__(self, board, fromRow, fromCol, toRow, toCol):
        self.board = board
        self.fromRow = fromRow
        self.fromCol = fromCol
        self.toRow = toRow
        self.toCol = toCol

        self.__isValid = False
        self.__killsEnemy = False
        self.__killsKing = False
        self.__pawnReplace = False

        self.CalculateMoveInfo()


    def CalculateMoveInfo(self):
        self.__isValid = self.__IsValidMove()


    def IsValid(self):
        return self.__isValid


    def KillsEnemy(self):
        return self.__killsEnemy


    def KillsKing(self):
        return self.__killsKing


    def PawnReplace(self):
        return self.__pawnReplace


    def FromEqualsTo(self):
        return self.fromRow == self.toRow and self.fromCol == self.toCol


    def IsInsideTheBoard(self):
        return self.fromRow in range(8) and self.fromCol in range(8) and self.toRow in range(8) and self.toCol in range(8)


    def IsDiagonal(self):
        return abs(self.fromRow - self.toRow) == abs(self.fromCol - self.toCol)


    def IsStraight(self):
        return self.fromRow == self.toRow or self.fromCol == self.toCol
    

    def GetFromPiece(self):
        return self.board[self.fromRow][self.fromCol]


    def GetToPiece(self):
        return self.board[self.toRow][self.toCol]


    def __IsValidMove(self):
        valid = False
        fromPieceType = self.GetFromPiece().pieceType

        if fromPieceType == PieceType.PAWN:
            valid = self.__CheckPawnMove()
        elif fromPieceType == PieceType.ROOK:
            valid = self.__CheckRookMove()
        elif fromPieceType == PieceType.HORSE:
            valid = self.__CheckHorseMove()
        elif fromPieceType == PieceType.BISHOP:
            valid = self.__CheckBishopMove()
        elif fromPieceType == PieceType.QUEEN:
            valid = self.__CheckQueenMove()
        elif fromPieceType == PieceType.KING:
            valid = self.__CheckKingMove()

        if valid:
            if self.__BothSquaresOccupied():
                self.__killsEnemy = True
                self.__killsKing = self.GetToPiece().pieceType == PieceType.KING
            if(fromPieceType == PieceType.PAWN):
                self.__pawnReplace = (self.GetFromPiece().IsWhite() and self.toRow == 7) or (self.GetFromPiece().IsBlack() and self.toRow == 0)    
        return valid


    def __PreliminaryValidMoveCheck(self):
        if not self.IsInsideTheBoard() or self.FromEqualsTo() or self.GetFromPiece() == None or self.__BothSquaresSameTeam():
            return False
        return True


    def __CheckPawnMove(self):
        if not self.__PreliminaryValidMoveCheck():
            return False
        
        isInStartingPosition = (self.GetFromPiece().IsWhite() and self.fromRow == 1) or (self.GetFromPiece().IsBlack() and self.fromRow == 6)
        validRowDir = 1 if self.GetFromPiece().IsWhite() else -1
        moveDist = max(abs(self.fromRow - self.toRow), abs(self.fromCol - self.toCol))
        moveRowDir = (self.toRow - self.fromRow)

        # Normalize moveRowDir
        moveRowDir = int(moveRowDir / abs(moveRowDir)) if moveRowDir != 0 else moveRowDir

        if validRowDir != moveRowDir:
            return False

        if self.IsDiagonal() and moveDist == 1 and self.GetToPiece() != None and self.GetFromPiece().IsEnemyWith(self.GetToPiece()):
            return True

        if self.IsStraight():
            if moveDist == 1:
                return self.GetToPiece() == None
            elif moveDist == 2 and not self.__StraightIntersects():
                return self.GetToPiece() == None and isInStartingPosition        
        return False


    def __CheckRookMove(self):
        if self.__PreliminaryValidMoveCheck() and self.IsStraight() and not self.__StraightIntersects():
            return True
        return False


    def __CheckHorseMove(self):
        if not self.__PreliminaryValidMoveCheck():
            return False

        rowDist = abs(self.fromRow - self.toRow)
        colDist = abs(self.fromCol - self.toCol)
        if (rowDist == 2 and colDist == 1) or (rowDist == 1 and colDist == 2):
            return True
        return False


    def __CheckBishopMove(self):
        if self.__PreliminaryValidMoveCheck() and self.IsDiagonal() and not self.__DiagonalIntersects():
            return True
        return False


    def __CheckQueenMove(self):
        if self.__PreliminaryValidMoveCheck():
            if (self.IsStraight() and not self.__StraightIntersects()) or (self.IsDiagonal() and not self.__DiagonalIntersects()):
                return True
        return False


    def __CheckKingMove(self):
        if self.__PreliminaryValidMoveCheck():
            if (self.IsStraight() and not self.__StraightIntersects()) or (self.IsDiagonal() and not self.__DiagonalIntersects()):
                # Assure move distance no more than 1 adjacent square
                return abs(self.fromRow - self.toRow) <= 1 and abs(self.fromCol - self.toCol) <= 1
        return False


    def __BothSquaresOccupied(self):
        return self.GetFromPiece() != None and self.GetToPiece() != None


    def __BothSquaresSameTeam(self):
        if self.__BothSquaresOccupied():
            return self.GetFromPiece().teamColor == self.GetToPiece().teamColor
        return False


    def __DiagonalIntersects(self):
        assert(self.IsDiagonal())

        # In diagonal, row distance = column distance so we only check row
        # Intersect can only occure when there is at least 1 square between the move
        if(abs(self.fromRow - self.toRow) >= 2):
            rowDir = self.toRow - self.fromRow
            colDir = self.toCol - self.fromCol
            
            # Normalize direction
            rowDir = int(rowDir / abs(rowDir)) if rowDir != 0 else rowDir
            colDir = int(colDir / abs(colDir)) if colDir != 0 else colDir

            # Stop one square before destination
            step = 1
            while(self.fromRow + step * rowDir != self.toRow):
                curRow = self.fromRow + step * rowDir
                curCol = self.fromCol + step * colDir
                step += 1
                if self.board[curRow][curCol] != None:
                    return True
        return False


    def __StraightIntersects(self):
        assert(self.IsStraight())

        # Intersect can only occure when there is at least 1 square between the move
        if(abs(self.fromRow - self.toRow) >= 2 or abs(self.fromCol - self.toCol) >= 2):
            # (Straight move, so one of them is zero)
            rowDir = self.toRow - self.fromRow
            colDir = self.toCol - self.fromCol

            # Normalize direction
            rowDir = int(rowDir / abs(rowDir)) if rowDir != 0 else rowDir
            colDir = int(colDir / abs(colDir)) if colDir != 0 else colDir
            
            # Stop one square before destination
            step = 1
            while(not (self.fromRow + step * rowDir == self.toRow and self.fromCol + step * colDir == self.toCol)):
                curRow = self.fromRow + step * rowDir
                curCol = self.fromCol + step * colDir
                step += 1
                if self.board[curRow][curCol] != None:
                    return True
        return False   


class Chess(Game):
    def __init__(self, play_id, player1_id, player2_id, player1_username, player2_username, tournament_id, phase):
        super().__init__(play_id)
        self.players = [player1_id, player2_id]
        self.gametype = GameType.CHESS
        self.board = [[Piece.CreateFromChar(startingBoardString[r][c]) for c in range(8)] for r in range(8)]
        self.player1 = player1_id
        self.player2 = player2_id
        self.player1_username = player1_username
        self.player2_username = player2_username
        self.tournament_id = tournament_id
        self.phase = phase

        self._turn = 1
        self._pieces_count = 32
        self._game_over = False
        self._winner_exists = False

    def GetStateJson(self):
        return {'play_id': self.play_id, 'gametype': 'chess', 'board': self.GetBoardToString(), 'player1': self.player1, 'player2': self.player2, \
            'player1_username': self.player1_username, 'player2_username': self.player2_username, 'tournament_id': self.tournament_id, \
                'phase': self.phase, 'turn': self._turn, 'pieces_count': self._pieces_count, 'game_over': self._game_over, \
                    'winner_exists': self._winner_exists}

    def LoadStateFromJson(self, data_json):
        self.play_id = data_json.get('play_id')
        self.players = [data_json.get('player1'), data_json.get('player2')]
        self.LoadStateFromString(data_json.get('board'))
        self.player1 = data_json.get('player1')
        self.player2 = data_json.get('player2')
        self.player1_username = data_json.get('player1_username')
        self.player2_username = data_json.get('player2_username')
        self.tournament_id = data_json.get('tournament_id')
        self.phase = data_json.get('phase')
        self._turn = data_json.get('turn')
        self._pieces_count = data_json.get('pieces_count')
        self._game_over = data_json.get('game_over')
        self._winner_exists = data_json.get('winner_exists')
        

    def PlayMove(self, rowFrom, colFrom, rowTo, colTo):
        if self.GameIsOver() or  self.board[rowFrom][colFrom] == None or self.board[rowFrom][colFrom].teamColor != self.WhoPlaysWB():
            return False

        move = Move(self.board, rowFrom, colFrom, rowTo, colTo)

        if not move.IsValid():
            return False

        self.__ApplyMove(move)
        self._turn += 1

        self.PrintChessBoard()
        return True


    def PlayMoveOriginalInput(self, inFrom, inTo):
        if not (len(inFrom) == 2 and len(inTo) == 2) or \
            not (chessColumnToIndex.get(inFrom[0].capitalize()) != None and chessColumnToIndex.get(inTo[0].capitalize()) != None) or \
                not (inFrom[1].isdigit() and inTo[1].isdigit()):
            return False

        rowFrom = int(inFrom[1]) - 1
        colFrom = chessColumnToIndex[inFrom[0].capitalize()]
        rowTo = int(inTo[1]) - 1
        colTo = chessColumnToIndex[inTo[0].capitalize()]
        return self.PlayMove(rowFrom, colFrom, rowTo, colTo)


    def __ApplyMove(self, move):
        if move.KillsEnemy():
            self._pieces_count -= 1
        
        if move.KillsKing():
            self._game_over = True
            self._winner_exists = True

        if self._pieces_count == 2:
            self._game_over = True

        self.board[move.toRow][move.toCol] = self.board[move.fromRow][move.fromCol]
        self.board[move.fromRow][move.fromCol] = None

        if move.PawnReplace():
            self.board[move.toRow][move.toCol] = Piece(PieceType.QUEEN, self.WhoPlaysWB()) #self.__PopStrongerDeadPiece(self.WhoPlays())


    def WhoPlays(self):
        return self.player1 if self._turn % 2 == 1 else self.player2


    def WhoPlaysWB(self):
        return TeamColor.WHITE if self._turn % 2 == 1 else TeamColor.BLACK


    def LastPlayerPlayed(self):
        if self._turn == 1:
            return None
        return self.player1 if self.WhoPlays() == self.player2 else self.player2


    def ThereIsAWinner(self):
        return self._winner_exists


    def GetTheWinner(self):
        return self.LastPlayerPlayed() if self.ThereIsAWinner() else None


    def GetTheLoser(self):
        return self.WhoPlays() if self.ThereIsAWinner() else None


    def GameIsOver(self):
        return self._game_over


    def IsADraw(self):
        return self.GameIsOver() and not self.ThereIsAWinner()


    def GetBoardToString(self):
        boardChar = [['0' if not self.board[r][c] else self.board[r][c].GetCharCode() for c in range(8)] for r in range(8)]
        boardString = ''
        for row in boardChar:
            boardString += ''.join(row)
        return boardString


    def PrintChessBoard(self):
        boardString = self.GetBoardToString()
        for r in range(7, -1, -1):
            print(boardString[r * 8 : r * 8 + 8] + "   {}".format(r + 1))

        print('\nABCDEFGH')


    def LoadStateFromString(self, stateString):
        assert(len(stateString) == 64)
        self.board = []
        self._pieces_count = 0
        for r in range(8):
            self.board.append(list(stateString[r * 8 : r * 8 + 8]))

        for r in range(8):
            for c in range(8):
                self.board[r][c] = Piece.CreateFromChar(self.board[r][c])
                self._pieces_count += 1 if self.board[r][c] else 0


    def GetState(self):
        return {'player1_id': self.player1, 'player2_id': self.player2, 'gamestate': self.GetBoardToString(), 'gameover': self.GameIsOver(), 'phase': self.phase,\
             'winner': self.GetTheWinner(), 'gametype': GameType.FromEnumToString(self.gametype), 'isADraw': self.IsADraw(), 'tournament_id': self.tournament_id,\
                 'player1_username': self.player1_username, 'player2_username': self.player2_username, 'play_id': self.play_id, 'who_plays': self.WhoPlays()}