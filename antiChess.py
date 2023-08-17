import chess

class AntiChess(chess.Board):
    Bitboard = int
    BB_ALL = 0xffff_ffff_ffff_ffff
    def generate_legal_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL):
        hasCapture = False
        for move in super().generate_legal_moves():
            if self.is_capture(move):
                hasCapture = True
                yield move
        if not hasCapture:
            yield from super().generate_legal_moves()

    def is_legal(self, move):
        return (move in tuple(self.legal_moves))
