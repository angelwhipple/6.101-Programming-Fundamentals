#!/usr/bin/env python3

import typing
import doctest
import time

# NO ADDITIONAL IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION
steps = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    """
    board = [[0 for c in range(num_cols)] for r in range(num_rows)]
    for b in bombs:
        board[b[0]][b[1]] = '.'
    hidden = [[True for c in range(num_cols)] for r in range(num_rows)]
    
    def get_neighbors(r, c):
        return [(r+i, c+j) for i, j in steps if 0 <= r+i < num_rows and \
                    0 <= c+j < num_cols and (r+i, c+j) not in bombs]
    for b in bombs:
        neighbors = get_neighbors(*b)
        for n in neighbors:
            board[n[0]][n[1]] += 1
            
    return {
        "dimensions": (num_rows, num_cols),
        "board": board,
        "hidden": hidden,
        "state": "ongoing",
    }


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    """
    rows, cols = game['dimensions'][0], game['dimensions'][1]
    def get_neighbors(r, c):
        return [(r+i, c+j) for i, j in steps if 0 <= r+i < rows and \
                    0 <= c+j < cols and game['board'][r+i][c+j] != '.' ]
            
    def check_victory(game):
        hidden = [(r, c) for r in range(rows) for c in range(cols) \
                  if game['hidden'][r][c]]
        for tile in hidden:
            if game['board'][tile[0]][tile[1]] != '.':
                return False
        return True
                
    def dig_recursive(row, col):
        if game["state"] == "defeat" or game["state"] == "victory" or \
            game['hidden'][row][col] == False:
            return 0 
        game['hidden'][row][col] = False
        if game['board'][row][col] == 0:
            neighbors = get_neighbors(row, col)
            return 1 + sum([dig_recursive(n[0], n[1]) for n in neighbors])
        else:
            if game['board'][row][col] == '.':
                game['state'] = 'defeat'
            return 1
            
    revealed = dig_recursive(row, col)
    if check_victory(game):
        game['state'] = 'victory'
    return revealed
    


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    rows, cols = game['dimensions'][0], game['dimensions'][1]
    array = [[str(game['board'][r][c]) for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if game['board'][r][c] == 0:
                array[r][c] = ' '
            if not xray and game['hidden'][r][c]:
                array[r][c] = '_'
    return array
        


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    array = render_2d_locations(game, xray)
    board = '\n'.join([''.join(row) for row in array])
    return board
        


# N-D IMPLEMENTATION

# HELPERS
def init_nested(dimen, val):
    """
    Initiates a nested list of the given dimensions with each value = val

    """
    dimen = list(dimen)
    if len(dimen) == 1:
        return [val for i in range(dimen[0])]
    else:
        d = dimen.pop(0)
        return [init_nested(dimen, val) for i in range(d)]
        
             

def get_coord(lst, coord):
    """
    Returns value at a given coordinate within a nested list 

    """
    if type(lst[0]) != list:
        return lst[coord[0]]
    else:
        return get_coord(lst[coord[0]], coord[1:])


def set_coord(lst, coord, val):
    """
    Sets value at given coordinate within a nested list to val 

    """
    if type(lst[0]) != list:
        lst[coord[0]] = val
    else:
        set_coord(lst[coord[0]], coord[1:], val)
            
def increment_coord(lst, coord):
    """
    Increments value at given coordinate within a nested list by 1 

    """
    if type(lst[0]) != list:
        lst[coord[0]] += 1
    else:
        increment_coord(lst[coord[0]], coord[1:])
    

def valid_coords(dimen):
    """
    Returns all valid coordinates in a board of the given dimensions
    
    """
    
    if len(dimen) == 1:
        for i in range(dimen[0]):
            yield (i,)
    else:
        for n in valid_coords(dimen[1:]):
            for i in range(dimen[0]):
                yield (i,)+n
        

nd_steps = [-1, 0, 1]
def get_comrades(coord, dimen):
    """
    Returns all valid neighboring coordinates of a given coord in an array of
    given dimensions

    """
    if len(coord) == 1:
        for s in nd_steps:
            if 0 <= coord[0]+s < dimen[0]:
                yield (coord[0]+s,)
    else:
        for c in get_comrades(coord[1:], dimen[1:]):
            for s in nd_steps:
                if 0 <= coord[0]+s < dimen[0]:
                    yield (coord[0]+s,)+c

                
def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: ongoing
    """
    board, hidden = init_nested(dimensions, 0), init_nested(dimensions, True)
    bombs = set(bombs)
    
    for b in bombs:
        set_coord(board, b, '.')
        neighbors = get_comrades(b, dimensions)
        for n in neighbors:
            if n not in bombs:
                increment_coord(board, n)

    return {'dimensions': dimensions, 
            'board': board, 
            'hidden': hidden,
            'state': 'ongoing'}


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: defeat
    """
    all_coords = valid_coords(game['dimensions'])
    def check_victory():
        for c in all_coords:
            val, hidden = get_coord(game['board'], c), get_coord(game['hidden'], c)
            if isinstance(val, int) and hidden:
                return False
        return True
    
    def dig_recursive(game, coord):
        if get_coord(game['hidden'], coord) == False or game['state'] == 'defeat' \
            or game['state'] == 'victory':
            return 0
        set_coord(game['hidden'], coord, False)
        value =  get_coord(game['board'], coord)
        if value == 0:
            revealed, neighbors = 1, get_comrades(coord, game['dimensions'])
            for n in neighbors:
                revealed += dig_recursive(game, n)
            return revealed
        elif value == '.':
            game['state'] = 'defeat'
            return 1
        else:
            return 1
    

    revealed = dig_recursive(game, coordinates)
    if check_victory():
        game['state'] = 'victory'
        
    return revealed
        


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    res, valid = init_nested(game['dimensions'], 0), valid_coords(game['dimensions'])
    
    for c in valid:
        val = str(get_coord(game['board'], c))
        if val == '0':
            val = ' '
        if xray:
            set_coord(res, c, val)
        else:
            if get_coord(game['hidden'], c):
                set_coord(res, c, '_')
            else:
                set_coord(res, c, val)
    return res


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    #doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    
    # game = {'dimensions': (2, 4), 'board': [['.', 3, 1, 0],
    # ['.', '.', 1, 0]], 'hidden': [[True, False, True, True],
    # [True, True, True, True]], 'state': 'ongoing'}
    # print(dig_2d(game, 0, 3))
    # 3d = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # 1d = new_game_nd((4,), [(1,), (3,)])
    # 2d = new_game_nd((2, 4), [(0, 3), (1, 2), (0, 1)])
    # print(g)
    
    # neighbors = get_comrades((5, 13, 0))
    # valid = valid_coords((10, 20, 3))
    # print(valid)
    
    # error = manip_coord(game['board'], (1,1), None, False, True)
    # print(f'{error=}')
    
    # game = {'dimensions': (2, 4),
    # 'board': [['.', 3, 1, 0],
    # ['.', '.', 1, 0]],
    # 'hidden': [[True, False, True, True],
    # [True, True, True, True]],
    # 'state': 'ongoing'} 
    # print(dig_nd(game, (0, 3)))
    
    
    # TEST_DIRECTORY = os.path.dirname(__file__)
    # exp_fname = os.path.join(TEST_DIRECTORY, 'test_outputs', 'testnd_newsmall6dgame.pickle')
    # inp_fname = os.path.join(TEST_DIRECTORY, 'test_inputs', 'testnd_newsmall6dgame.pickle')
    # with open(exp_fname, 'rb') as f:
    #     expected = pickle.load(f)
    
    # with open(inp_fname, 'rb') as f:
    #     inputs = pickle.load(f)
    # result = new_game_nd(inputs['dimensions'], inputs['bombs'])
    
    
