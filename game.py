import sys, pygame
import numpy as np
# pygame is in x,y
# point = [x, y]
# Some global values
SCREEN_SIZE = 800, 800
BACKGROUND_COLOR = (0, 0, 0)
BLOCK_SIZE = 1, 1
MIN_DIST = 0.001
MAX_RAY_ITERS = 50


def import_level(filename):
    return level


class Player:
    """Params:
        x,y
        look angle
        look direction (back or front)
    """
    
    def __init__(self, starting_pos):
        self.pos = starting_pos  # x, y 
        self.look_angle = 0  # degrees
        self.look_dir = 'forward'  # 'back' or 'forward'


class Block:
    def __init__(self, top_left, texture_top, texture_side, texture_bottom):
        assert BLOCK_SIZE == len(texture_top) == len(texture_side) == len(texture_bottom) 
        bl = (top_left[0], top_left[1]+BLOCK_SIZE)
        tr = (top_left[0]+BLOCK_SIZE, top_left[1])
        br = (top_left[0]+BLOCK_SIZE, top_left[1]+BLOCK_SIZE)
        self.left_side = VBlockSide(top_left, bl)
        self.right_side = VBlockSide(tr, br)
        self.top_side = HBLockSide(top_left, tr)
        self.bot_side = HBLockSide(bl, br)
        
    def get_two_closest_sides(source_point):
        dists = [self.left_side.dist_from_point(source_point),
                 self.right_side.dist_from_point(source_point),
                 self.top_side.dist_from_point(source_point),
                 self.bot_side.dist_from_point(source_point)]
        dists.sort()
        return dists[:2]


class HBLockSide:
    def __init__(self, left, right, texture):
        assert len(texture) == BLOCK_SIZE
        self.left = left
        self.right = right
        self.texture = texture
        
    def dist_from_point(self, point):
        if point[0] > self.right[0]: 
            return dist_between_points(point, self.top)
        elif point[0] < self.left[0]:
            return dist_between_points(point, self.bot)
        else:  # point y between top and bot ys
            return abs(point[1]-self.top[1])
          
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
        index = int(l1*BLOCK_SIZE/l2)  # floored since 0 is start
        return self.texture[index]
    
    
class VBlockSide:
    def __init__(self, top, bot, texture):
        assert len(texture) == BLOCK_SIZE
        self.top = top
        self.bot = bot
        self.texture = texture
        
    def dist_from_point(point):
        if point[1] > self.top[1]: 
            return dist_between_points(point, self.top)
        elif point[1] < self.bot[1]:
            return dist_between_points(point, self.bot)
        else:  # point y between top and bot ys
            return abs(point[0]-self.top[0])
            
    def adjacent_to(self, other):
        if not isinstance(other, VBlockSide) or self is other:
            return False
        if dist_between_points(self.left, other.left) < MIN_DIST:
            if dist_between_points(self.right, other.rught) < MIN_DIST:
                return True
        return False
        
    def find_color_from_point(self, point):
        l1 = point[1] - self.top[1]
        l2 = self.bot[1] - self.top[1]
        # ------* l1
        # ------*------------- BLOCK_SIZE
        #       ^ index
        index = int(l1*BLOCK_SIZE/l2)  # floored since 0 is start
        return self.texture[index]
        

def dist_between_points(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**(1/2)  # TODO
    
    
def update_player_pos(player, world, delta_x, delta_y):
    pass  # TODO
    
    
def check_colision_at(newpos, world):
    pass  # TODO
    
    
def find_closest_side(pos, sides):
    min_dist = 1000000000
    min_side = None
    for s in sides:
        d = s.dist_from_point(player.pos)
        if d < MIN_DIST:
            # we found a side the point is right on top of, so this must be the one!
            return s, 0
        if d < min_dist:
            min_dist = d
            min_side = s
    return min_side, distance
    
    
def raycast_one(player, angle, sides):
    """Finds the color for a single ray."""
    curr_point = player.pos
    i = 0
    closest, distance = find_closest_side(player.pos, sides)
    while i < MAX_RAY_ITERS
        if distance == 0:
            return side.find_color_from_point(player.pos)
        else:
            curr_point = (curr_point[0] + math.cos(angle)*distance
                          curr_point[1] + math.sin(angle)*distance)
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
    angles = 
    for ang in np.linspace(player.look_angle, SCREEN_SIZE[1], player.fov_angle):
        # linspace spaces array between arg0 and arg2, with arg1 elements
        pix_color_list.append(raycast_one(player, angle, sides))
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
            if event.type == pygame.QUIT: sys.exit()

        # phys stuff here
        col_list = raycast(player, level)
        render(screen, col_list)
        index += 1


def main():
    """Starting point for execution"""
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    mainloop(screen, None, None)
    # setup player, world, etc


# This lets python know to run the main function
if __name__ == '__main__':
    main()