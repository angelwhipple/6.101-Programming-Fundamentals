#!/usr/bin/env python3

##################
# Game Constants #
##################
import sys;
print(sys.version)

TILE_SIZE = 128

# vertical movement
GRAVITY = -9
MAX_DOWNWARD_SPEED = 48
PLAYER_JUMP_SPEED = 62
PLAYER_JUMP_DURATION = 3
PLAYER_BORED_THRESHOLD = 60

# horizontal movement
PLAYER_DRAG = 6
PLAYER_MAX_HORIZONTAL_SPEED = 48
PLAYER_HORIZONTAL_ACCELERATION = 16


# maps single-letter strings to the name of the object they
# represent
SPRITE_MAP = {
    "p": "slight_smile",
    "c": "cloud",
    "=": "black_large_square",
    "B": "classical_building",
    "C": "castle",
    "u": "cactus",
    "t": "tree",
    's': 'thunderstorm',
    'h': 'helicopter',
    'w': 'water_wave'

}


STORM_LIGHTNING_ROUNDS = 5
STORM_RAIN_ROUNDS = 10

BEE_SPEED = 40
CATERPILLAR_SPEED = 16
PEANUT_SPEED = 60

CHIPMUNK_POWER = 5

ENEMIES = {
    'f': ["fire", (0, 0)],
    '~': ['caterpillar', (CATERPILLAR_SPEED, 0)],
    'e' : ['bee', (0, BEE_SPEED)]
}

##########################
# Classes and Game Logic #
##########################


class Rectangle:
    """
    A rectangle object to help with collision detection and resolution.
    """

    def __init__(self, x, y, w, h):
        """
        Initialize a new rectangle.

        `x` and `y` are the coordinates of the bottom-left corner. `w` and `h`
        are the dimensions of the rectangle.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
     
    @property
    def center(self):
        return (self.x+self.w//2, self.y+self.h//2)
    

    def intersects(self, other):
        """
        Check whether `self` and `other` (another Rectangle) overlap.

        Rectangles are open on the top and right sides, and closed on the
        bottom and left sides; concretely, this means that the rectangle
        [0, 0, 1, 1] does not intersect either of [0, 1, 1, 1] or [1, 0, 1, 1].
        
        >>> Rectangle(2, 2, 2, 3).intersects(Rectangle(0, 0, 4, 3))
        True
        
        >>> Rectangle(0, 0, 5, 4).intersects(Rectangle(2, 1, 1, 1))
        True
        """
        overlap = (self.x+self.w <= other.x or self.y+self.h <= other.y or \
            other.x+other.w <= self.x or other.y+other.h <= self.y)
        return not overlap


    def translation_vector(r1, r2):
        """
        Computes how much `r2` needs to move to stop intersecting `r1`.

        If `r2` does not intersect `r1`, return `None`.  Otherwise, return a
        minimal pair `(x, y)` such that translating `r2` by `(x, y)` would
        suppress the overlap. `(x, y)` is minimal in the sense of the "L1"
        distance; the sum of `abs(x)` and `abs(y)` should be
        as small as possible.

        When two pairs `(x1, y1)` and `(x2, y2)` are tied in terms of this
        metric, returns the one whose first element has the smallest
        magnitude.
        """
        if not r2.intersects(r1):
            return None
        # max distances to move in each dir
        right, left, up, down = (r1.x+r1.w-r2.x, 0), (-(r2.x+r2.w-r1.x), 0), \
            (0, r1.y+r1.h-r2.y), (0, -(r2.y+r2.h-r1.y))
        moves = sorted([right, left, up, down], key=lambda pair:abs(pair[0])) 
        return min(moves, key=lambda m: abs(m[0])+abs(m[1]))
        
        
            

def get_tiles(lvl_map):
    lvl_map.reverse()
    width, height = len(lvl_map[0]), len(lvl_map)
    for y in range(height):
        for x in range(width):
            yield lvl_map[y][x], x, y
    

class Sprite:
    size = 128
    def __init__(self, x, y, texture):
        self.x, self.y = (x*self.size, y*self.size)
        self.texture = texture
        
    def __str__(self):
        return f'Sprite({self.texture}: ({self.x}, {self.y}))'
    

class Dynam(Sprite):
    def __init__(self, x, y, texture, velocity):
        Sprite.__init__(self, x, y, texture)
        self.vx, self.vy = velocity
    
    def move(self, ax, ay):
        """
        Helper function for applying changes in velocity and position to dynamic sprites.
        """ 
        # cap Vy if current Vy + Ay exceeds max down velocity
        if self.vy+ay < -MAX_DOWNWARD_SPEED:
            self.vx, self.vy = (self.vx+ax, -MAX_DOWNWARD_SPEED)
        else:
            self.vx, self.vy = (self.vx+ax, self.vy+ay)
        
        self.x, self.y = (self.x+self.vx, self.y+self.vy)

    def __str__(self):
        return f'Dynamic({self.texture}: ({self.x}, {self.y}), {self.vy=}, {self.y=})'
        
class Player(Dynam):
    def __init__(self, x, y, texture, velocity):
        Dynam.__init__(self, x, y, texture, velocity)
        self.jump_hold, self.peanuts = [False, 0], 0
        
    def apply_drag(self):
        # check if drag exceeds |Vx|
        drag = abs(self.vx) if PLAYER_DRAG > abs(self.vx) else PLAYER_DRAG
            
        # apply drag acceleration
        if self.vx > 0:
            self.vx -= drag
        if self.vx < 0:
            self.vx += drag
        
    def move(self, ax, ay):
        """
        Helper function for applying changes in velocity and position to dynamic sprites.
        """ 
        # cap Vy if current Vy + Ay exceeds max down velocity
        if self.vy+ay < -MAX_DOWNWARD_SPEED:
            self.vx, self.vy = (self.vx+ax, -MAX_DOWNWARD_SPEED)
        else:
            self.vx, self.vy = (self.vx+ax, self.vy+ay)
            
        self.apply_drag()
        
        # cap Vx at max horizontal velocity after applying Ax + drag
        self.vx = PLAYER_MAX_HORIZONTAL_SPEED if self.vx > PLAYER_MAX_HORIZONTAL_SPEED else self.vx
        self.vx = -PLAYER_MAX_HORIZONTAL_SPEED if self.vx < -PLAYER_MAX_HORIZONTAL_SPEED else self.vx
        
        self.x, self.y = (self.x+self.vx, self.y+self.vy)
    
    def __str__(self):
        return f'Player({self.texture}: ({self.x}, {self.y}), {self.vy=}, {self.y=})'



class Game:
    def __init__(self, level_map):
        """
        Initialize a new game, populated with objects from `level_map`.

        `level_map` is a 2D array of 1-character strings; all possible strings
        (and some others) are listed in the SPRITE_MAP dictionary.  Each
        character in `level_map` corresponds to a sprite of size `TILE_SIZE *
        TILE_SIZE`.
        """
        self.bored, self.status, self.sprites, self.dynams, self.player, self.player2 = 0, 'ongoing', set(), set(), None, None
        self.storm, self.storms = ['thunderstorm', 0], set()
        
        for tile, x, y in get_tiles(level_map):
            if tile == 'p':
                self.player, self.player2 = Player(x, y, 'slight_smile', (0, 0)), Player(x, y, 'slight_smile', (0, 0))
                self.dynams.add(self.player)
                self.sprites.add(self.player)
            elif tile == 's':
                self.storms.add(Sprite(x, y, SPRITE_MAP['s']))
            elif tile in ENEMIES:
                self.dynams.add(Dynam(x, y, ENEMIES[tile][0], ENEMIES[tile][1]))
            elif tile in SPRITE_MAP:
                self.sprites.add(Sprite(x, y, SPRITE_MAP[tile]))
            self.sprites.update(self.dynams)
            self.sprites.update(self.storms)
                
    def search_sprites(self):
        yield from self.sprites

    def collisions(self, ind, type='static'):
        dynam_dead, static_dead = set(), set()
        for d in self.dynams:
            dynam = Rectangle(d.x, d.y, d.size, d.size)
            for s in self.search_sprites():
                # dynamic-static
                if type == 'static' and not (isinstance(s, Player) or isinstance(s, Dynam)):
                    static = Rectangle(s.x, s.y, s.size, s.size)
                    if dynam.intersects(static):
                        # end player jump hold: static col from above
                        if d is self.player and d.y >= s.y:
                            d.jump_hold[0] = False

                        vec = static.translation_vector(dynam)
                        dx, dy = vec
                        # only use hor/ver displ vectors
                        if vec[ind] == 0:
                            d.x, d.y = (d.x+dx, d.y+dy)
                            dynam.x += dx
                            dynam.y += dy
                            if d.texture == 'bee':
                                d.vy = -d.vy
                            elif d.texture == 'caterpillar':
                                if dy == 0 and dx:
                                    d.vx = -d.vx
                                elif dx == 0 and dy:
                                    d.vy = 0
                            elif d is self.player:
                                # slowdown: check for dx/dy and vx/vy opposite signs
                                if (dx > 0 and d.vx < 0) or (dx < 0 and d.vx > 0):
                                    d.vx = 0
                                if (dy > 0 and d.vy < 0) or (dy < 0 and d.vy > 0):
                                    d.vy = 0
                                # revert from ship texture if moving horizontally from  water
                                if d.texture == 'passenger_ship' and s.texture != 'water_wave' and dy and dx == 0:
                                    d.texture = 'slight_smile'
                        # victory check
                        if d is self.player and s.texture == 'castle':
                            self.status = 'victory'
                            d.texture = 'partying_face'
                        # defeat check: player-static enemy collision
                        elif d is self.player and (s.texture == 'cactus' or s.texture == 'thunderstorm'):
                            self.status = 'defeat'
                            d.texture = 'injured'
                        elif d is self.player and s.texture == 'helicopter':
                            static_dead.add(s)
                            d.texture = 'helicopter'
                        elif d is self.player and s.texture == 'water_wave':
                            d.texture = 'passenger_ship'

                # dynamic-dynamic
                else:
                    if isinstance(s, Dynam) and s is not self.player:
                        enem = Rectangle(s.x, s.y, s.size, s.size)
                        if dynam.intersects(enem):
                            if d is self.player:
                                # check for caterpillar collision from above
                                vec = enem.translation_vector(dynam)
                                dx, dy = vec
                                if s.texture == 'caterpillar' and dx == 0 and dy > 0:
                                    dynam_dead.add(s)
                                # defeat check: player-dynamic enemy collision
                                else:
                                    self.status = 'defeat'
                                    self.player.texture = 'injured'
                            elif d.texture == 'fire' and s.texture == 'caterpillar':
                                dynam_dead.add(s)
        # clear dead sprites after iteration
        self.dynams.difference_update(dynam_dead)
        self.sprites.difference_update(dynam_dead)         
        self.sprites.difference_update(static_dead)         
                    
    def timestep(self, keys):
        """
        Simulate the evolution of the game state over one time step.  `keys` is
        a list of currently pressed keys.
        """
        if self.status != 'ongoing':
            return
        
        # storm blinking
        storm_states = {'thunderstorm': STORM_LIGHTNING_ROUNDS, 'rainy': STORM_RAIN_ROUNDS}
        if self.storm[1]+1 < storm_states[self.storm[0]]:
                self.storm[1] += 1
        else:
            self.storm = ['rainy', 0] if self.storm[0] == 'thunderstorm' else ['thunderstorm', 0]
            for storm in self.storms:
                storm.texture = self.storm[0]
                
        if not keys:  
            self.bored += 1
        else:
            self.bored = 0
            
        # no boredom if player is a choppa/ship
        if self.player.texture != 'helicopter' and self.player.texture != 'passenger_ship':
            if self.bored > PLAYER_BORED_THRESHOLD:
                self.player.texture = 'sleeping'
                return
            else:
                self.player.texture = 'slight_smile'

        # if self.player2.texture != 'helicopter' and self.player2.texture != 'passenger_ship':
        #     if self.bored > PLAYER_BORED_THRESHOLD:
        #         self.player2.texture = 'sleeping'
        #         return
        #     else:
        #         self.player2.texture = 'slight_smile'
                
        # update dynamic sprite position/accel due to G
        ax, ax2, ay = 0, 0, GRAVITY
                
        if 'left' in keys:
            ax -= PLAYER_HORIZONTAL_ACCELERATION
        if 'right' in keys:
            ax += PLAYER_HORIZONTAL_ACCELERATION

        # if 'a' in keys:
        #     ax2 -= PLAYER_HORIZONTAL_ACCELERATION
        # if 'd' in keys:
        #     ax2 += PLAYER_HORIZONTAL_ACCELERATION


        # modified jump handling
        if 'up' in keys:
            if self.player.texture == 'helicopter':
                self.player.vy = PLAYER_JUMP_SPEED
            else:
                # revert from ship texture 
                if self.player.texture == 'passenger_ship':
                    self.player.texture = 'slight_smile'
                if not self.player.jump_hold[0]:
                    self.player.jump_hold = [True, PLAYER_JUMP_DURATION]

        if self.player.jump_hold[1]:
            self.player.vy = PLAYER_JUMP_SPEED
            self.player.jump_hold[1] -= 1

        # if 'w' in keys:
        #     if self.player2.texture == 'helicopter':
        #         self.player2.vy = PLAYER_JUMP_SPEED
        #     else:
        #         # revert from ship texture 
        #         if self.player2.texture == 'passenger_ship':
        #             self.player2.texture = 'slight_smile'
        #         if not self.player2.jump_hold[0]:
        #             self.player2.jump_hold = [True, PLAYER_JUMP_DURATION]

        # if self.player2.jump_hold[1]:
        #     self.player2.vy = PLAYER_JUMP_SPEED
        #     self.player2.jump_hold[1] -= 1

        self.player.move(ax, ay)
        # self.player2.move(ax2, ay)

        # move dynamic enemy sprites
        for s in self.dynams:
            if s.texture == 'fire':
                s.move(0, ay)
            elif s.texture == 'bee':
                s.move(0, 0)
            elif s.texture == 'caterpillar':
                s.move(0, ay)

        # dynamic-static collision detection, vertical
        self.collisions(0)
        # horizontal
        self.collisions(1)

        # dynamic-dynamic collision detection
        self.collisions(0, 'dynamic')
        self.collisions(1, 'dynamic')

            
        # defeat check
        if self.player.y < -TILE_SIZE:
            self.status = 'defeat'
            self.player.texture = 'injured'
        
                
        
                
    
    def render(self, w, h):
        """
        Report status and list of sprite dictionaries for sprites with a
        horizontal distance of w//2 from player. 
        """
        window, px = [], self.player.x
        # initialize rectangle centered on player
        player = Rectangle(px-w//2, 0, w, h)
        # search for in-frame sprites
        for s in self.search_sprites():
            sprite = Rectangle(s.x, s.y, s.size, s.size)
            if player.intersects(sprite):
                window.append({'texture': s.texture, 'pos': (s.x, s.y), 'player': isinstance(s, Player)})
        return (self.status, window)

if __name__ == "__main__":
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    lvlmap = [
    "p          ffffffffffffffffffffff           C",
    '=============================================',
    ]
    # game = Game(lvlmap)
    # for sprite in game.sprites:
    #     print(sprite)
    
    
    # for i in range(1, 9): 
    #     print(f'Timestep:{i}')
    #     game.timestep(['right'])
        
    # print(game.render(640, 384))
    
    r1 = Rectangle(2, 2, 2, 3)
    r2 = Rectangle(0, 0, 4, 3)
    # print(Rectangle.translation_vector(r2, r1))

    # p = game.player
    # p.x, p.y = (0, 0)
    # print('n=0')
    # game.timestep('[up]')
    # for n in range(8):
    #     print(f'{n=}')
    #     game.timestep([])


    
