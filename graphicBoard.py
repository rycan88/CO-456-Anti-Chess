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
        pygame.init()
        self.screen = pygame.display.set_mode(((8 + 4) * self.tileSize, 8 * self.tileSize))

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
                            if event.pos[0] >= 8 * self.tileSize or event.pos[1] >= 8 * self.tileSize:
                                continue
                            tileNum = self.positionToTile(event.pos)
                            if first == None:
                                if self.board.color_at(tileNum) == self.board.turn:
                                    first = tileNum
                                    self.clicked = first
                                    self.update()
                            else:
                                second = tileNum
                                move = chess.Move(first, second)
                                
                                self.clicked = None
                                # Checks if the move is legal
                                if self.board.is_legal(move):
                                    break
                                # Checks if the move is legal with a promotion
                                move.promotion = 5
                                if self.board.is_legal(move):
                                    promotion_y_start = 4 * self.tileSize
                                    Images = ["w_N", "w_B", "w_R", "w_Q"]
                                    for i in range(len(Images)):
                                        im = pygame.image.load("pieceImages/" + Images[i] + ".png")
                                        im = pygame.transform.scale(im, (self.tileSize, self.tileSize))
                                        self.screen.blit(im, ((8 + i) * self.tileSize, promotion_y_start))
                                    pygame.display.flip()
                                    promoted_piece = None
                                    while promoted_piece == None:
                                        for event in pygame.event.get():
                                            if event.type == pygame.QUIT:
                                                pygame.quit()
                                                sys.exit()
                                            if event.type == pygame.MOUSEBUTTONDOWN:
                                                if event.pos[0] >= 8 * self.tileSize and promotion_y_start <= event.pos[1] < promotion_y_start + self.tileSize:
                                                    promoted_piece = (event.pos[0] // self.tileSize) - 8 + 2
                                    move.promotion = promoted_piece
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
        self.screen.fill(Color(38,37,34))
        for y in range(8):
            for x in range(8): 
                if (x + y) % 2 == 0:
                    tileColor = beige
                else:
                    tileColor = green
                
                pygame.draw.rect(self.screen, tileColor, rect=(x * self.tileSize, y * self.tileSize, self.tileSize, self.tileSize))

                # Highlights the previous move
                if prevMove and (y * 8 + x) in (prevMove.from_square, prevMove.to_square):
                    surface = pygame.Surface((self.tileSize, self.tileSize))
                    surface.set_alpha(180)
                    surface.fill(Color(244,246,128))
                    self.screen.blit(surface, (x * self.tileSize, y * self.tileSize))

                # Highlights the square you click
                if self.clicked == (y * 8 + x):
                    surface = pygame.Surface((self.tileSize, self.tileSize))
                    surface.set_alpha(180)
                    surface.fill(Color(179, 31, 65))
                    self.screen.blit(surface, (x * self.tileSize, y * self.tileSize))
                tileNum = y * 8 + x

                # Draws the pieces on the board
                piece = self.board.piece_at(tileNum)
                if piece != None:
                    im = pygame.image.load("pieceImages/" + Images[piece.symbol()] + ".png")
                    im = pygame.transform.scale(im, (self.tileSize, self.tileSize))
                    self.screen.blit(im, (x * self.tileSize, y * self.tileSize))

        pygame.display.flip()
