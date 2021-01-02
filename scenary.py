from random import randint

import pyxel
from config import *
from game_element import GameElement

class Ore(GameElement):

    def __init__(self, x, y, tribe=NEUTRAL):
        self.x = x
        self.y = y
        self.depth = randint(4, 18)
        self.grow_crystal()

        self.height = max(p[1] for p in self.pixels) - min(p[1] for p in self.pixels)
        self.width = max(p[0] for p in self.pixels) - min(p[0] for p in self.pixels)

        super().__init__(x, y, tribe)

    def draw(self):
        for p in self.pixels:
            pyxel.rect(viewport['x'] + p[0], viewport['y'] + p[1], 1, 1, ORE_COLOUR)


    def grow_crystal(self):
        self.pixels = []
        for shard in range(self.depth):
            length = randint(2, 4)
            direction = [randint(-1, 1), randint(-2, -1)]
            x, y = self.x, self.y
            for i in range(length):
                x += direction[0]
                y += direction[1]

                self.pixels.append([x, y])

