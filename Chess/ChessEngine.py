class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        #ściąga
       # ["00", "01", "02", "03", "04", "05", "06", "07"],
       # ["10", "11", "12", "13", "14", "15", "16", "17"],
       # ["20", "21", "22", "23", "24", "25", "26", "17"],
       # ["30", "31", "32", "33", "34", "35", "36", "37"],
       # ["40", "41", "42", "43", "44", "36", "46", "47"],
       # ["50", "51", "52", "53", "54", "55", "56", "57"],
       # ["60", "61", "62", "63", "64", "65", "66", "67"],
       # ["70", "71", "72", "73", "74", "75", "76", "77"]]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False;
        self.staleMate = False;
        self.enPassantPossible = ()
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castlingRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        #zmiana zapisanej pozycji króli
        if (move.pieceMoved == 'wK'):
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif (move.pieceMoved == 'bK'):
            self.blackKingLocation = (move.endRow, move.endCol)

        #promocja
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #bicie w przelocie
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'

        #zmiana pola enPassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            if move.pieceMoved[0] == 'w':
                self.enPassantPossible = (move.startRow - 1, move.startCol)
            else:
                self.enPassantPossible = (move.startRow + 1, move.startCol)
        else:
            self.enPassantPossible = ()

        #roszada
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:        #krótka roszada
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol +1]
                self.board[move.endRow][move.endCol +1] = "--"
            else:                                       #długa roszada
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol -2]
                self.board[move.endRow][move.endCol -2] = "--"
        #prawa do roszady
        self.updateCastleRights(move)
        self.castlingRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                   self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        if self.moveLog == []:
            return
        move = self.moveLog.pop()
        self.board[move.endRow][move.endCol] = move.pieceCaptured
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove

        #zmiana zapisanej pozycji króli
        if (move.pieceMoved == 'wK'):
            self.whiteKingLocation = (move.startRow, move.startCol)
        elif (move.pieceMoved == 'bK'):
            self.blackKingLocation = (move.startRow, move.startCol)

        #cofnięcie bicia w przelocie
        if move.isEnPassantMove:
            self.board[move.endRow][move.endCol] = '--'
            self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enPassantPossible = (move.endRow, move.endCol)

        #cofnięcie ruchu piona o 2 pola
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ()

        #cofnięcie roszady
        self.castlingRightsLog.pop()
        newRights = self.castlingRightsLog[-1]
        self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:        #krótka roszada
                self.board[move.endRow][move.endCol +1] = self.board[move.endRow][move.endCol -1]
                self.board[move.endRow][move.endCol -1] = "--"
            else:                                       #długa roszada
                self.board[move.endRow][move.endCol -2] = self.board[move.endRow][move.endCol +1]
                self.board[move.endRow][move.endCol +1] = "--"

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):

        #podtrzymanie informacji
        tmpEnPassantPossible = self.enPassantPossible
        tmpCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                       self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        #usunięcie niedozwolonych ruchów z listy moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves)-1, -1, -1): ##iterowanie od końca
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  ##usunięcie ruchu z listy
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        #sprawdzenie warunku zakończenia
        if len(moves) ==0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        #przywrócenie informacji
        self.enPassantPossible = tmpEnPassantPossible
        self.currentCastlingRight = tmpCastleRights
        return moves

    def inCheck(self):                          ##czy gracz jest szachowany
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):          ##czy pole jest atakowane
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)        #Funkcja wywołująca funkcję w zależności od znaku 'piece'
        return moves

    # FUNKCJE GET MOVES

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r,c), (r-1,c), self.board))                      #Zwykły ruch do przodu
                if r == 6 and self.board[r-2][c] == '--':
                    moves.append(Move((r,c), (r-2,c), self.board))         #Ruch do przodu o 2 pola
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))              #Bicie w lewo
                elif (r-1, c-1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r-1, c-1), self.board, isEnPassantMove = True))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append((Move((r,c), (r-1, c+1), self.board)))             #Bicie w prawo
                elif (r-1, c+1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r-1, c+1), self.board, isEnPassantMove = True))
        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))                    #Zwykły ruch do przodu
                if r == 1 and self.board[r+2][c] == '--':
                    moves.append(Move((r, c), (r+2, c), self.board))       #Ruch do przodu o 2 pola
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))              #Bicie w lewo
                elif (r+1, c-1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r+1, c-1), self.board, isEnPassantMove = True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append((Move((r, c), (r+1, c+1), self.board)))            #Bicie w prawo
                elif (r+1, c+1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r+1, c+1), self.board, isEnPassantMove = True))

    def getRookMoves(self, r, c, moves):
        checkedSq = ''
        if self.whiteToMove:
            i = 1
            while (r-i <= 7):
                checkedSq = self.board[r-i][c][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r-i,c), self.board))      #Ruch w górę
                    i += 1
                elif (checkedSq == 'b'):
                    moves.append(Move((r,c), (r-i,c), self.board))      #Bicie w górę
                    break
                elif (checkedSq == 'w'):
                    break
            i = 1
            while (r+i <= 7):
                checkedSq = self.board[r+i][c][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r+i,c), self.board))      #Ruch w dół
                    i += 1
                elif (checkedSq == 'b'):
                    moves.append(Move((r,c), (r+i,c), self.board))      #Bicie w dół
                    break
                elif (checkedSq == 'w'):
                    break
            i = 1
            while (c-i >= 0):
                checkedSq = self.board[r][c-i][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r,c-i), self.board))      #Ruch w lewo
                    i += 1
                elif (checkedSq == 'b'):
                    moves.append(Move((r,c), (r,c-i), self.board))      #Bicie w lewo
                    break
                elif (checkedSq == 'w'):
                    break
            i = 1
            while (c+i <= 7):
                checkedSq = self.board[r][c+i][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r,c+i), self.board))      #Ruch w prawo
                    i += 1
                elif (checkedSq == 'b'):
                    moves.append(Move((r,c), (r,c+i), self.board))      #Bicie w prawo
                    break
                elif (checkedSq == 'w'):
                    break
        else:
            i = 1
            while (r-i <= 7):
                checkedSq = self.board[r-i][c][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r-i,c), self.board))      #Ruch w górę
                    i += 1
                elif (checkedSq == 'w'):
                    moves.append(Move((r,c), (r-i,c), self.board))      #Bicie w górę
                    break
                elif (checkedSq == 'b'):
                    break
            i = 1
            while (r+i <= 7):
                checkedSq = self.board[r+i][c][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r+i,c), self.board))      #Ruch w dół
                    i += 1
                elif (checkedSq == 'w'):
                    moves.append(Move((r,c), (r+i,c), self.board))      #Bicie w dół
                    break
                elif (checkedSq == 'b'):
                    break
            i = 1
            while (c-i >= 0):
                checkedSq = self.board[r][c-i][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r,c-i), self.board))      #Ruch w lewo
                    i += 1
                elif (checkedSq == 'w'):
                    moves.append(Move((r,c), (r,c-i), self.board))      #Bicie w lewo
                    break
                elif (checkedSq == 'b'):
                    break
            i = 1
            while (c+i <= 7):
                checkedSq = self.board[r][c+i][0]
                if (checkedSq == '-'):
                    moves.append(Move((r,c), (r,c+i), self.board))      #Ruch w prawo
                    i += 1
                elif (checkedSq == 'w'):
                    moves.append(Move((r,c), (r,c+i), self.board))      #Bicie w prawo
                    break
                elif (checkedSq == 'b'):
                    break

    def getKnightMoves(self, r, c, moves):
        ##od 12 w kierunku wskazówek zegara
        if self.whiteToMove:                                                #Białe
            if r-2 in range(len(self.board)) and c+1 in range(len(self.board)):       #1
                if self.board[r-2][c+1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r-2, c+1), self.board))
            if r-1 in range(len(self.board)) and c+2 in range(len(self.board)):       #2
                if self.board[r-1][c+2][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r-1, c+2), self.board))
            if r+1 in range(len(self.board)) and c+2 in range(len(self.board)):       #3
                if self.board[r+1][c+2][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r+1, c+2), self.board))
            if r+2 in range(len(self.board)) and c+1 in range(len(self.board)):       #4
                if self.board[r+2][c+1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r+2, c+1), self.board))
            if r+2 in range(len(self.board)) and c-1 in range(len(self.board)):       #5
                if self.board[r+2][c-1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r+2, c-1), self.board))
            if r+1 in range(len(self.board)) and c-2 in range(len(self.board)):       #6
                if self.board[r+1][c-2][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r+1, c-2), self.board))
            if r-1 in range(len(self.board)) and c-2 in range(len(self.board)):       #7
                if self.board[r-1][c-2][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r-1, c-2), self.board))
            if r-2 in range(len(self.board)) and c-1 in range(len(self.board)):       #8
                if self.board[r-2][c-1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r-2, c-1), self.board))
        else:                                                                ##Czarne
            if r-2 in range(len(self.board)) and c+1 in range(len(self.board)):       #1
                if self.board[r-2][c+1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r-2, c+1), self.board))
            if r-1 in range(len(self.board)) and c+2 in range(len(self.board)):       #2
                if self.board[r-1][c+2][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r-1, c+2), self.board))
            if r+1 in range(len(self.board)) and c+2 in range(len(self.board)):       #3
                if self.board[r+1][c+2][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r+1, c+2), self.board))
            if r+2 in range(len(self.board)) and c+1 in range(len(self.board)):       #4
                if self.board[r+2][c+1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r+2, c+1), self.board))
            if r+2 in range(len(self.board)) and c-1 in range(len(self.board)):       #5
                if self.board[r+2][c-1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r+2, c-1), self.board))
            if r+1 in range(len(self.board)) and c-2 in range(len(self.board)):       #6
                if self.board[r+1][c-2][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r+1, c-2), self.board))
            if r-1 in range(len(self.board)) and c-2 in range(len(self.board)):       #7
                if self.board[r-1][c-2][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r-1, c-2), self.board))
            if r-2 in range(len(self.board)) and c-1 in range(len(self.board)):       #8
                if self.board[r-2][c-1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r-2, c-1), self.board))

    def getBishopMoves(self, r, c, moves):
        if self.whiteToMove:                                            # BIALE
            i = 1
            while (r-i in range(len(self.board)) and c-i in range(len(self.board))):    #W lewo w górę
                if self.board[r-i][c-i][0] == '-':
                    moves.append(Move((r,c), (r-i, c-i), self.board))
                    i += 1
                elif self.board[r-i][c-i][0] == 'b':
                    moves.append(Move((r,c), (r-i, c-i), self.board))
                    break
                else:
                    break
            i = 1
            while (r - i in range(len(self.board)) and c + i in range(len(self.board))):  # W prawo w górę
                if self.board[r - i][c + i][0] == '-':
                    moves.append(Move((r, c), (r - i, c + i), self.board))
                    i += 1
                elif self.board[r - i][c + i][0] == 'b':
                    moves.append(Move((r, c), (r - i, c + i), self.board))
                    break
                else:
                    break
            i = 1
            while (r + i in range(len(self.board)) and c + i in range(len(self.board))):  # W prawo w dół
                if self.board[r + i][c + i][0] == '-':
                    moves.append(Move((r, c), (r + i, c + i), self.board))
                    i += 1
                elif self.board[r + i][c + i][0] == 'b':
                    moves.append(Move((r, c), (r + i, c + i), self.board))
                    break
                else:
                    break
            i = 1
            while (r + i in range(len(self.board)) and c - i in range(len(self.board))):  # W lewo w dół
                if self.board[r + i][c - i][0] == '-':
                    moves.append(Move((r, c), (r + i, c - i), self.board))
                    i += 1
                elif self.board[r + i][c - i][0] == 'b':
                    moves.append(Move((r, c), (r + i, c - i), self.board))
                    break
                else:
                    break
        else:                                                               #CZARNE
            i = 1
            while (r - i in range(len(self.board)) and c - i in range(len(self.board))):  # W lewo w górę
                if self.board[r - i][c - i][0] == '-':
                    moves.append(Move((r, c), (r - i, c - i), self.board))
                    i += 1
                elif self.board[r - i][c - i][0] == 'w':
                    moves.append(Move((r, c), (r - i, c - i), self.board))
                    break
                else:
                    break
            i = 1
            while (r - i in range(len(self.board)) and c + i in range(len(self.board))):  # W prawo w górę
                if self.board[r - i][c + i][0] == '-':
                    moves.append(Move((r, c), (r - i, c + i), self.board))
                    i += 1
                elif self.board[r - i][c + i][0] == 'w':
                    moves.append(Move((r, c), (r - i, c + i), self.board))
                    break
                else:
                    break
            i = 1
            while (r + i in range(len(self.board)) and c + i in range(len(self.board))):  # W prawo w dół
                if self.board[r + i][c + i][0] == '-':
                    moves.append(Move((r, c), (r + i, c + i), self.board))
                    i += 1
                elif self.board[r + i][c + i][0] == 'w':
                    moves.append(Move((r, c), (r + i, c + i), self.board))
                    break
                else:
                    break
            i = 1
            while (r + i in range(len(self.board)) and c - i in range(len(self.board))):  # W lewo w dół
                if self.board[r + i][c - i][0] == '-':
                    moves.append(Move((r, c), (r + i, c - i), self.board))
                    i += 1
                elif self.board[r + i][c - i][0] == 'w':
                    moves.append(Move((r, c), (r + i, c - i), self.board))
                    break
                else:
                    break

    def getKingMoves(self, r, c, moves):

        if self.whiteToMove:
            if r-1 in range(len(self.board)):                                           #W górę
                if self.board[r-1][c][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r-1, c), self.board))
            if r-1 in range(len(self.board)) and c+1 in range(len(self.board)) :        #W prawo w górę
                if self.board[r-1][c+1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r-1, c+1), self.board))
            if c+1 in range(len(self.board)):                                           #W prawo
                if self.board[r][c+1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r, c+1), self.board))
            if r+1 in range(len(self.board)) and c+1 in range(len(self.board)) :        #W prawo w dół
                if self.board[r+1][c+1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r+1, c+1), self.board))
            if r+1 in range(len(self.board)):                                           #W dół
                if self.board[r+1][c][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r+1, c), self.board))
            if r+1 in range(len(self.board)) and c-1 in range(len(self.board)) :        #W lewo w dół
                if self.board[r+1][c-1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c-1 in range(len(self.board)):                                           #W lewo
                if self.board[r][c-1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r, c-1), self.board))
            if r-1 in range(len(self.board)) and c-1 in range(len(self.board)) :        #W lewo w górę
                if self.board[r-1][c-1][0] in ('-', 'b'):
                    moves.append(Move((r, c), (r-1, c-1), self.board))
        else:                                                                       ## CZARNE
            if r-1 in range(len(self.board)):                                           #W górę
                if self.board[r-1][c][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r-1, c), self.board))
            if r-1 in range(len(self.board)) and c+1 in range(len(self.board)) :        #W prawo w górę
                if self.board[r-1][c+1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r-1, c+1), self.board))
            if c+1 in range(len(self.board)):                                           #W prawo
                if self.board[r][c+1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r, c+1), self.board))
            if r+1 in range(len(self.board)) and c+1 in range(len(self.board)) :        #W prawo w dół
                if self.board[r+1][c+1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r+1, c+1), self.board))
            if r+1 in range(len(self.board)):                                           #W dół
                if self.board[r+1][c][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r+1, c), self.board))
            if r+1 in range(len(self.board)) and c-1 in range(len(self.board)) :        #W lewo w dół
                if self.board[r+1][c-1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c-1 in range(len(self.board)):                                           #W lewo
                if self.board[r][c-1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r, c-1), self.board))
            if r-1 in range(len(self.board)) and c-1 in range(len(self.board)) :        #W lewo w górę
                if self.board[r-1][c-1][0] in ('-', 'w'):
                    moves.append(Move((r, c), (r-1, c-1), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r,c, moves)
        self.getBishopMoves(r,c, moves)

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r,c+2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove=True))


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                  "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        #promocja pionków
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        #bicie w przelocie
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            if self.pieceMoved == 'wp':
                self.pieceCaptured = 'bp'
            else:
                self.pieceCaptured = 'wp'

        #roszada
        self.isCastleMove = isCastleMove

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def checkIfInBoard(self, r, c):
        if (r in range(8) and c in range(8)):
            return True
        else:
            return False

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs