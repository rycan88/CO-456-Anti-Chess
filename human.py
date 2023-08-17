import chess

class Human():
    def __init__(self):
        self.time_used = 0
        self.opponent = None
    def getMove(self, board: chess.Board):
        while True:
            print("Possible Moves are ", tuple(board.generate_legal_moves()))
            try:               
                inp = input("Enter your move: ")
                move = chess.Move.from_uci(inp)
                if board.is_legal(move):
                    return move
                print("INVALID MOVE")
            except:
                print("INVALID MOVE")
                pass