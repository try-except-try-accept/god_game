import pyxel
from random import randint
from helpers import probability
from game_element import GameElement
from config import *
global viewport


class Character(GameElement):
    def __init__(self, x, y, tribe=PLAYER_1):
        self.width = 1
        self.height = 1
        super().__init__(x, y, tribe)
        self.s = 1
        self.x_vel = randint(-1, 1)
        self.y_vel = randint(-1, 1)
        self.selected = False
        self.commanded = False
        self.delete = False
        self.top_corner = False
        self.walk_count = 0
        self.chance = 50
        self.target = None
        self.training = None
        self.idle_colour = IDLE_COLOUR
        self.behaviour_colour = PLAYER_1
        self.colour = PLAYER_1
        self.bg_colour = SOLDIER_COLOUR

    def __cmp__(self, other):
        if self == other:
            return True
        return False

    def __gt__(self, other):
        if UNIT_HIERACHY.index(type(self)) >= UNIT_HIERACHY.index(type(other)):
            return True
        return False

    def __lt__(self, other):
        if UNIT_HIERACHY.index(type(self)) < UNIT_HIERACHY.index(type(other)):
            return True
        return False


    def select(self):
        self.selected = True
        self.colour = SELECT_COLOUR

    def deselect(self):
        self.selected = False
        self.colour = self.behaviour_colour

    def __str__(self):
        return "x: {}, y: {}, selected: {}".format(self.x, self.y, self.selected)

    def go_to_destination(self, tx=None, ty=None):

        if tx is not None:
            self.tx = tx
            self.selected = False
            self.commanded = True
        else:
            tx = self.tx
        if ty is not None:
            self.ty = ty
        else:
            ty = self.ty

        if tx > self.x:
            self.x_vel = 1
        elif tx < self.x:
            self.x_vel = -1
        else:
            self.x_vel = 0

        if ty > self.y:
            self.y_vel = 1
        elif ty < self.y:
            self.y_vel = -1
        else:
            self.y_vel = 0

        if self.x == tx and self.y == ty:


            self.colour = self.behaviour_colour
            self.commanded = False
            return False


        return True

    def go_queue(self, building):
        self.training = building
        x, y = building.x, building.y
        self.go_to_destination(x, y)


    def process_train_command(self):
        if self.training is not None:
            try:
                queue_position = self.training.queue.index(self)
                #print("i'm at position {} in the queue".format(queue_position))

                self.x, self.y = self.training.perimeter[queue_position*2]


                return True
            except:
                self.training.leave_queue(self)
                return False
        return False


    def end_task(self):
        if self.target is not None:
            self.target.attackers.remove(self)
            self.target = None
            self.lock_x = None
            self.lock_y = None
        if self.training is not None:

            self.training.leave_queue(self)
            self.training = None

    def draw(self):
        pyxel.rect(viewport['x']+self.x, viewport['y']+self.y, self.s, self.s, self.colour)

    def go_attack(self, target):
        self.attack_pattern = 0
        self.attack_count = 0
        self.target = target
        x, y = target.x - 1, target.y - 1

        self.attack_x = 0
        self.attack_y = 0

        self.lock_x = target.x
        self.lock_y = target.y

        self.go_to_destination(x, y)

        north = self.target.y - self.y
        south = self.y - self.target.y
        east = self.target.x - self.x
        west = self.x - self.target.x

        furthest = max([north, south, east, west])

        if furthest == north:
            self.attack_y = 1
            if abs(north - east) < 10:
                self.attack_x = -1
            elif abs(north - west) < 10:
                self.attack_x = 1
        elif furthest == south:
            self.attack_y = -1
            if abs(south - east) < 10:
                self.attack_x = -1
            elif abs(south - west) < 10:
                self.attack_x = 1
        elif furthest == east:
            self.attack_x = -1
            if abs(east - north) < 10:
                self.attack_y = 1
            elif abs(east - south) < 10:
                self.attack_y = -1
        else:
            self.attack_x = 1
            if abs(west - north) < 10:
                self.attack_y = 1
            elif abs(west - south) < 10:
                self.attack_y = -1

    def process_walk_command(self):

        if self.commanded:

            self.colour = COMMAND_COLOUR
            self.chance = 90
            return self.go_to_destination()
        else:
            return False

    def process_build_command(self):
        return False

    def process_attack_command(self):
        if self.target:
            self.colour = ATTACK_COLOUR
            if self.target.x != self.lock_x or self.target.y != self.lock_y:
                self.commanded = True
                self.go_attack(self.target)

            if self.attack_pattern == 0:
                self.x_vel = self.attack_x
                self.y_vel = self.attack_y
            else:

                self.x_vel = 0 - self.attack_x
                self.y_vel = 0 - self.attack_y

            self.attack_count += 1

            if self.attack_count % 5 == 0:  # every 5 frames

                self.attack_pattern = abs(self.attack_pattern - 1)

            self.chance = 100
            return True
        return False

    def check_out_of_bounds(self):
        return

        if self.x > WIDTH or self.y > HEIGHT:
            self.delete = True

    def process_idle_behaviour(self):

        if self.selected:
            self.colour = SELECT_COLOUR
            dont_move = 99
        else:
            self.colour = self.idle_colour

        if self.walk_count > 20:
            dont_move = 99
            self.x_vel = randint(-1, 1)
            self.y_vel = randint(-1, 1)

        else:
            dont_move = 4

        self.chance = 50
        if probability(dont_move):
            self.chance = 0

    def update(self):

        self.walk_count += 1

        self.process_damage()

        self.process_commands()

        if probability(self.chance):
            self.x += self.x_vel
        if probability(self.chance):
            self.y += self.y_vel

        self.check_out_of_bounds()

    def process_commands(self):
        self.process_idle_behaviour()

class Soldier(Character):
    def __init__(self, x, y, tribe=PLAYER_1):
        super().__init__(x, y, tribe)
        self.s = 1
        self.target = None


    def end_task(self):
        if self.target is not None:
            self.target.attackers.remove(self)
            self.target = None

    def draw(self):
        pyxel.rect(viewport['x']+self.x-self.s, viewport['y']+self.y-self.s, self.s+2, self.s+2, self.bg_colour)
        super().draw()

    def process_commands(self):
        if self.process_walk_command():
            pass
        elif self.process_attack_command():
            pass
        elif self.process_train_command():
            self.training.queue.append(self)

class Tank(Character):
    def __init__(self, x, y, tribe=PLAYER_1):
        super().__init__(x, y, tribe)
        self.s = 2
        self.target = None

    def set_target():
        pass

    def fire():
        pass

    def release_target():
        pass

    def draw(self):

        if self.y_vel != 0:
            wide = 3
            tall = 5

        else:
            wide = 5
            tall = 3

        pyxel.rect(viewport['x']+self.x-self.s, viewport['y']+self.y-self.s, self.s+wide, self.s+tall, self.bg_colour)
        pyxel.rect(viewport['x']+self.x, viewport['y']+self.y, self.s, self.s, self.colour)

    def process_commands(self):
        if self.process_walk_command():
            pass
        elif self.process_attack_command():
            pass


class Worker(Character):
    def __init__(self, x, y, tribe=PLAYER_1):
        super().__init__(x, y, tribe)
        self.build_pattern = 0
        self.build_count = 0

        self.mine_count = 0
        self.mine_in = 1

        self.colour = 10
        self.building = None
        self.mining = None
        self.health = 1000

    def end_task(self):
        super().end_task()
        finishing_job = None
        if self.building is not None:
            finishing_job = self.building.workers
            self.building = None
            self.build_pattern = 0
            self.build_count = 0
            self.walk_count = 0
        elif self.mining is not None:
            finishing_job = self.mining.miners
            self.mining = None
            self.mine_pattern = 0
            self.mine_count = 1
            self.walk_count = 0
        else:
            self.behaviour_colour = PLAYER_1

        if finishing_job is not None:
            try:
                finishing_job.remove(self)
            except KeyError:
                print("Already quit that job.")

    def go_build(self, building):

        self.commanded = True
        self.colour = BUILD_COLOUR
        self.behaviour_colour = self.colour
        self.building = building

        self.x_count = 0
        self.y_count = 0
        x, y = building.x - 1, building.y - 1
        self.tx, self.ty = x, y

    def go_mine(self, mine):
        self.colour = MINE_COLOUR
        self.behaviour_colour = self.colour

        self.mining = mine
        x, y = mine.x, mine.y
        self.go_to_destination(x, y)


    def process_mine_command(self):
        if self.mining is not None:
            if self.mine_in == -1:
                chance = 20
            else:
                chance = 90

            if probability(chance):
                self.mine_count += self.mine_in

            if self.mine_count == len(self.mining.path):
                self.mine_in = -1
                self.mine_count -= 1
            elif self.mine_count == 0:
                self.mine_in = 1
                self.mine_count += 1

            self.x, self.y = self.mining.path[self.mine_count]
            return True
        return False

    def process_build_command(self):


        if self.building is not None:

            self.colour = BUILD_COLOUR

            if self.build_pattern == 0:
                self.x_vel = 1
                self.y_vel = 0
            if self.build_pattern == 1:
                self.y_vel = 1
                self.x_vel = 0
            if self.build_pattern == 2:
                self.x_vel = -1
                self.y_vel = 0
            if self.build_pattern == 3:
                self.y_vel = -1
                self.x_vel = 0
            self.build_count += 1

            w = self.building.width + 1
            h = self.building.height + 1

            if self.build_count == w:
                self.build_pattern = 1
            elif self.build_count == w + h:
                self.build_pattern = 2
            elif self.build_count == w + h + w:
                self.build_pattern = 3
            elif self.build_count == w + h + w + h:
                self.build_pattern = 0
                self.build_count = 0
            self.chance = 100
            return True
        return False

    def process_commands(self):
        if self.process_walk_command():
            pass
            # print("walking")
        elif self.process_build_command():
            self.building.workers.add(self)
            # print("building")
        elif self.process_mine_command():
            self.mining.miners.add(self)
            # print("mining")
        elif self.process_train_command():
            pass
            # print("training")
        else:
            self.process_idle_behaviour()
            pass
            # print("idling")

UNIT_HIERACHY = [Tank, Soldier, Worker]