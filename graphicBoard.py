# Example file showing a circle moving on screen
import sys
import pygame
from pygame import Color
from human import Human
from game import Game
from antiChessBot import *
from antiChess import AntiChess
from multiprocessing import Process

class GraphicBoard():
    def __init__(self, player1, player2):

        self.tileSize = 100
        self.pieces = ["b_R", "b_N", "b_B", "b_Q", "b_K", "b_B", "b_N", "b_R",
                      "b_P", "b_P", "b_P", "b_P", "b_P", "b_P", "b_P", "b_P",
                       None,  None,  None,  None,  None,  None,  None,  None, 
                       None,  None,  None,  None,  None,  None,  None,  None,
                       None,  None,  None,  None,  None,  None,  None,  None,
                       None,  None,  None,  None,  None,  None,  None,  None,
                      "w_P", "w_P", "w_P", "w_P", "w_P", "w_P", "w_P", "w_P", 
                      "w_R", "w_N", "w_B", "w_Q", "w_K", "w_B", "w_N", "w_R",]
        pygame.init()
        self.screen = pygame.display.set_mode((8 * self.tileSize, 8 * self.tileSize))

        self.player1 = player1
        self.player2 = player2
        player1.opponent = self.player2
        player2.opponent = self.player1
   
        self.board = AntiChess()
        self.clicked = None    
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    def positionToTile(self, tup):
        return (tup[1] // self.tileSize) * 8 + (tup[0] // self.tileSize)
    def run(self):
        clock = pygame.time.Clock()
        self.update()

        #print(self.board.turn)
        #print(self.board, end = '\n\n')   
        currentPlayer = self.player1
        while self.board.outcome() == None and (not self.board.is_fifty_moves()) and (not self.board.is_repetition()):
            self.checkEvents()
            t = time.time()
            currentPlayer.turn_start_time = t

            if type(currentPlayer) == Human:
                first = None
                second = None
                while second == None:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            tileNum = self.positionToTile(event.pos)
                            print(tileNum)
                            print(first, second)
                            if first == None:
                                if self.board.color_at(tileNum) == self.board.turn:
                                    first = tileNum
                                    self.clicked = first
                                    self.update()
                            else:
                                second = tileNum
                                move = chess.Move(first, second)
                                print(move, self.board.is_legal(move))
                                self.clicked = None
                                if self.board.is_legal(move):
                                    break
                                first = None
                                second = None
                                self.update()

            else:
                move = currentPlayer.getMove(self.board.copy())

            self.makeMove(move)            
            
            currentPlayer.time_used += time.time() - t
            
            currentPlayer = currentPlayer.opponent


        print(self.board.outcome(), self.board.can_claim_draw())
        print(self.board.fullmove_number)

        print("Player 1 used: ", self.player1.time_used)
        print("Player 2 used: ", self.player2.time_used)

        startingBoard = AntiChess()
        print(startingBoard.variation_san(self.board.move_stack))
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()

    def makeMove(self, move):
        self.board.push(move)
        self.update()

    
    def update(self):
        Images = {"p": "b_P", "n": "b_N", "b": "b_B", "r": "b_R", "q": "b_Q", "k": "b_K",
                  "P": "w_P", "N": "w_N", "B": "w_B", "R": "w_R", "Q": "w_Q", "K": "w_K"}
        green = Color(119,153,84)
        beige = Color(233,237,204)
        prevMove = None 
        if len(self.board.move_stack) > 0:
            prevMove = self.board.peek()
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("white")
        for y in range(8):
            for x in range(8): 
                if (x + y) % 2 == 0:
                    tileColor = beige
                else:
                    tileColor = green
                
                pygame.draw.rect(self.screen, tileColor, rect=(x * self.tileSize, y * self.tileSize, self.tileSize, self.tileSize))
                if prevMove and (y * 8 + x) in (prevMove.from_square, prevMove.to_square):
                    surface = pygame.Surface((self.tileSize, self.tileSize))
                    surface.set_alpha(180)
                    surface.fill(Color(244,246,128))
                    self.screen.blit(surface, (x * self.tileSize, y * self.tileSize))

                if self.clicked == (y * 8 + x):
                    surface = pygame.Surface((self.tileSize, self.tileSize))
                    surface.set_alpha(180)
                    surface.fill(Color(179, 31, 65))
                    self.screen.blit(surface, (x * self.tileSize, y * self.tileSize))
                tileNum = y * 8 + x

                piece = self.board.piece_at(tileNum)
                if piece != None:
                    im = pygame.image.load("pieceImages/" + Images[piece.symbol()] + ".png")
                    im = pygame.transform.scale(im, (self.tileSize, self.tileSize))
                    self.screen.blit(im, (x * self.tileSize, y * self.tileSize))
        # flip() the display to put your work on screen
        pygame.display.flip()
