import chess, chess.gaviota
import random, math, time
import chess.svg

#--------------------------------------------------------------------------------------------HUMAN------------------------------------------------------------------------------------

class AntiChessBot():
    def __init__(self, color):
        self.opponent = None
        self.color = color
        self.turn_start_time = 0
        self.time_used = 0
        self.CalculatedBoards = {}

    def getRandomMove(self, board: chess.Board): # Randomly chooses a legal move
        return random.choice(tuple(board.legal_moves))
    
    # Returns True if at least one side only has their king left, and False otherwise
    def getPieceCount(self, board: chess.Board):
        piece_count = 0
        for pieceNum in range(1, 7):
            piece_count += len(board.pieces(pieceNum, chess.WHITE))
            piece_count += len(board.pieces(pieceNum, chess.BLACK))
        return piece_count

    def getSquaresAround(self, square: chess.Square):
        Around = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (-1, -1))
        Box = []
        for around in Around:
            new_square = square + 8 * around[1] + around[0]
            if 0 <= new_square < 64 and abs((square % 8) - (new_square % 8)) == 1: 
                Box.append(new_square)
        return Box

    def getTablebaseMove(self, board: chess.Board):
        tablebase = chess.gaviota.open_tablebase("tablebase")

        bestMove = None
        highest = -math.inf
        for move in board.legal_moves:

            new_board = board.copy()
            new_board.push(move)

            # The tablebase gives positive number if the player to move is winning, negative if they are losing
            score = tablebase.probe_dtm(new_board)
            isWinning = tablebase.probe_wdl(new_board)
            
            score = 500 - abs(score)
            if isWinning == 0:
                score = 0

            # On the child board, it is the opponents turn to move. So if "isWinning" is 1 then the opponent is winning
            # So we want to minimize the score which we do by negating the score
            elif isWinning == 1:
                score *= -1

            if score > highest:
                highest = score
                bestMove = move
            elif score == highest:
                if score == 0:
                    if board.piece_at(bestMove.from_square).piece_type == chess.PAWN:
                        continue
                    if board.piece_at(move.from_square).piece_type == chess.PAWN:
                        bestMove = move
                        continue

                bestMove = random.choice((bestMove, move))

        print(highest, bestMove)
        return bestMove            

    def isLateEndGame(self, board: chess.Board):
        p1_piece_count = 0
        p2_piece_count = 0
        for pieceNum in range(1, 7):
            p1_piece_count += len(board.pieces(pieceNum, chess.WHITE))
            p2_piece_count += len(board.pieces(pieceNum, chess.BLACK))
        
        return p1_piece_count == 1 or p2_piece_count == 1
        

#-------------------------------------------------------------------------------------------LEVEL 1-----------------------------------------------------------------------------------
# Randomly chooses a legal move
class BotLevel_1(AntiChessBot):
    def getMove(self, board):
        return self.getRandomMove(board)

class BotLevel_2(AntiChessBot):
    def getMove(self, board: chess.Board) -> chess.Move:
        if self.getPieceCount(board) <= 4 and self.isLateEndGame(board):
            return self.getTablebaseMove(board)
        
        LegalMoves = list(board.legal_moves)
        t = time.time()
        random.shuffle(LegalMoves)
        self.time_used += time.time() - t
        if (len(LegalMoves) == 1):
            return LegalMoves[0]

        highestScore = -math.inf
        bestMove = None       
        alpha = -math.inf
        beta = math.inf     
        for move in LegalMoves:
            new_board = board.copy()
            new_board.push(move)
            
            score = self.evaluateNode(new_board, 1, alpha, beta)    
            if score > highestScore:
                highestScore = score
                bestMove = move

            alpha = max(alpha, highestScore)
        print(highestScore, bestMove)
        return bestMove

    def evaluateNode(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        #print(depth, board.legal_moves.count())

        # It is a leaf node if the game ends or it reaches a certain depth with no captures
        if board.legal_moves.count() == 0 or (depth >= 4 and (board.legal_moves.count() > 8 or depth >= 10)): 
            score = self.evaluateBoard(board, depth)
            return score

        # If depth is even, we want to maximize score
        if depth % 2 == 0:
            highestScore = -math.inf            
            for move in board.legal_moves:
                new_board = board.copy()
                new_board.push(move)
                
                score = self.evaluateNode(new_board, depth + 1, alpha, beta)    
                
                
                highestScore = max(highestScore, score)
                
                alpha = max(alpha, highestScore)
                if beta <= alpha:
                    break

            return highestScore

        else: # If depth is odd, we want to minimize score
            lowestScore = math.inf            
            for move in board.legal_moves:
                new_board = board.copy()
                new_board.push(move)
                
                score = self.evaluateNode(new_board, depth + 1, alpha, beta)    

                lowestScore = min(lowestScore, score)
                beta = min(beta, lowestScore)

                if beta <= alpha:
                    break

            return lowestScore

    def evaluateBoard(self, board: chess.Board, depth: int) -> float:
        outcome = board.outcome()
        if outcome != None:
            if outcome.winner == None:
                return 0
            elif outcome.winner == self.color:
                return 10 ** 20 - depth
            else:
                return -10 ** 20 + depth

        PieceValue = {1: 1, 2: 1.2, 3: 1.2, 4: 1.4, 5: 3, 6: 1}
        ally_piece_count = 0
        enemy_piece_count = 0
        for pieceNum in range(1, 7):
            ally_piece_count += len(board.pieces(pieceNum, self.color)) * PieceValue[pieceNum]
            enemy_piece_count += len(board.pieces(pieceNum, not self.color)) * PieceValue[pieceNum]
        
        # Late game strat
        if ally_piece_count - enemy_piece_count > 1 and enemy_piece_count < 3:
            enemy_king_square = board.king(not self.color)
            new_board = board.copy()
            new_board.remove_piece_at(enemy_king_square)
            count = 0
            for square in self.getSquaresAround(enemy_king_square):
                count += new_board.is_attacked_by(self.color, square)
            ally_piece_count += (9 - count) * (10 ** -5)

            pawn_squares = board.pieces(chess.PAWN, self.color)

            for square in pawn_squares:
                if self.color == chess.WHITE:
                    ally_piece_count += (square // 8) * (10 ** -4)
                else:
                    ally_piece_count += (8 - square // 8) * (10 ** -4)                    
            
        return ally_piece_count - enemy_piece_count
# ---------------------------------------------------------------------------Level 3-------------------------------------------------------

class BotLevel_3(AntiChessBot):
    def getMove(self, board: chess.Board) -> chess.Move:
        if board.fullmove_number == 1:
            if self.color == chess.WHITE:
                move = chess.Move.from_uci("f2f3")      
            else:
                move = chess.Move.from_uci("f7f6")                      
            return move

        '''if board.fullmove_number == 2:
            if self.color == chess.WHITE:
                move = chess.Move.from_uci("e1f2")      
            else:
                move = chess.Move.from_uci("e8f7")                      
            return move'''

        if self.getPieceCount(board) <= 4:
            return self.getTablebaseMove(board)
        
        LegalMoves = list(board.legal_moves)

        if (len(LegalMoves) == 1):
            return LegalMoves[0]



        random.shuffle(LegalMoves)

        highestScore = -math.inf
        bestMove = None       
        alpha = -math.inf
        beta = math.inf     

        for move in LegalMoves:
            new_board = board.copy()
            new_board.push(move)

            score = self.evaluateNode(new_board, 1, not board.is_capture(move), alpha, beta)    
            if score > highestScore:
                highestScore = score
                bestMove = move

            alpha = max(alpha, highestScore)
        print(highestScore, bestMove)
        return bestMove

    def evaluateNode(self, board: chess.Board, depth: int, calculationDepth: int, alpha: float, beta: float) -> float:
        #print(depth, board.legal_moves.count())
        moveCount = board.legal_moves.count()
        if self.time_used + (time.time() - self.turn_start_time) >= 175:
            if moveCount == 0 or depth >= 3: 
                score = self.evaluateBoard(board, depth)
                return score        
        elif self.time_used + (time.time() - self.turn_start_time) >= 160:
            if moveCount == 0 or (depth >= 3 and (moveCount > 3 or depth >= 10)): 
                score = self.evaluateBoard(board, depth)
                return score
        elif self.time_used + (time.time() - self.turn_start_time) >= 80 and self.opponent.time_used <= 2:
            if moveCount == 0 or (depth >= 3 and (moveCount > 3 or depth >= 10)): 
                score = self.evaluateBoard(board, depth)
                return score
        else:
            # It is a leaf node if the game ends or it reaches a certain depth with no captures
            if moveCount == 0 or ((calculationDepth >= 3 and depth >= 4 and moveCount > 4) or depth >= 10): 
                score = self.evaluateBoard(board, depth)
                return score

        # If depth is even, we want to maximize score
        if depth % 2 == 0:
            highestScore = -math.inf            
            for move in board.legal_moves:
                new_board = board.copy()
                new_board.push(move)
                
                score = self.evaluateNode(new_board, depth + 1, calculationDepth + (not (board.is_capture(move) or moveCount <= 2)), alpha, beta)    
                
                
                highestScore = max(highestScore, score)
                
                alpha = max(alpha, highestScore)
                if beta <= alpha:
                    break

            return highestScore

        else: # If depth is odd, we want to minimize score
            lowestScore = math.inf            
            for move in board.legal_moves:
                new_board = board.copy()
                new_board.push(move)
                
                score = self.evaluateNode(new_board, depth + 1, calculationDepth + (not (board.is_capture(move) or moveCount <= 2)), alpha, beta)    

                lowestScore = min(lowestScore, score)
                beta = min(beta, lowestScore)

                if beta <= alpha:
                    break

            return lowestScore

    def evaluateBoard(self, board: chess.Board, depth: int) -> float:
        outcome = board.outcome()
        if outcome != None:
            if outcome.winner == None or board.can_claim_draw():
                return 0
            elif outcome.winner == self.color:
                return 10 ** 20 - depth
            else:
                return -10 ** 20 + depth

        ally_piece_count = 0
        enemy_piece_count = 0

        for pieceNum in range(1, 7):
            ally_piece_count += len(board.pieces(pieceNum, self.color))
            enemy_piece_count += len(board.pieces(pieceNum, not self.color))

        if ally_piece_count + enemy_piece_count <= 4 and self.isLateEndGame(board):
            tablebase = chess.gaviota.open_tablebase("tablebase")
            score = tablebase.probe_dtm(board)
            isWinning = tablebase.probe_wdl(board)
            
            score = 500 - abs(score)
            if isWinning == 0:
                score = 0

            elif ((board.turn == (not self.color)) and isWinning == 1) or ((board.turn == self.color) and isWinning == -1):
                score *= -1
            return score


        PieceValue = {1: 1, 2: 1.2, 3: 1.2, 4: 1.4, 5: 3, 6: 1}  
        
        ally_piece_value = 0
        enemy_piece_value = 0    
        for pieceNum in range(1, 7):
            ally_piece_value += len(board.pieces(pieceNum, self.color)) * PieceValue[pieceNum]
            enemy_piece_value += len(board.pieces(pieceNum, not self.color)) * PieceValue[pieceNum]
        
        # Late game strat
        if ally_piece_count + enemy_piece_count <= 12:
            if ally_piece_value - enemy_piece_value >= 2 and enemy_piece_count <= 3:
                enemy_king_square = board.king(not self.color)
                new_board = board.copy()
                new_board.remove_piece_at(enemy_king_square)
                count = 0
                for square in self.getSquaresAround(enemy_king_square):
                    count += new_board.is_attacked_by(self.color, square)
                ally_piece_value += (9 - count) * (10 ** -5)

            pawn_squares = board.pieces(chess.PAWN, self.color)

            for square in pawn_squares:
                if self.color == chess.WHITE:
                    ally_piece_value += (square // 8) * (10 ** -4)
                else:
                    ally_piece_value += (8 - square // 8) * (10 ** -4)                    
            
        return ally_piece_value - enemy_piece_value





