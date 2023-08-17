import chess
import time
from antiChess import AntiChess
from human import Human

class Game():
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
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

    def PlayGame(self):

        #print(self.board.turn)
        #print(self.board, end = '\n\n')   
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1         
        while self.board.outcome() == None and (not self.board.can_claim_draw()):
            t = time.time()
            self.player1.turn_start_time = t
            valid_move = self.MakeMove(self.board, self.player1)
            self.player1.time_used += time.time() - t
            if not valid_move:
                break
             
            if self.board.outcome() != None:
                break
            
            t = time.time()
            self.player2.turn_start_time = t
            valid_move = self.MakeMove(self.board, self.player2)
            self.player2.time_used += time.time() - t
            if not valid_move:
                break 

        print(self.board.outcome(), self.board.can_claim_draw())
        print(self.board.fullmove_number)

        print("Player 1 used: ", self.player1.time_used)
        print("Player 2 used: ", self.player2.time_used)

        startingBoard = AntiChess()
        print(startingBoard.variation_san(self.board.move_stack))
