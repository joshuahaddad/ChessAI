import constants as const
import pygame


class SpriteSheet(object):
    def __init__(self, file_name):
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert_alpha()

    def get_image(self, x, y, width, height):
        # Create a new blank image
        image = pygame.Surface([width, height], pygame.SRCALPHA)
        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

        # Assuming black works as the transparent color

        # Return the image
        return image