import pygame
import sys
import constants as const
import pieces
from pygame.locals import *
import random

class Graphic:
    img = None
    rect = None

class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = (600, 600)
        self.board = None
        self.sprites = None
        self.available_moves = []
        self.current_piece = -1

        #Castling Flags
        self.wOO = True
        self.wOOO = True
        self.bOOO = True
        self.bOO = True

        #Check Flags
        self.wCheck = False
        self.bCheck = False

        #Win flags
        self.wWin = False
        self.bWin = False

        #En paasant flags
        self.enpassant = -1

        #King position tracking for check highlighting
        self.wKing = -100
        self.bKing = -100

        #Turn flag
        self.turn = "w"

    def on_init(self):
        pygame.init()
        self.__init__()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE)

        #self.load_FEN("8/6p1/8/8/8/8/1P6/8")
        self.load_FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        pygame.display.update()
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.turn == "b":
                print(self.turn)
                self.move_piece(*self.get_move("b"))

            pos = pygame.mouse.get_pos()
            idx = pos[0] // 75 + pos[1] // 75 * 8
            color, piece = self.decode_piece(self.board[idx])

            #If proper turn and no other piece selected, select the piece
            if (self.turn == "w" and color == "w") or (self.turn == "b" and color == "b"):
                self.current_piece = idx

            else:
                self.move_piece(self.current_piece, idx)
                print(self.wCheck, self.bCheck)


        if event.type == pygame.MOUSEBUTTONUP:
            if self.current_piece != -1:
                valid_moves = []
                self.available_moves = self.get_valid_moves(self.current_piece)
            #Render board
            self.on_render()

    def on_loop(self):
        if self.check_stalemate(self.turn):
            print("Stalemate bruh")
            self.on_init()
        pass

    def on_render(self):
        self.draw_board()
        if self.bCheck:
            kingLoc = self.bKing
            pygame.draw.circle(self._display_surf, (255, 0, 0), (kingLoc % 8 * 75 + 75/2, kingLoc//8*75 + 75/2), 38)
        if self.wCheck:
            kingLoc = self.wKing
            pygame.draw.circle(self._display_surf, (255, 0, 0), (kingLoc % 8 * 75 + 75/2, kingLoc//8*75 + 75/2), 38)

        for graphic in self.sprites:
            self._display_surf.blit(graphic.img, graphic.rect)

        for move in self.available_moves:
            pygame.draw.circle(self._display_surf, (0, 100, 0), (move % 8 * 75 + 75/2, move//8*75 + 75/2), 10)

        pygame.display.update()

        if self.bWin or self.wWin:
            self.on_init()

        pass

    def on_cleanup(self):
        pygame.quit()
        sys.exit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    #Draws the black and white checkerboard grid for the game
    def draw_board(self) -> bool:
        for i in range(8):
            for j in range(8):
                if (i+j)%2 == 0:
                    color = const.WHITE
                else:
                    color = const.LBROWN
                pygame.draw.rect(self._display_surf, color, (j*75, i*75, 75, 75), 0)

        return True

    def load_FEN(self, FEN) -> bool:
        row = 0
        column = 0
        board = []
        sprites = []
        for letter in FEN:
            position = len(board)
            if letter == "r":
                piece = pieces.PieceSprite(pieces.bRook)
                board.append(pieces.Piece.rook + pieces.Piece.black)
            elif letter == "n":
                piece = pieces.PieceSprite(pieces.bKnight)
                board.append(pieces.Piece.knight + pieces.Piece.black)
            elif letter == "b":
                piece = pieces.PieceSprite(pieces.bBishop)
                board.append(pieces.Piece.bishop + pieces.Piece.black)
            elif letter == "k":
                self.bKing = position
                piece = pieces.PieceSprite(pieces.bKing)
                board.append(pieces.Piece.king + pieces.Piece.black)
            elif letter == "q":
                piece = pieces.PieceSprite(pieces.bQueen)
                board.append(pieces.Piece.queen + pieces.Piece.black)
            elif letter == "p":
                piece = pieces.PieceSprite(pieces.bPawn)
                board.append(pieces.Piece.pawn + pieces.Piece.black)
            elif letter == "R":
                piece = pieces.PieceSprite(pieces.wRook)
                board.append(pieces.Piece.rook + pieces.Piece.white)
            elif letter == "N":
                piece = pieces.PieceSprite(pieces.wKnight)
                board.append(pieces.Piece.knight + pieces.Piece.white)
            elif letter == "B":
                piece = pieces.PieceSprite(pieces.wBishop)
                board.append(pieces.Piece.bishop + pieces.Piece.white)
            elif letter == "K":
                self.wKing = position
                piece = pieces.PieceSprite(pieces.wKing)
                board.append(pieces.Piece.king + pieces.Piece.white)
            elif letter == "Q":
                piece = pieces.PieceSprite(pieces.wQueen)
                board.append(pieces.Piece.queen + pieces.Piece.white)
            elif letter == "P":
                piece = pieces.PieceSprite(pieces.wPawn)
                board.append(pieces.Piece.pawn + pieces.Piece.white)
            elif letter == "/":
                row += 1
                continue
            else:
                column += int(letter)
                for i in range(int(letter)):
                    board.append(pieces.Piece.empty)
                continue

            graphic = self.get_graphic(piece, row, column)
            sprites.append(graphic)
            column += 1

        self.board = board
        self.sprites = sprites
        return True

    def get_graphic(self, piece, row, column) -> Graphic:

        graphic = Graphic()
        graphic.img = pygame.Surface([75, 75]).convert_alpha()
        pygame.transform.scale(piece.image, (75, 75), graphic.img)
        graphic.rect = graphic.img.get_rect(topleft=(75 * (column % 8), 75 * row))
        return graphic

    def decode_piece(self, piece) -> (str, str):
        if piece > 16:
            color = "b"
            piece -= 16
        else:
            color = "w"
            piece -= 8

        if piece == 2: return color, "Pawn"
        if piece == 3: return color, "Bishop"
        if piece == 4: return color, "Knight"
        if piece == 5: return color, "Rook"
        if piece == 6: return color, "Queen"
        if piece == 7: return color, "King"
        else: return "Error", "Error"

    def get_diagonals(self, sc) -> [int]:
        color, piece = self.decode_piece(self.board[sc])
        upleft, upright, downleft, downright = True, True, True, True
        moves = []
        i = 1

        while upleft or upright or downleft or downright:
            if upleft:
                if (sc-(i-1)*9) % 8 == 0 or sc-i*9 < 0:
                    upleft = False

                elif self.board[sc - i*9] != 1:
                    if color != self.decode_piece((self.board[sc-i*9]))[0]:
                        moves.append(sc-i*9)
                    upleft = False
                else:
                    moves.append(sc-i*9)

            if upright:
                if (sc - (i-1) * 7)%8 == 7 or sc-i*7 < 0:
                    upright = False

                elif self.board[sc - i * 7] != 1:
                    if color != self.decode_piece((self.board[sc - i * 7]))[0]:
                        moves.append(sc - i * 7)
                    upright = False
                else:
                    moves.append(sc - i * 7)

            if downleft:
                if (sc + i * 7)//8 == (sc+(i-1)*7)//8 or sc+i*7 > 63:
                    downleft = False

                elif self.board[sc + i * 7] != 1:
                    if color != self.decode_piece((self.board[sc + i * 7]))[0]:
                        moves.append(sc + i * 7)
                    downleft = False
                else:
                    moves.append(sc + i * 7)

            if downright:
                if (sc+(i-1)*9) % 8 == 7 or sc+i*9 > 63:
                    downright = False

                elif self.board[sc + i * 9] != 1:
                    if color != self.decode_piece((self.board[sc + i * 9]))[0]:
                        moves.append(sc + i * 9)
                    downright = False
                else:
                    moves.append(sc + i * 9)


            i += 1
        return moves

    def get_rows(self, sc) -> [int]:
        color, piece = self.decode_piece(self.board[sc])
        up, left, down, right = True, True, True, True
        moves = []
        i = 1

        while up or left or down or right:
            if up:
                if sc - i * 8 > 63 or sc - i * 8 < 0:
                    up = False

                elif self.board[sc - i * 8] != 1:
                    if color != self.decode_piece((self.board[sc - i * 8]))[0]:
                        moves.append(sc - i * 8)
                    up = False
                else:
                    moves.append(sc - i * 8)

            if left:
                if sc - i < sc//8*8:
                    left = False

                elif self.board[sc - i] != 1:
                    if color != self.decode_piece((self.board[sc - i]))[0]:
                        moves.append(sc - i)
                    left = False
                else:
                    moves.append(sc - i)

            if right:
                if sc + i > sc//8*8+7:
                    right = False

                elif self.board[sc + i] != 1:
                    if color != self.decode_piece((self.board[sc + i]))[0]:
                        moves.append(sc + i)
                    right = False
                else:
                    moves.append(sc + i)

            if down:
                if sc + i*8 > 63 or sc + i * 8 < 0:
                    down = False

                elif self.board[sc + i * 8] != 1:
                    if color != self.decode_piece((self.board[sc + i * 8]))[0]:
                        moves.append(sc + i * 8)
                    down = False
                else:
                    moves.append(sc + i * 8)

            i += 1
        return moves

    #Get a manhattan distance between the row/column of the source and destination |rdest-rsc| + |cdest-csc)|
    #A valid knight move should have distance of 3
    def rc_dist(self, sc, dest) -> int:
        sc_row = sc//8
        dest_row = dest//8
        sc_col = sc%8
        dest_col = dest%8

        return abs(sc_row - dest_row) + abs(sc_col - dest_col)

    #Get the available moves for a given piece in the form of an array of integer destinations.  Does not account for checks
    def get_available_moves(self, sc) -> [int]:
        color, piece = self.decode_piece(self.board[sc])
        moves = []
        if "Pawn" in piece:
            if color == "b":
                mult = 1
                start_row = 1
            else:
                mult = -1
                start_row = 6


            #Check for double move privs
            if sc//8 == start_row:
                if self.board[sc+8*mult] == 1 and self.board[sc+16*mult] == 1:
                    moves = [sc+8*mult, sc+16*mult]
                elif self.board[sc+8*mult] == 1:
                    moves = [sc+8*mult]
            else:
                if self.board[sc+8*mult] == 1:
                    moves = [sc+8*mult]

            # Check for en passant
            if sc == self.enpassant - 1 or sc == self.enpassant + 1:
                # Get enpassant square
                moves.append(self.enpassant + 8 * mult)

            #Get capture diagonals
            diag1 = sc + 8*mult + 1
            diag2 = sc + 8*mult - 1

            #Get distance for each diagonal, if distance is not equal to 2 it overflowed the board and is invalid
            dist1 = self.rc_dist(sc, diag1)
            dist2 = self.rc_dist(sc, diag2)

            #Check if dist is valid, square isnt empty, and destination piece is opposite color
            if dist1 == 2 and self.board[diag1] != 1 and color != self.decode_piece(self.board[diag1])[0]:
                moves.append(diag1)
            if dist2 == 2 and self.board[diag2] != 1 and color != self.decode_piece(self.board[diag2])[0]:
                moves.append(diag2)

        if "Bishop" in piece:
            moves = self.get_diagonals(sc)

        if "Knight" in piece:
            moves = []
            for move in [sc + 6, sc - 6, sc + 10, sc - 10, sc - 15, sc - 17, sc + 17, sc + 15]:
                if move > 63 or move < 0 or self.rc_dist(sc, move) not in [3]:
                    continue
                elif self.board[move] == 1:
                    moves.append(move)
                elif color != self.decode_piece(self.board[move])[0]:
                    moves.append(move)

        if "Rook" in piece:
            moves = self.get_rows(sc)

        if "Queen" in piece:
            moves = self.get_rows(sc) + self.get_diagonals(sc)

        if "King" in piece:
            if color == "w": attack_color = "b"
            else: attack_color = "w"

            attacked_squares = self.get_attacked_squares(attack_color)
            for move in [sc-9, sc-8, sc-7, sc+9, sc+8, sc+7, sc-1, sc+1]:
                if move > 63 or move < 0 or self.rc_dist(sc, move) > 2:
                    continue
                if color == self.decode_piece(self.board[move])[0]:
                    continue
                if move in attacked_squares:
                    continue
                else:
                    moves.append(move)

            if color == "b":
                OO = self.bOO
                OOO = self.bOOO
            else:
                OO = self.wOO
                OOO = self.wOOO

            if OO and self.board[sc+1] == 1 and self.board[sc+2] == 1 and {sc+1, sc+2} - attacked_squares == {sc+1, sc+2}:
                moves.append(sc+2)
            if OOO and self.board[sc-1] == 1 and self.board[sc-2] and self.board[sc-3] == 1 and {sc+1,sc+2,sc+3}-attacked_squares == {sc+1,sc+2,sc+3}:
                moves.append(sc-2)

        return moves

    #Gets the valid moves for a piece by accounting for checks
    def get_valid_moves(self, sc) -> [int]:
        available_moves = self.get_available_moves(sc)
        valid_moves = []
        for move in available_moves:
            if self.in_check(sc, move):
                continue
            else:
                valid_moves.append(move)

        return valid_moves

    #Check if the king can castle and return an array with valid directions (IE [queenside (OOO), kingside (OO)])
    def valid_castle(self, sc, dest) -> [str]:
        color, piece = self.decode_piece(self.board[sc])

        castle = []
        if piece != "King": return []

        king_rook = "Rook" in self.decode_piece(self.board[sc + 2])[1]
        queen_rook = "Rook" in self.decode_piece(self.board[sc - 3])[1]

        if color == "b":
            if dest == sc + 2 and self.bOO and king_rook:
                castle.append("OO")
            if dest == sc - 2 and self.bOOO and queen_rook:
                castle.append("OOO")

        if color == "w":
            if dest == sc + 2 and self.wOO and king_rook:
                castle.append("OO")
            if dest == sc - 2 and self.wOOO and queen_rook:
                castle.append("OOO")

        return castle

    def in_check(self, sc, dest):
        #Get the moved piece info
        color, piece = self.decode_piece(self.board[sc])
        in_check = False

        #Get the attacker color
        if color == "w": attackers = "b"
        if color == "b": attackers = "w"

        #Temporarily move the piece from the sc to the destination
        temp = self.board[dest]
        self.board[dest] = self.board[sc]
        self.board[sc] = 1

        #If moving the king temporarily update the king location
        if piece == "King":
            if color == "w": self.wKing = dest
            if color == "b": self.bKing = dest

        if color == "w":
            #Check if king is attacked after the move
            if self.wKing in self.get_attacked_squares(attackers):
                in_check = True

            #Restore the original king position if necessary
            if piece == "King":
                self.wKing = sc

        if color == "b":
            # Check if king is attacked after the move
            if self.bKing in self.get_attacked_squares(attackers):
                in_check = True

            #Restore the original king position if necessary
            if piece == "King":
                self.bKing = sc

        #Restore original board state
        self.board[sc] = self.board[dest]
        self.board[dest] = temp
        return in_check

    def check_promotion(self, dest):
        color, piece = self.decode_piece(self.board[dest])

        if "Pawn" not in piece:
            return False

        if color == "w" and dest <= 7:
            return True
        if color == "b" and dest >= 56:
            return True

        return False

    #Move a piece from a source location to a destination location, check for collisions, remove @ dest if collision
    def move_piece(self, sc, dest) -> bool:
        color, piece = self.decode_piece(self.board[sc])

        #Probably should have been using ternarys elsewhere but I was late to the ballgame
        mult = 1 if color == "b" else -1

        #Check if sc position has a piece, if empty return False
        if self.board[sc] == 1:
            return False

        #Check if dest position piece is same color as source position, if yes return false
        if bin(self.board[sc] - self.board[dest]) == bin(0):
            return False

        #Get available movements for the source piece, if dest not contained return false
        if dest not in self.get_valid_moves(sc):
            return False

        #Check if king is in check, if so check if the move would block the check
        if self.in_check(sc, dest):
            return False
        else:
            if color == "w": self.wCheck = False
            if color == "b": self.bCheck = False

        if piece == "King":
            #Check for castling rights and check if player is trying to castle
            valid_castle = self.valid_castle(sc, dest)
            if dest == sc + 2 and "OO" in valid_castle:
                self.move_piece(sc+3, sc+1)
            elif dest == sc -2 and "OOO" in valid_castle:
                self.move_piece(sc-4, sc-1)

            #King is moving so remove castling rights
            if color == "w":
                self.wKing = dest
                self.wOO = False
                self.wOOO = False
            else:
                self.bKing = dest
                self.bOO = False
                self.bOOO = False

        if piece == "Rook":
            #Black queenside rook
            if sc == 0:
                self.bOOO = False
            #Black kingside rook
            if sc == 7:
                self.bOO = False

            #White queenside rook
            if sc == 56:
                self.wOOO = False

            #White kingside rook
            if sc == 63:
                self.wOO = False

        #Check for en passant capture
        if piece == "Pawn" and dest == self.enpassant + 8*mult:
            dest_pos = (self.enpassant % 8 * 75, self.enpassant // 8 * 75)
            for sprite in [s for s in self.sprites if s.rect.collidepoint(dest_pos)]:
                self.sprites.remove(sprite)

            self.board[self.enpassant] = -1
        if piece == "Pawn" and dest == sc+16*mult:
            color_left, piece_left = self.decode_piece(self.board[dest-1])
            color_right, piece_right = self.decode_piece(self.board[dest+1])

            #If left/right position has a pawn then set the enpassant flag to the destination of the double moved pawn
            if color != color_left and piece_left == "Pawn" and self.rc_dist(dest, dest-1) == 1:
                self.enpassant = dest
            elif color != color_right and piece_right == "Pawn" and self.rc_dist(dest, dest+1) == 1:
                self.enpassant = dest
            else:
                self.enpassant = -1
        else:
            self.enpassant = -1

        #Move the sprite of the moved piece
        sc_pos = (sc % 8 * 75, sc//8 * 75)
        dest_pos = (dest % 8 * 75, dest // 8 * 75)

        for sprite in [s for s in self.sprites if s.rect.collidepoint(dest_pos)]:
            self.sprites.remove(sprite)

        for sprite in [s for s in self.sprites if s.rect.collidepoint(sc_pos)]:
            sprite.rect.x = dest_pos[0]
            sprite.rect.y = dest_pos[1]
            stored_sprite = sprite

        self.board[dest] = self.board[sc]
        self.board[sc] = 1

        if self.check_promotion(dest):
            promotion = color + self.get_promotion()

            #Promote to queen
            piece_sprite = pieces.PieceSprite(eval("pieces."+promotion))
            stored_sprite.img = self.get_graphic(piece_sprite, dest % 8, dest//8 % 7).img
            self.board[dest] += 4

        #Move piece, check for checks, check for win, swap turns
        self.available_moves = []
        self.current_piece = -1

        attacked_squares = self.get_attacked_squares(self.turn)

        if self.turn == "w":
            # Check for king checks
            if self.bKing in attacked_squares:
                self.bCheck = True
                self.wWin = self.check_checkmate(self.turn)
            self.turn = "b"

        elif self.turn == "b":
            if self.wKing in attacked_squares:
                self.wCheck = True
                self.bWin = self.check_checkmate(self.turn)

            self.turn = "w"

        return True

    #Gets all attacked squares for a certain color.
    #Used for calculating which squares are available for the king, castling rights, calculating checkmate
    def get_attacked_squares(self, color):
        attacked_squares = []
        for sc in range(64):
            sc_color, sc_piece = self.decode_piece(self.board[sc])
            if color == sc_color:
                #If pawn only check the immediate diagonals
                if sc_piece == "Pawn":
                    if color == "b": mult = 1
                    else: mult = -1

                    diag1 = sc + 8 * mult + 1
                    diag2 = sc + 8 * mult - 1

                    if self.rc_dist(sc, diag1) == 2:
                        attacked_squares.append(diag1)
                    if self.rc_dist(sc, diag2) == 2:
                        attacked_squares.append(diag2)
                elif sc_piece == "King":
                    attacked_squares += [sc - 9, sc - 8, sc - 7, sc + 9, sc + 8, sc + 7, sc - 1, sc + 1]
                else:
                    attacked_squares += self.get_available_moves(sc)
        return set(attacked_squares)

    #Check if the given color has checkmate
    def check_checkmate(self, color):
        if color == "w": defender = "b"
        if color == "b": defender = "w"

        #Check if any available moves will stop check
        for sc in range(63):
            color, piece = self.decode_piece(self.board[sc])

            if color != defender:
                continue

            moves = self.get_available_moves(sc)
            for dest in moves:
                if not self.in_check(sc, dest):
                    return False

        return True

    #Check if a given color is in stalemate
    def check_stalemate(self, color):
        for sc in range(63):
            sc_color, piece = self.decode_piece(self.board[sc])

            if sc_color != color:
                continue

            if len(self.get_valid_moves(sc)) != 0:
                return False

        return True
    def get_promotion(self):
        return "Queen"

    def get_move(self, color):
        moves = []
        for piece in range(63):
            if piece == -1:
                continue
            if self.board[piece] > 16 and color == "b":
                if len(self.get_valid_moves(piece)) != 0:
                    moves.append((piece, self.get_valid_moves(piece)))
            elif (10 <= self.board[piece] <= 15) and color == "w":
                pieces.append(piece)

        rand = random.randrange(len(moves))
        move_idx = moves[rand]
        piece = move_idx[0]
        move = move_idx[1][0]

        return piece, move
    #TODO game tracking (IE add move list to the side of the screen)
    #TODO read/write PGN
    #TODO write FEN
    #TODO reset game functionality on win
    #TODO elo system?
    #TODO promotion to things other than a queen




if __name__ == "__main__":
    chessApp = App()
    chessApp.on_execute()


