from random import randint

import pyxel
from config import *
from game_element import GameElement


class Maze():

    def __init__(self):

        self.vertices = []
        self.all_points = []

    def add_point(self, x, y):

        start_x, start_y = [x, y]

        try:
            end_x, end_y = self.points[-1]
        except IndexError:
            self.vertices.append([x, y])
            self.all_points.append([x, y])
            print("First vertex of maze")
            return

        self.vertices.append([x, y])

        x_adjust = end_x - start_x
        y_adjust = end_y - start_y

        x_dir, y_dir = True, True

        x_comp = "{} < {}"
        if x_adjust < 0:
            x_dir = False
            x_comp = "{} > {}"

        y_comp = "{} < {}"
        if y_adjust < 0:
            y_dir = False
            y_comp = "{} > {}"

        if abs(x_adjust) > abs(y_adjust):
            y_adjust = y_adjust / abs(x_adjust)
            x_adjust = 1
            if not x_dir:
                x_adjust = -1
        else:

            x_adjust = x_adjust / abs(y_adjust)
            y_adjust = 1
            if not y_dir:
                y_adjust = -1

        condition = x_comp.format(start_x, end_x) + " or " + y_comp.format(start_y, end_y)

        while eval(condition):
            condition = x_comp.format(start_x, end_x) + " or " + y_comp.format(start_y, end_y)
            
            self.all_points.append([start_x, start_y])
            start_x += x_adjust
            start_y += y_adjust



    def draw(self):
        for p in self.all_points:
            pyxel.rect(viewport['x'] + int(p[0]), viewport['y'] + int(p[1]), 1, 1, MAZE_COLOUR)

        for i, point in enumerate(self.points):
            try:
                next_point = self.points[i+1]
            except IndexError:
                break








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

