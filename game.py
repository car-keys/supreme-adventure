import sys, pygame, math, json
import numpy as np
# pygame is in x,y
# point = [x, y]
# Some global values
SCREEN_SIZE = (300, 800)
BACKGROUND_COLOR = pygame.Color(255, 255, 255)
TEXTURE_LEN = 32
BLOCK_SIZE = 1
MIN_DIST_FOR_EQUAL = 0.001
MAX_RAY_ITERS = 50
DEFAULT_LOOK_ANGLE = 0
DEFALT_LOOK_FOV_RADIUS = 60


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
        self.top_texture = top_texture
        self.side_texture = side_texture
        self.bot_texture = bot_texture
        
    def make_one(self, loc):
        return Block(loc, self.top_texture, self.side_texture, self.bot_texture)


class Player:
    """Params:
        x,y
        look angle
        look direction (back or front)
    """
    
    def __init__(self, starting_pos):
        self.pos = starting_pos  # x, y 
        self.look_angle = DEFAULT_LOOK_ANGLE  # degrees
        self.look_dir = 'forward'  # 'back' or 'forward'
        self.fov_radius = DEFALT_LOOK_FOV_RADIUS

    def get_bottom_angle(self):
        return self.look_angle-self.fov_radius

    def get_top_angle(self):
        return self.look_angle + self.fov_radius


class Block:
    def __init__(self, top_left, texture_top, texture_side, texture_bottom):
        assert TEXTURE_LEN == len(texture_top) == len(texture_side) == len(texture_bottom)
        bl = (top_left[0], top_left[1]-BLOCK_SIZE)
        tr = (top_left[0]+BLOCK_SIZE, top_left[1])
        br = (top_left[0]+BLOCK_SIZE, top_left[1]-BLOCK_SIZE)
        self.left_side = VBlockSide(top_left, bl, texture_side)
        self.right_side = VBlockSide(tr, br, texture_side)
        self.top_side = HBLockSide(top_left, tr, texture_top)
        self.bot_side = HBLockSide(bl, br, texture_top)
        
    def get_two_closest_sides(self, source_point):
        sides = [self.left_side,
                 self.right_side,
                 self.top_side,
                 self.bot_side]
        sides.sort(key=lambda a: a.dist_from_point(source_point))
        return sides[:2]


class HBLockSide:
    def __init__(self, left, right, texture):
        assert len(texture) == TEXTURE_LEN
        self.left = left
        self.right = right
        self.texture = texture
        
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
        if dist_between_points(self.left, other.left) < MIN_POINT_ADJ_DIST:
            if dist_between_points(self.right, other.rught) < MIN_POINT_ADJ_DIST:
                return True
        return False
    
    def find_color_from_point(self, point):
        l1 = point[0] - self.left[0]
        l2 = self.right[0] - self.left[0]
        # ------* l1
        # ------*------------- BLOCK_SIZE
        #       ^ index
        index = int(l1*TEXTURE_LEN/l2)  # floored since 0 is start
        return self.texture[index]
    
    
class VBlockSide:
    def __init__(self, top, bot, texture):
        assert len(texture) == TEXTURE_LEN
        self.top = top
        self.bot = bot
        self.texture = texture
        
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
        if dist_between_points(self.left, other.left) < MIN_DIST_FOR_EQUAL:
            if dist_between_points(self.right, other.rught) < MIN_DIST_FOR_EQUAL:
                return True
        return False
        
    def find_color_from_point(self, point):
        l1 = point[1] - self.top[1]
        l2 = self.bot[1] - self.top[1]
        # ------* l1
        # ------*------------- BLOCK_SIZE
        #       ^ index
        index = int(l1*TEXTURE_LEN/l2)  # floored since 0 is start
        return self.texture[index]
        

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
    
    
def raycast_one(player, angle, sides):
    """Finds the color for a single ray."""
    curr_point = player.pos
    i = 0

    while i < MAX_RAY_ITERS:
        closest_side, distance = find_closest_side(curr_point, sides)
        if distance == 0:
            return closest_side.find_color_from_point(curr_point)
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
    # TODO
    # 3 - find color for each point
    pix_color_list = []
    for ang in np.linspace(player.get_bottom_angle(), player.get_top_angle(), SCREEN_SIZE[1]):
        # linspace spaces array between arg0 and arg2, with arg1 elements
        pix_color_list.append(raycast_one(player, ang, sides))
    pix_color_list.reverse()
    return pix_color_list
    
    
def render(screen, col_list):
    """draws bunch of horisontal lines, width of screen(?) and color from col_list"""
    assert len(col_list) == SCREEN_SIZE[1]  # same length of screen height
    for i, c in enumerate(col_list):
        # Rect(left, top, width, height)
        curr_line = pygame.Rect(0, i, SCREEN_SIZE[0], 1) 
        screen.fill(c, curr_line)
    pygame.display.flip()
    
    
def mainloop(screen, player, world):
    """Main game execution loop. Grabs player input, calculates movement, updates position, and draws to screen"""
    
    index = 0
    while 1:
        # basic script to close out if window closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # phys stuff here
        col_list = raycast(player, world)
        render(screen, col_list)
        index += 1


def main():
    """Starting point for execution"""
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    block_defs = parse_block_files(["Grass.json", "Dirt.json"])
    level, player = parse_level('level_flat.json', block_defs)
    mainloop(screen, player, level)
    # setup player, world, etc


# This lets python know to run the main function
if __name__ == '__main__':
    main()
