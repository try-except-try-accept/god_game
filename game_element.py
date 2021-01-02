import pyxel

from config import *


class GameElement:
    def __init__(self, x, y, tribe):
        self.tribe = tribe
        self.x = x
        self.y = y
        self.x2 = x + self.width
        self.y2 = y + self.height
        self.attackers = []
        global id_count
        self.id_ = hash(id_count)
        id_count += 1


    def hover(self, x, y):
        if self.x <= x <= self.x + BUILDING_WIDTH:
            if self.y <= y <= self.y + BUILDING_HEIGHT:
                return True
        return False

    def process_damage(self):
        for attacker in self.attackers:
            if self.x - self.width > attacker.x < self.x + self.width:
                if self.y - self.height > attacker.y < self.y + self.height:
                    self.health -= 1


                    if self.health < 25:
                        self.idle_colour = DYING_COLOUR
                        self.colour = self.idle_colour

                    if self.health == 0:
                        self.delete = True
                        for attacker in self.attackers:
                            attacker.end_task()
                        return

    def __hash__(self):
        return self.id_

    def __eq__(self, other):
        return getattr(other, 'id_', None) == self.id_

    def __ne__(self, other):
        return not self.__eq__