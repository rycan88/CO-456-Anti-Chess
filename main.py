import chess, chess.gaviota
import sys
import chess.svg
from human import Human
from graphicBoard import GraphicBoard
from antiChessBot import *

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "white":
            player1 = BotLevel_3(chess.WHITE)
            player2 = Human()
        elif sys.argv[1] == "black":
            player1 = Human()
            player2 = BotLevel_3(chess.BLACK)
    else:
        player1 = Human()
        player2 = BotLevel_3(chess.BLACK)
        #player1 = BotLevel_3(chess.WHITE)
        #player2 = BotLevel_3(chess.BLACK)

    #player1 = Human()
    #player2 = Human()


    board = GraphicBoard(player1, player2)
    board.run()

main()