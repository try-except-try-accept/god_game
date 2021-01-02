PIP_COMMANDS = ["pip install pyxel", "pip3 install pyxel"]
WIDTH = 1000
HEIGHT = 800

pyxel_installed = False


while not pyxel_installed:

    try:
        import pyxel
        break
    except Exception as e:
        print(e)
    try:
        import os
        os.system(PIP_COMMANDS.pop(0))
    except Exception as e:
        print(e)
        
    if len(PIP_COMMANDS) == 0:
        exit("Can't install pyxel... oops bye")
            
import itertools
from collections import OrderedDict
from random import randint, randrange, shuffle, choice
import math

from config import *
from buildings import *
from characters import *
from helpers import *
from music import *
from scenary import *






## TO DO


# 4b. merge build behaviour and mine behaviour
# 6. building decreases ore
# 7. training decrease ore
# 8. delete unbuilt building increases ore
# 9. create mine cursor not white if build max reached
# 9. stop from laying plans over stuff that already exists
# 9. attacking harms building after time, eventually destroys
# 11. select all idles
# 12. attack perimiter of building not just top left corner point
# 13. selection and build -> straight to build
# 14. queue jobs for workers
# 15.



class Selection:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def find_bounds(self):
        if self.x < pyxel.mouse_x:
            x = self.x
            w = pyxel.mouse_x - self.x
        else:
            x = pyxel.mouse_x
            w = self.x - pyxel.mouse_x

        if self.y < pyxel.mouse_y:
            y = self.y
            h = pyxel.mouse_y - self.y
        else:
            y = pyxel.mouse_y
            h = self.y - pyxel.mouse_y
        return x, y, w, h

    def draw(self):
        x, y, w, h = self.find_bounds()
        pyxel.rect(x, y, w, h, SELECT_COLOUR)

    def finalise_selection(self, bits):
        x, y, w, h = self.find_bounds()
        x2 = x + w
        y2 = y + h

        x -= viewport['x']
        x2 -= viewport['x']
        y -= viewport['y']
        y2 -= viewport['y']

        selected_bits = []
        for bit in bits:
            bit.deselect()
            if bit.x >= x and bit.x <= x2:
                if bit.y >= y and bit.y <= y2:
                    bit.select()
                    selected_bits.append(bit)

        return selected_bits





class Game:
    def __init__(self, width=100, height=600):

        pyxel.init(WIDTH, HEIGHT, caption="GODGAME")
        pyxel.load("sprites.pyxres")

        self.ore = 50

        self.energy = 10
        self.bits = [Tank(100, 100)]
        self.scenary = [Ore(randint(0, GAME_WIDTH), randint(0, HEIGHT)) for i in range(5)]
        self.scenary += [Ore(randint(-5000, 5000), randint(-5000, 5000)) for i in range(500)]
        self.buildings = [Home(WIDTH // 2, HEIGHT // 2, pre_built=True)]
        self.bit_selection = None
        self.selected_bits = []
        self.cursor = "."
        self.enemy_objects = self.bits
        self.being_built = []
        self.icons = OrderedDict()
        self.left, self.right, self.up, self.down = False, False, False, False
        self.view_x_move = 0
        self.view_y_move = 0


        for object in IMPLEMENTED_BUILDINGS:
            self.icons.update({object.symbol: {"y": 0, "constructor": object, "type": object.build_type}})



        prep_music()
        pyxel.playm(0, loop=True)

        pyxel.run(self.process_events, self.draw)
        pyxel.mouse(True)



    def initiate_selection(self, x, y):
        if x < GAME_WIDTH:
            self.bit_select = True

    def process_events(self):


        true_mouse_x = pyxel.mouse_x
        true_mouse_y = pyxel.mouse_y

        viewport_mouse_x = pyxel.mouse_x - viewport['x']
        viewport_mouse_y = pyxel.mouse_y - viewport['y']


        self.cursor_colour = 7
        for target in self.enemy_objects:
            if target.hover(viewport_mouse_x, viewport_mouse_y):
                self.cursor_colour = ATTACK_COLOUR

        spawn_rate = SPAWN_RATE - self.energy
        ore_rate = 1000
        for building in self.buildings:


            if building in self.being_built:
                if all(building.build_state):
                    if type(building) == Generator:
                        self.energy += 10
                    self.ore -= building.cost
                    self.being_built.remove(building)

            if type(building) == Mine:
                ore_rate -= len(building) // 5
                if pyxel.frame_count % ore_rate == 0:
                    self.ore += 1


            building.update(pyxel.frame_count)
            spawn = building.check_spawn(pyxel.frame_count)

            if spawn is not None:
                if len(self.bits) < BIT_LIMIT:
                    self.bits.append(spawn)
                    self.bits = sorted(self.bits)

        if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON):
            self.cursor = "."
            for b in self.selected_bits:  ## make bits go in a grid when idle?
                b.deselect()

        if self.cursor in self.icons.keys():

            new_building = self.icons[self.cursor]["constructor"](viewport_mouse_x, viewport_mouse_y)
            new_building_allowed = (self.ore - new_building.cost) > 0

            if self.icons[self.cursor]["type"] == "mine":
                new_building_allowed = new_building_allowed and new_building.check_placement_allowed(viewport_mouse_x, viewport_mouse_y, self.scenary)

            if not new_building_allowed:
                self.cursor_colour = WARNING_COLOUR
            else:
                self.cursor_colour = CURSOR_COLOUR



        if pyxel.btnp(pyxel.KEY_LEFT):
            self.left = True
        elif pyxel.btnr(pyxel.KEY_LEFT):
            self.left = False

        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.right = True

        elif pyxel.btnr(pyxel.KEY_RIGHT):
            self.right = False

        if pyxel.btnp(pyxel.KEY_DOWN):
              self.down = True
        elif pyxel.btnr(pyxel.KEY_DOWN):
            self.down = False

        if pyxel.btnp(pyxel.KEY_UP):
            self.up = True
        elif pyxel.btnr(pyxel.KEY_UP):
            self.up = False




        viewport['x'] += self.view_x_move
        viewport['y'] += self.view_y_move

        if self.left:
            self.view_x_move += 1
            if self.view_x_move > MAX_SCROLL_SPEED:
                self.view_x_move = MAX_SCROLL_SPEED
        elif self.right:
            self.view_x_move -= 1
            if self.view_x_move < 0 - MAX_SCROLL_SPEED:
                self.view_x_move = 0 - MAX_SCROLL_SPEED
        else:
            if self.view_x_move > 0:
                self.view_x_move -= 1
            elif self.view_x_move < 0:
                self.view_x_move += 1

        if self.up:
            self.view_y_move += 1
            if self.view_y_move > MAX_SCROLL_SPEED:
                self.view_y_move = MAX_SCROLL_SPEED
        elif self.down:
            self.view_y_move -= 1
            if self.view_y_move < 0 - MAX_SCROLL_SPEED:
                self.view_y_move = 0 - MAX_SCROLL_SPEED
        else:
            if self.view_y_move > 0:
                self.view_y_move -= 1
            elif self.view_y_move < 0:
                self.view_y_move += 1



        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):


            if true_mouse_x >= GAME_WIDTH:

                self.bit_selection = None
                for icon, properties in self.icons.items():
                    y = properties["y"] - 4
                    if true_mouse_y >= y:
                        if true_mouse_y <= y + ICON_HEIGHT:
                            if len(self.buildings) < BUILDING_LIMIT-1:
                                self.cursor = icon

                if true_mouse_y >= HEIGHT-10:
                    print("skipping")
                    prep_music()
                    

            elif self.cursor == ".":
                self.bit_selection = Selection(true_mouse_x, true_mouse_y)


            elif self.cursor in self.icons.keys():


                if new_building_allowed:

                    if len(self.buildings) < BUILDING_LIMIT:

                        self.buildings.append(new_building)
                        self.being_built.append(new_building)
                else:
                    self.cursor = "."


            else:
                to_mine = None
                to_build = None
                to_train_at = None


                for building in self.buildings:
                    if building.hover(viewport_mouse_x, viewport_mouse_y):
                        if not all(building.build_state):
                            to_build = building
                            break
                        elif type(building) == Mine:
                            to_mine = building
                            break
                        elif type(building) in [Barracks, Factory]:
                            if building.has_training_space():
                                print("Training time.")
                                to_train_at = building
                                break



                to_attack = None

                for target in self.bits:
                    if target.tribe == PLAYER_1:
                        continue
                    if target not in self.selected_bits and target.hover():
                        to_attack = target
                        break

                orig_x, orig_y = viewport_mouse_x, viewport_mouse_y

                side = get_stance_size(len(self.selected_bits))

                regiment_positions = itertools.chain.from_iterable(
                    [[(x, y) for x in range(0, side * 2, 2)] for y in range(0, side * 2, 2)])


                for b, [regiment_x, regiment_y] in zip(self.selected_bits, regiment_positions):
                    b.end_task()

                    inappropriate_selection = False

                    if b.delete:
                        if b in self.bits:
                            self.bits.remove(b)

                    job_given = False
                    if type(b) in [Soldier, Tank]:
                        if to_attack is not None:
                            to_attack.attackers.append(b)
                            b.go_attack(to_attack)
                            job_given = True

                    elif type(b) == Worker:
                        if to_build is not None:
                            b.go_build(to_build)
                            job_given = True
                        elif to_mine is not None:
                            b.go_mine(to_mine)
                            job_given = True
                        # else:
                        #     inappropriate_selection = True
                        #     job_given = True

                    if to_train_at is not None:
                        if to_train_at.input == type(b):
                            b.go_queue(to_train_at)
                            building.queue.append(b)
                            job_given = True


                    if inappropriate_selection:
                        self.selected_bits.remove(b)
                        b.deselect()
                        job_given = True

                    if not job_given:
                        b.go_to_destination(orig_x + regiment_x, orig_y + regiment_y)





        elif pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):

            if self.bit_selection:

                self.selected_bits = self.bit_selection.finalise_selection(self.bits)
                self.bit_selection = None
                if len(self.selected_bits) > 0:
                    self.cursor = "^"

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw_selection(self):

        if self.bit_selection:
            self.bit_selection.draw()

    def draw_bits(self):

        for bit in self.bits:
            bit.update()
            if bit.delete:
                self.bits.remove(bit)
            bit.draw()

    def draw_buildings(self):

        for building in self.buildings:
            building.draw()

    def draw_scenary(self):

        for thing in self.scenary:
            thing.draw()

    def draw_stats(self):
        stats_y = HEIGHT - 5
        stats_x = 10
        labels = """POP:1    BGS:2    ORE:3    NRG:4"""

        positions = [stats_x + labels.index(str(i))*4 for i in range(1, 5)]

        labels = """POP:     BGS:     ORE:     NRG: """

        pyxel.text(stats_x, stats_y, labels, CURSOR_COLOUR)

        pop = len(self.bits)
        bgs = len(self.buildings)

        stats = [pop, bgs, self.ore, self.energy]

        for i, (pos, stat, limit) in enumerate(zip(positions, stats, LIMITS)):
            if stat == limit:
                colour = WARNING_COLOUR
            elif stat > limit * 0.75:
                colour = 9
            elif stat > limit * 0.5:
                colour = 10
            else:
                colour = 11

            pyxel.text(pos, stats_y, str(stat), colour)


    def draw_menu(self):
        pyxel.rect(GAME_WIDTH, 0, 10, HEIGHT, MENU_COLOUR)

        x = GAME_WIDTH + 3

        if len(self.buildings) < BUILDING_LIMIT:
            colour = ICON_COLOUR
        else:
            colour = WARNING_COLOUR

        for y, icon in enumerate(self.icons):
            y = y * ICON_SPACER
            pyxel.rect(x - 1, y, ICON_HEIGHT, ICON_HEIGHT + 1, 13)
            self.icons[icon]["y"] = (y)
            pyxel.text(x, y, icon, colour)

    def draw_music(self):
        #pyxel.rect(GAME_WIDTH, 0, 10, HEIGHT-10, MENU_COLOUR)
        pyxel.text(GAME_WIDTH+3, HEIGHT-10, ">", ICON_COLOUR)

    def draw_cursor(self):

        pyxel.text(pyxel.mouse_x, pyxel.mouse_y, self.cursor, self.cursor_colour)

    def draw(self):

        self.run_updates()
        pyxel.cls(0)
        self.draw_selection()
        self.draw_scenary()
        self.draw_buildings()
        self.draw_bits()

        self.draw_stats()
        self.draw_menu()
        self.draw_cursor()
        self.draw_music()

    def run_updates(self):
        pass


Game()

