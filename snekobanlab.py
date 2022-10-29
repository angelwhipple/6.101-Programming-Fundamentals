# Snekoban Game

import json
import typing


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation 
    
    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    """
    internal = { 'wall': set(), 'computer': set(), 'target': set(), 'rows': len(level_description),
                'player':set() }
    for i in range(len(level_description)):
        internal['cols'] = len(level_description[i])
        for j in range(len(level_description[i])):
            if 'wall' in level_description[i][j]:
                internal['wall'].add((i, j))
            if 'computer' in level_description[i][j]:
                internal['computer'].add((i, j))
            if 'target' in level_description[i][j]:
                internal['target'].add((i, j))
            if 'player' in level_description[i][j]:
                internal['player'].add((i, j))
    return internal, (frozenset(internal['computer']), frozenset(internal['player']))


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    # Count computers and targets on board
    c = len(game[0]['computer'])
    t = len(game[0]['target'])
    # Check for unequal/no computers and targets
    if c != t or c == 0 or t == 0:
        return False
    else:
        if game[0]['computer'] == game[0]['target']:
            return True
        return False
            

# Helper function for checking/moving valid steps across the board
def move_valid_step(game, loc, step): 
    newi, newj = step[0]+loc[0], step[1]+loc[1]
    # check for obstacle, no moves
    if (newi, newj) in game['wall']:
        return game
    # if no obstacles, check for further obstacles in that direction, move
    elif (newi, newj) in game['computer']:
        if (newi+step[0], newj+step[1]) not in game['wall'] and \
            (newi+step[0], newj+step[1]) not in game['computer']:
                game['player'].add((newi, newj))
                game['player'].remove((loc[0], loc[1]))
                game['computer'].remove((newi, newj))
                game['computer'].add((newi+step[0], newj+step[1]))
    else:
        game['player'].add((newi, newj))
        game['player'].remove((loc[0], loc[1]))
    return game

def get_loc(game):
    return list(game[0]['player'])[0]

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of: {'up', 'down', 'left', 'right'}.

    This function should not mutate the input.
    """
    # Copy current game representation
    replica = { 'wall': game[0]['wall'].copy(), 'computer': game[0]['computer'].copy(), \
           'target': game[0]['target'].copy(), 'rows': game[0]['rows'], 'cols': game[0]['cols'], \
               'player': game[0]['player'].copy() }
    step = direction_vector[direction]
    # Get current player location
    loc = get_loc(game)
    # Check for valid step in given direction, update board
    res = move_valid_step(replica, loc, step)
    return res, (frozenset(res['computer']), frozenset(res['player']))
            

def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that is a suitable input for new_game
    (a list of lists of lists of strings).

    """
    level_description = [ [ [] for j in range(game[0]['cols']) ] for i in range(game[0]['rows']) ]
    elements = [elem for elem in game[0] if elem != 'rows' and elem != 'cols']
    for elem in elements:
        for i,j in game[0][elem]:
            level_description[i][j].append(elem)
    return level_description

# Helper func, check if new possible computer postion is in a corner
# def not_in_corner(game, newi, newj, step):
#     # case: top left corner
#     if 'wall' in game[newi+step[0]-1][newj+step[1]] and 'wall' in \
#         game[newi+step[0]][newj+step[1]-1]:
#         return False
#     # case: top right corner
#     elif 'wall' in game[newi+step[0]-1][newj+step[1]] and 'wall' in \
#         game[newi+step[0]][newj+step[1]+1]:
#             return False
#     # case: bottom left corner
#     elif 'wall' in game[newi+step[0]+1][newj+step[1]] and 'wall' in \
#         game[newi+step[0]][newj+step[1]-1]:
#             return False
#     # case: bottom right corner
#     elif 'wall' in game[newi+step[0]+1][newj+step[1]] and 'wall' in \
#         game[newi+step[0]][newj+step[1]+1]:
#             return False
#     else:
#         return True

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    # base case: game satisfies victory check, return empty list (no moves)
    if victory_check(game):
        return []
    agenda = [ ([], game) ]
    visited = { game[1] }
    while agenda:
        this = agenda.pop(0)
        sequence, board = this[0], this[1]
        for d in direction_vector:
            next_state = step_game(board, d)
            if victory_check(next_state):
                return sequence+[d]
            if next_state[1] not in visited:
                visited.add(next_state[1])
                agenda.append((sequence+[d], next_state))
    # no victory path found in agenda, return None
    return None
    


if __name__ == "__main__":
#     m1_008 = new_game([
#   [[], [], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
#   [[], [], ["wall"], [], ["target"], ["target"], ["player"], ["wall"]],
#   [[], [], ["wall"], [], ["computer"], ["computer"], [], ["wall"]],
#   [[], [], ["wall"], ["wall"], [], ["wall"], ["wall"], ["wall"]],
#   [[], [], [], ["wall"], [], ["wall"], [], []],
#   [[], [], [], ["wall"], [], ["wall"], [], []],
#   [["wall"], ["wall"], ["wall"], ["wall"], [], ["wall"], [], []],
#   [["wall"], [], [], [], [], ["wall"], ["wall"], []],
#   [["wall"], [], ["wall"], [], [], [], ["wall"], []],
#   [["wall"], [], [], [], ["wall"], [], ["wall"], []],
#   [["wall"], ["wall"], ["wall"], [], [], [], ["wall"], []],
#   [[], [], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], []]
# ])
#     print(solve_puzzle(m1_008))
#     m1_044 = new_game([
#   [["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
#   [["wall"], ["player"], ["computer"], ["target"], ["wall"]],
#   [["wall"], ["wall"], ["wall"], ["wall"], ["wall"]]
# ])
#     print(solve_puzzle(m1_044))
    m1_001 = new_game([
  [["wall"], ["wall"], ["wall"], ["wall"], [], []],
  [["wall"], [], ["target"], ["wall"], [], []],
  [["wall"], [], [], ["wall"], ["wall"], ["wall"]],
  [["wall"], ["target", "computer"], ["player"], [], [], ["wall"]],
  [["wall"], [], [], ["computer"], [], ["wall"]],
  [["wall"], [], [], ["wall"], ["wall"], ["wall"]],
  [["wall"], ["wall"], ["wall"], ["wall"], [], []]
])
    print(solve_puzzle(m1_001))
