import sys, pygame

# Some global values
SCREEN_SIZE = 800, 800
BACKGROUND_COLOR = (0, 0, 0)

def import_level(filename):
    return level

class Player:
    """Params:
        x,y
        look angle
        look direction (back or front)
    """
    pass


def update_player_pos(player, world):
    pass

def raycast(player, level):
    """Calculates the color of every pixel on the screen, using the player's head position and angle"""
    pass
    
    
    return pix_color_list
    
    
def render(screen, col_list):
    """draws bunch of horisontal lines, width of screen(?) and color from col_list"""
    assert len(col_list) == SCREEN_SIZE[0]  # same length of screen height
    screen.fill(BACKGROUND_COLOR)
    for i, c in enumerate(col_list):
        # Rect(left, top, width, height)
        curr_line = pygame.Rect(0, i, SCREEN_SIZE[1], 1) 
        screen.fill(c, curr_line)
    pygame.display.flip()
    
    
def mainloop(screen, player, world):
    """Main game execution loop. Grabs player input, calculates movement, updates position, and draws to screen"""
    
    index = 0
    while 1:
        # basic script to close out if window closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # stuff here
        
        # Simple test colors, changing every frame for performance test
        test_colors = []
        for i in range(SCREEN_SIZE[0]):
            mod_i  = (i+index) % 255
            test_colors.append(pygame.Color(mod_i, mod_i, mod_i))
        render(screen, test_colors)
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