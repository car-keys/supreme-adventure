import sys, pygame, math, json, time
import numpy as np
# pygame is in x,y
# point = [x, y]
# Some global values
SCREEN_SIZE = (500, 900)
BACKGROUND_COLOR = pygame.Color(255, 255, 255)
TEXTURE_LEN = 32
BLOCK_SIZE = 1
MIN_DIST_FOR_EQUAL = 0.3
MAX_RAY_ITERS = 20
DEFAULT_LOOK_ANGLE = 0
DEFALT_LOOK_FOV_RADIUS = 80
LINES_PER_PIX = 6
RAYS = SCREEN_SIZE[1]//LINES_PER_PIX

textures = []


def parse_block_file(filename):
    print(f'parsing {filename}')
    with open(filename) as f:
        data = json.load(f)
    return BlockDef(data['Name'],
                    hexes_to_colors(data['Top']),
                    hexes_to_colors(data['Bottom']),
                    hexes_to_colors(data['Side']))


def hexes_to_colors(hexes):
    cols = []
    for h in hexes:
        cols.append(pygame.Color('0x'+h.lower()))
    return cols


def parse_block_files(block_filenames):
    block_defs = {}
    
    for b in block_filenames:
        newdef = parse_block_file(b)
        block_defs[newdef.name] = newdef

    return block_defs


def parse_level(filename, block_defs):
    level = []
    with open(filename) as f:
        data = json.load(f)
        for b in data["Blocks"]:
            level.append(block_defs[b[2]].make_one((b[0], b[1])))
    player = Player(list(data["StartingPos"]))
    return level, player


class BlockDef:
    """Yes, i know this is bad code"""
    def __init__(self, name, top_texture, bot_texture, side_texture):
        self.name = name
        textures.append(top_texture)
        textures.append(side_texture)
        textures.append(bot_texture)

        self.top_texture = len(textures)-3
        self.side_texture = len(textures)-2
        self.bot_texture = len(textures)-1
        
    def make_one(self, loc):
        return Block(loc, self.top_texture, self.side_texture, self.bot_texture)


class Player:
    """Params:
        x,y
        look angle
        look direction (back or front)
    """
    
    def __init__(self, starting_pos):
        self.pos = [starting_pos[0]+BLOCK_SIZE/2, starting_pos[1]+BLOCK_SIZE/2]  # x, y
        self.look_angle = DEFAULT_LOOK_ANGLE  # degrees
        self.look_dir = 'forward'  # 'back' or 'forward'
        self.fov_radius = DEFALT_LOOK_FOV_RADIUS

    def get_bottom_angle(self):
        return self.look_angle-self.fov_radius

    def get_top_angle(self):
        return self.look_angle + self.fov_radius


class Block:
    def __init__(self, top_left, top_texture_index, side_texture_index, bot_texture_index):
        bl = (top_left[0], top_left[1]-BLOCK_SIZE)
        tr = (top_left[0]+BLOCK_SIZE, top_left[1])
        br = (top_left[0]+BLOCK_SIZE, top_left[1]-BLOCK_SIZE)
        self.left_side = VBlockSide(top_left, bl, side_texture_index)
        self.right_side = VBlockSide(tr, br, side_texture_index)
        self.top_side = HBLockSide(top_left, tr, top_texture_index)
        self.bot_side = HBLockSide(bl, br, bot_texture_index)
        
    def get_two_closest_sides(self, source_point):
        sides = [self.left_side,
                 self.right_side,
                 self.top_side,
                 self.bot_side]
        sides.sort(key=lambda a: a.dist_from_point(source_point))
        return sides[:2]


class HBLockSide:
    def __init__(self, left, right, texture_index):
        self.left = left
        self.right = right
        self.texture_index = texture_index
        
    def dist_from_point(self, point):
        if point[0] > self.right[0]: 
            return dist_between_points(point, self.right)
        elif point[0] < self.left[0]:
            return dist_between_points(point, self.left)
        else:  # point y between top and bot ys
            return abs(point[1]-self.left[1])
          
    def adjacent_to(self, other):
        if not isinstance(other, HBLockSide) or self is other:
            return False
        if dist_between_points(self.left, other.left) < MIN_DIST_FOR_EQUAL:
            if dist_between_points(self.right, other.rught) < MIN_DIST_FOR_EQUAL:
                return True
        return False
    
    def find_color_from_point(self, point):
        l1 = point[0] - self.left[0]
        l2 = self.right[0] - self.left[0]
        # ------* l1
        # ------*------------- BLOCK_SIZE
        #       ^ index
        index = int(l1*TEXTURE_LEN/l2)  # floored since 0 is start
        if index > TEXTURE_LEN-1:
            index = TEXTURE_LEN-1
        elif index < 0:
            index = 0
        return textures[self.texture_index][index]
    
    
class VBlockSide:
    def __init__(self, top, bot, texture_index):
        self.top = top
        self.bot = bot
        self.texture_index = texture_index
        
    def dist_from_point(self, point):
        if point[1] > self.top[1]: 
            return dist_between_points(point, self.top)
        elif point[1] < self.bot[1]:
            return dist_between_points(point, self.bot)
        else:  # point y between top and bot ys
            return abs(point[0]-self.top[0])
            
    def adjacent_to(self, other):
        if not isinstance(other, VBlockSide) or self is other:
            return False
        if dist_between_points(self.top, other.top) < MIN_DIST_FOR_EQUAL:
            if dist_between_points(self.bot, other.bot) < MIN_DIST_FOR_EQUAL:
                return True
        return False
        
    def find_color_from_point(self, point):
        l1 = point[1] - self.top[1]
        l2 = self.bot[1] - self.top[1]
        # ------* l1
        # ------*------------- BLOCK_SIZE
        #       ^ index
        index = int(l1*TEXTURE_LEN/l2)  # floored since 0 is start

        if index > TEXTURE_LEN-1:
            index = TEXTURE_LEN-1
        elif index < 0:
            index = 0
        return textures[self.texture_index][index]
        

def dist_between_points(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**(1/2)  # TODO
    
    
def find_closest_side(pos, sides):
    smallest_dist = 1000000000
    min_side = None
    for s in sides:
        d = s.dist_from_point(pos)
        if d < MIN_DIST_FOR_EQUAL:
            # we found a side the point is right on top of, so this must be the one!
            return s, 0
        if d < smallest_dist:
            smallest_dist = d
            min_side = s
    return min_side, smallest_dist
    
    
def raycast_one(player, angle, sides, max_dist):
    """Finds the color for a single ray."""
    curr_point = player.pos
    i = 0

    while i < MAX_RAY_ITERS:
        closest_side, distance = find_closest_side(curr_point, sides)
        if distance == 0:
            return closest_side.find_color_from_point(curr_point)
        elif distance > max_dist:
            return BACKGROUND_COLOR
        else:
            curr_point = (curr_point[0] + math.cos(math.radians(angle))*distance,
                          curr_point[1] + math.sin(math.radians(angle))*distance)
        i += 1
    return BACKGROUND_COLOR
       
       
def raycast(player, level):
    """Calculates the color of every pixel on the screen, using the player's head position and angle"""
    # 1 - grab all possible sides, and cull when possible
    sides = []

    for block in level:
        sides += block.get_two_closest_sides(player.pos)
    # 2 - cull adjacent sides, since they must be internal
    max_dist = max([s.dist_from_point(player.pos) for s in sides])
    # 3 - find color for each point
    pix_color_list = np.zeros((RAYS, 4))
    angs = np.linspace(player.get_bottom_angle(), player.get_top_angle(), RAYS)
    t = time.time()
    for i in range(RAYS-1, 0, -1):
        # linspace spaces array between arg0 and arg2, with arg1 elements
        pix_color_list[i] = raycast_one(player, angs[i], sides, max_dist)
    print('raycast time:', time.time()-t)
    return pix_color_list
    
    
def render(screen, col_list):
    """draws bunch of horisontal lines, width of screen(?) and color from col_list"""
    assert len(col_list) == RAYS  # same length of screen height
    for i, c in enumerate(col_list):
        # Rect(left, top, width, height)
        curr_line = pygame.Rect(0, i*LINES_PER_PIX, SCREEN_SIZE[0], LINES_PER_PIX)
        screen.fill(c, curr_line)
    pygame.display.flip()


def render_line(screen, col, index):
    curr_line = pygame.Rect(0, index*LINES_PER_PIX, SCREEN_SIZE[0], LINES_PER_PIX)
    screen.fill(col, curr_line)


def mainloop(screen, player, world):
    """Main game execution loop. Grabs player input, calculates movement, updates position, and draws to screen"""
    speed = 0.2 # blocks per s
    look_speed = 0.1
    index = 0
    clock = pygame.time.Clock()
    col_list_master = raycast(player, world)
    while 1:
        # basic script to close out if window closed
        dt = clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        if pygame.key.get_pressed()[pygame.K_UP]:
            player.pos[0] += speed*dt/100
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            player.pos[0] -= speed*dt/100
        if pygame.key.get_pressed()[pygame.K_w]:
            player.look_angle += look_speed*dt
        elif pygame.key.get_pressed()[pygame.K_s]:
            player.look_angle -= look_speed*dt
        if player.look_angle > 90:
            player.look_angle = 90
        elif player.look_angle < -120:
            player.look_angle = -120

        # phys stuff here
        col_list = raycast(player, world)
        #for i in range(len(col_list)):
        #    if not np.equal(col_list[i], col_list_master[i]).all():
        #        col_list_master[i] = col_list[i]
        #        render_line(screen, col_list_master[i], i)
        #pygame.display.flip()
        render(screen, col_list[::-1])


def main():
    """Starting point for execution"""
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    block_defs = parse_block_files(["Grass.json", "Dirt.json", "Brick.json", "Alien.json"])
    level, player = parse_level('level_basic.json', block_defs)
    mainloop(screen, player, level)
    # setup player, world, etc


# This lets python know to run the main function
if __name__ == '__main__':
    main()
