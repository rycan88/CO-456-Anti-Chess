import chess
import time
from antiChess import AntiChess
from human import Human

class Game():
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        player1.opponent = self.player2
        player2.opponent = self.player1   
        self.board = AntiChess()
    def MakeMove(self, board: chess.Board, player):
        move = player.getMove(board.copy())
        if type(player) != Human:
            print(move)
        if not board.is_legal(move):
            #print("ILLEGAL MOVE")
            return False

        board.push(move)

        print("WHITE" if board.turn else "BLACK")
        print(player.time_used)
        print(board, end = '\n\n') 
        
        return True


