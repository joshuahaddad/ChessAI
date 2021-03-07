from dataclasses import dataclass
import pygame
from spritesheet import SpriteSheet

#Define data structure for different piece encodings
@dataclass
class Piece():
    empty = 1
    pawn = 2
    bishop = 3
    knight = 4
    rook = 5
    queen = 6
    king = 7

    white = 8
    black = 16

#Define spirtesheet data here, each piece is 300x400
bRook = (20, 80, 280, 270)
bBishop = (320, 70, 280, 270)
bQueen = (620, 80, 280, 270)
bKing = (920, 70, 280, 270)
bKnight = (1220, 80, 280, 270)
bPawn = (1520, 80, 280, 270)

wRook = (20, 450, 280, 270)
wBishop = (320, 440, 280, 270)
wQueen = (620, 450, 280, 270)
wKing = (920, 440, 280, 270)
wKnight = (1220, 450, 280, 270)
wPawn = (1520, 450, 280, 270)

class PieceSprite(pygame.sprite.Sprite):
    def __init__(self, spritesheet_data):
        super().__init__()
        spritesheet = SpriteSheet("./assets/pieces.png")
        self.image = spritesheet.get_image(spritesheet_data[0],
                                           spritesheet_data[1],
                                           spritesheet_data[2],
                                           spritesheet_data[3])
        self.rect = self.image.get_rect()