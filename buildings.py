import pyxel
from random import shuffle


from game_element import GameElement
from config import *
from characters import *

from tilemap import TILE_MAP
from scenary import *


class Building(GameElement):
    def __init__(self, x, y, pre_built=False, tribe=PLAYER_1):
        self.width = TILE_MAP["p{}_{}_{}".format(PLAYERS[tribe], self.build_type, "w")]
        self.height = TILE_MAP["p{}_{}_{}".format(PLAYERS[tribe], self.build_type, "h")]
        self.x_buffer = TILE_MAP["p{}_{}_{}".format(PLAYERS[tribe], self.build_type,"x")]
        self.y_buffer = TILE_MAP["p{}_{}_{}".format(PLAYERS[tribe], self.build_type, "y")]
        self.x_buffer2 = TILE_MAP["p{}_{}_{}".format(PLAYERS[tribe], self.build_type, "x2")]
        self.y_buffer2 = TILE_MAP["p{}_{}_{}".format(PLAYERS[tribe], self.build_type, "y2")]

        if all(stat==0 for stat in [self.width, self.height, self.x_buffer, self.y_buffer]):
            self.width = BUILDING_WIDTH
            self.height = BUILDING_HEIGHT


        self.area = self.width * self.height




        super().__init__(x, y, tribe)


        self.build_state = []
        if pre_built:
            self.build_state = [True for i in range(self.area)]
        else:
            self.build_state = [False for i in range(self.area)]



        shuffle(self.build_state)


        self.state = ""
        self.colour = BUILDING_COLOUR
        self.workers = set()
        self.input = None
        self.output = None

        self.calculate_perimeter()
        self.spawn_rate = SPAWN_RATE

    def calculate_perimeter(self):
        buffer = 2
        self.perimeter = []

        x_max = self.x + self.width + buffer
        y_max = self.y + self.height + buffer
        y_min = self.y - buffer
        x_min = self.x - buffer

        y = y_max
        for x in range(x_max - buffer, x_min-1, -1):
            self.perimeter.append([x, y])
        for y in range(y_max-1, y_min-1, -1):
            self.perimeter.append([x, y])
        for x in range(x_min, x_max, 1):
            self.perimeter.append([x, y])
        for y in range(y_min, y_max):
            self.perimeter.append([x, y])






    def draw(self):

        if not all(self.build_state):
            x, y = self.x_buffer2, self.y_buffer2
        else:
            x, y = self.x_buffer, self.y_buffer

        pyxel.text(viewport['x'] + self.x, viewport['y'] + self.y, self.symbol, self.colour)
        pyxel.blt(viewport['x'] + self.x, viewport['y'] + self.y, 0, x, y, self.width, self.height)


        if len(self.workers):
            mask_count = 0
            for mask_x in range(self.width):
                for mask_y in range(self.height):
                    if not self.build_state[mask_count]:
                        pyxel.rect(self.x + mask_x + viewport['x'],
                                   self.y + mask_y + viewport['y'],
                                   1,
                                   1,
                                   0)
                    mask_count += 1




    def dismiss(self):
        workers = self.workers
        for worker in set(workers):
            worker.end_task()

    def update(self, frame_count):

        if False in self.build_state:
            if frame_count % self.calculate_build_rate() == 0:
                if len(self.workers):
                    i = self.build_state.index(False)
                    self.build_state[i] = True


        else:
            self.colour = BUILDING_COLOUR
            if len(self.workers) > 0:
                self.dismiss()



    def calculate_build_rate(self):
        work_force = len(self.workers)

        if work_force > self.build_complexity:
            work_force = self.build_complexity
        max_ = self.build_complexity * 5

        max_time = self.build_complexity * 5
        min_time = 10

        interval = (max_time - min_time) // self.build_complexity
        #return max_time - interval * work_force
        return 1

    def check_spawn(self, frame_count):
        if all(self.build_state):
            if frame_count % self.spawn_rate == 0:
                return self.produce()

    def produce(self):
        if self.output is not None:
            return self.output(self.x, self.y+self.height)

    def check_placement_allowed(self,  x, y, scenery):
        return True


class Generator(Building):
    symbol = "G"
    build_type = "generator"

    def __init__(self, x, y, pre_built=False, tribe=PLAYER_1):

        super().__init__(x, y, pre_built, tribe)
        self.build_complexity = GENERATOR_BUILD_TIME
        self.cost = GENERATOR_COST


class Mine(Building):
    symbol = "X"
    build_type = "mine"

    def __init__(self, x, y, pre_built=False, tribe=PLAYER_1):
        super().__init__(x, y, pre_built, tribe)
        self.build_complexity = MINE_BUILD_TIME
        self.miners = set()
        self.plot_path()
        self.cost = MINE_COST


    def __len__(self):
        return len(self.miners)

    def check_placement_allowed(self, x, y, scenery):
        for object in scenery:
            if type(object) == Ore:

                if object.x <= x + object.width <= (object.x + object.width):
                    if object.y <= y + object.height <= (object.y + object.height):

                        return True

        return False

    def plot_path(self):

        path = []

        x_min = self.x
        y_min = self.y
        x_max = self.x + self.width
        y_max = self.y + self.height

        while x_min < x_max:
            for x in range(x_min, x_max + 1):
                path.append([x, y_min])
            for y in range(y_min + 1, y_max + 1):
                path.append([x_max, y])
            for x in range(x_max - 1, x_min - 1, -1):
                path.append([x, y_max])
            for y in range(y_max - 1, y_min, -1):
                path.append([x_min, y])

            x_min += 1
            x_max -= 1
            y_min += 1
            y_max -= 1



        self.path = path





class Home(Building):
    symbol = "H"
    build_type = "house"

    def __init__(self, x, y, pre_built=False, tribe=PLAYER_1):
        super().__init__(x, y, pre_built, tribe)
        self.output = Worker
        self.health = 10000
        self.build_complexity = HOME_BUILD_TIME
        self.cost = HOME_COST


class Barracks(Building):
    symbol = "S"
    build_type = "barracks"


    def __init__(self, x, y, pre_built=False, tribe=PLAYER_1):
        super().__init__(x, y, pre_built, tribe)
        self.input = Worker
        self.output = Soldier
        self.queue = []
        self.queue_time = 0
        self.spawn = SOLDIER_SPAWN
        self.build_complexity = SOLDIER_BUILD_TIME
        self.queue_max = BARRACKS_QUEUE_MAX
        self.cost = BARRACKS_COST


    def update(self, frame_count):
        super().update(frame_count)

        if len(self.queue):
            self.queue_time += 1

    def check_spawn(self, frame_rate):

        if len(self.queue):
            if all(self.build_state):
                if self.queue_time % self.spawn == 0:
                    bit = self.queue.pop(0)
                    bit.delete = True

                    return self.produce()

    def leave_queue(self, bit):
        if bit in self.queue:
            self.queue.remove(bit)

    def has_training_space(self):
        return len(self.queue) < self.queue_max



class Factory(Barracks):
    symbol = "T"
    build_type = "factory"

    def __init__(self, x, y, pre_built=False, tribe=PLAYER_1):
        super().__init__(x, y, pre_built, tribe)
        self.queue_max = FACTORY_QUEUE_MAX
        self.input = Soldier
        self.output = Tank
        self.spawn = TANK_SPAWN
        self.build_complexity = FACTORY_BUILD_TIME
        self.cost = FACTORY_COST



IMPLEMENTED_BUILDINGS = [Home, Mine, Generator, Barracks, Factory]