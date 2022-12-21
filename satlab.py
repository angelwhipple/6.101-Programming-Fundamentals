#!/usr/bin/env python3

import sys
import typing
import doctest

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS

def mod_formula(formula, var, truth):
    """
    Given a CNF formula, a variable, and a T/F value, returns a new formula 
    that represents the result of omitting literals and satisfying clauses by 
    the assumption of assigning variable the specified truth value.

    >>> mod_formula([
    ...         [('a', True), ('b', True), ('c', True)],
    ...         [('a', False), ('f', True)],
    ...         [('d', False), ('e', True), ('a', True), ('g', True)],
    ...         [('h', False), ('c', True), ('a', False), ('f', True)],
    ...         ], 'e', True)
    [[('a', True), ('b', True), ('c', True)], [('a', False), ('f', True)], 
     [('h', False), ('c', True), ('a', False), ('f', True)]]
    >>> mod_formula([[('f', True)], [('h', False), ('c', True), ('f', True)]], 'f', True)
    []
    >>> mod_formula([[('f', True)], [('h', False), ('c', True), ('f', True)]], 'f', False)
    [[], [('h', False), ('c', True)]]
    """
    new_formula = []
    for clause in formula:        
        # if literal containing var exists and truth value aligns, skip clause
        if [literal for literal in clause if var in literal and literal[1] == truth]:
            continue
        # add clause to the formula w/o var (assume it evals to false)
        else:
            new_clause = [(literal[0], literal[1]) for literal in clause if var not in literal]
            new_formula.append(new_clause)
    return new_formula

def get_unit_clause(formula):
    for clause in formula:
        if len(clause) == 1:
            return clause[0]
    return None

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]]) is None
    True
    """
    assign, search = {}, True
    while search:
        search = False
        for clause in formula:
            if len(clause) == 1:
                elem, truth = clause[0][0], clause[0][1]
                formula = mod_formula(formula, elem, truth)
                assign[elem] = truth
                if not formula:
                    return assign
                if [] in formula:
                    return None
                search = True
                break
    if not formula:
        return assign
    else: 
        var = formula[0][0][0]
        for truth in (True, False):
            f1 = mod_formula(formula, var, truth)
            if [] in f1:
                continue
            assignment = satisfying_assignment(f1)
            if assignment is not None: 
                assign[var] = truth
                return assign | assignment
        return None
                
    return satisfying_assignment(formula)
        
def subgrids(n):
    """
    Returns the coords in each of the the n subgrids as a list of lists of tuples

    >>> subgrids(4)
    [[(0, 0), (0, 1), (1, 0), (1, 1)], [(0, 2), (0, 3), (1, 2), (1, 3)], [(2, 0), (2, 1), (3, 0), (3, 1)], [(2, 2), (2, 3), (3, 2), (3, 3)]]
    """
    deg, subgrids = int(n**0.5), []
        
    istart = 0
    for iscale in range(1, deg+1):
        jstart, istop = 0, iscale*deg
        for jscale in range(1, deg+1):
            grid, jstop = [], jscale*deg
            for i in range(istart, istop):
                for j in range(jstart, jstop):
                    grid.append((i, j))
            subgrids.append(grid)
            jstart = jstop
        istart = istop
    
    return subgrids
    
            
def create_pairs(lst):
    """
    Returns a set of all possible pairs of values in lst

    >>> create_pairs([1, 2, 3, 4, 5])
    {(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)}
    """
    pairs = set()
    for i in range(len(lst)-1):
        for j in range(i+1, len(lst)):
            pairs.add((lst[i], lst[j]))
    return pairs
         
def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    
    """
    n, formula = len(sudoku_board), []
    
    digit_pairs = create_pairs(list(range(1, n+1)))
    for i in range(n):
        for j in range(n):
            num = sudoku_board[i][j]
            # sudoku cell != 0, add unit clause
            if num:
                formula.append([((i, j, num), True)])
            # each cell must contain atleast 1 digit
            c1 = [((i, j, d), True) for d in range(1, n+1)]
            formula.append(c1)
            # pairwise, atleast 1 digit must not be in current cell
            for p in digit_pairs:
                c2 = [((i, j, p[0]), False), ((i, j, p[1]), False)]
                formula.append(c2)
    
    
    rowcol_pairs = create_pairs(list(range(n)))
    for i in range(n):
        # each digit appears atleast 1x in every row, col
        for d in range(1, n+1):
            col = [((i, j, d), True) for j in range(n)]
            row = [((j, i, d), True) for j in range(n)]
            formula.extend([row, col])
            # pairwise, atleast 1 cell must not contain digit (by row/col)
            for p in rowcol_pairs:
                    colpairwise = [((i, p[0], d), False), ((i, p[1], d), False)]
                    rowpairwise = [((p[0], i, d), False), ((p[1], i, d), False)]
                    formula.extend([rowpairwise, colpairwise])
    
    
    subgrid_coords = subgrids(n)
    for g in subgrid_coords:
        subgrid_pairs = create_pairs(g)
        # each digit appears atleast 1x in the subgrid
        for d in range(1, n+1):
            c1 = [((c[0], c[1], d), True) for c in g]
            formula.append(c1)
            # pairwise, atleast 1 loc in subgrid must not contain digit
            for p in subgrid_pairs:
                subgridpairwise = [((p[0][0], p[0][1], d), False), ((p[1][0], p[1][1], d), False)]
                formula.append(subgridpairwise)
            
    return formula

                
def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolveable board, return None
    instead.
    
    >>> assignments_to_sudoku_board({(0, 0, 1): True}, 2) is None
    True
    
    >>> assignments_to_sudoku_board({(0, 0, 1): True, (0, 1, 1): False, (0, 1, 2): True,
    ...         (1, 0, 1): False, (1, 0, 2): True, (1, 1, 1): True}, 2)
    [[1, 2], [2, 1]]
    """
    if assignments:
        board = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for d in range(1, n+1):
                    if (i, j, d) in assignments and assignments[(i, j, d)]:
                        board[i][j] = d
            if board[i][j] == 0:
                return None
        return board
    return None


if __name__ == "__main__":

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)
    
    # doctest.run_docstring_examples(
    #     mod_formula,
    #     globals(),
    #     optionflags=_doctest_flags,
    #     verbose=True
    # )
    
    # doctest.run_docstring_examples(
    #     sudoku_board_to_sat_formula,
    #     globals(),
    #     optionflags=_doctest_flags,
    #     verbose=True
    # )
    
    # doctest.run_docstring_examples(
    #     satisfying_assignment,
    #     globals(),
    #     optionflags=_doctest_flags,
    #     verbose=True
    # )
    
    # doctest.run_docstring_examples(
    #     assignments_to_sudoku_board,
    #     globals(),
    #     optionflags=_doctest_flags,
    #     verbose=True
    # )
    
    # doctest.run_docstring_examples(
    #     subgrids,
    #     globals(),
    #     optionflags=_doctest_flags,
    #     verbose=True
    # )
    
    # doctest.run_docstring_examples(
    #     create_pairs,
    #     globals(),
    #     optionflags=_doctest_flags,
    #     verbose=True
    # )
    
    # rule1 = [[('dylan', True), ('adam', True), ('rob', True),
    #       ('pete', True), ('tim', True)]]

    # rule2 = [[('dylan', False), ('adam', False)],
    #          [('dylan', False), ('rob', False)],
    #          [('dylan', False), ('pete', False)],
    #          [('dylan', False), ('tim', False)],
    #          [('adam', False), ('rob', False)],
    #          [('adam', False), ('pete', False)],
    #          [('adam', False), ('tim', False)],
    #          [('rob', False), ('pete', False)],
    #          [('rob', False), ('tim', False)],
    #          [('pete', False), ('tim', False)]]
    
    
    # rule3 = [[('chocolate', False), ('vanilla', False), ('pickles', False)],
    #          [('chocolate', True), ('vanilla', True)],
    #          [('chocolate', True), ('pickles', True)],
    #          [('vanilla', True), ('pickles', True)]]
    
    # rule4 = [[('dylan', False), ('pickles', True)],
    #          [('dylan', False), ('chocolate', False)],
    #          [('dylan', False), ('vanilla', False)]]
    
    # rule5 = [[('rob', False), ('pete', True)],
    #          [('pete', False), ('rob', True)]]
    
    # rule6 = [[('adam', False), ('chocolate', True)],
    #          [('adam', False), ('vanilla', True)],
    #          [('adam', False), ('pickles', True)]]
    
    # rules = rule1 + rule2 + rule3 + rule4 + rule5 + rule6
    # print(satisfying_assignment(rules))

    # CNF = [
    # [('a', True), ('b', True), ('c', True)],
    # [('a', False), ('f', True)],
    # [('d', False), ('e', True), ('a', True), ('g', True)],
    # [('h', False), ('c', True), ('a', False), ('f', True)],
    # ]
    # print(satisfying_assignment(CNF))
    # cnf = [[('a', True), ('a', False)], 
    #        [('b', True), ('a', True)], 
    #        [('b', True)], 
    #        [('b', False), ('b', False), ('a', False)], 
    #        [('c', True), ('d', True)], 
    #        [('c', True), ('d', True)]]
    # print(satisfying_assignment(cnf))
    
    small = [
    [1, 0, 0, 4],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [3, 0, 1, 2]
    ]

    
    # sudoku_formula = sudoku_board_to_sat_formula(small)
    # print(sudoku_formula)
    # solution = satisfying_assignment(sudoku_formula)
    # print(f'{solution=}')
     
    # solved_sudoku = assignments_to_sudoku_board(solution, 4)
    # print(solved_sudoku)
    
    # [[1, 2, 4, 3], 
    # [2, 1, 3, 4], 
    # [3, 4, 2, 1], 
    # [4, 3, 1, 2]]
    
    med = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    # sudoku_formula = sudoku_board_to_sat_formula(med)
    # solution = satisfying_assignment(sudoku_formula)
    # print(f'{solution=}')
     
    # solved_sudoku = assignments_to_sudoku_board(solution, 9)
    # print(solved_sudoku)
    
    [[5, 3, 1, 2, 7, 6, 4, 9, 8], 
    [6, 2, 3, 1, 9, 5, 8, 4, 7], 
    [1, 9, 8, 3, 4, 7, 5, 6, 2], 
    [8, 1, 2, 7, 6, 4, 9, 5, 3], 
    [4, 7, 9, 8, 5, 3, 6, 2, 1], 
    [7, 4, 5, 9, 2, 8, 3, 1, 6], 
    [9, 6, 7, 5, 3, 1, 2, 8, 4], 
    [2, 8, 6, 4, 1, 9, 7, 3, 5], 
    [3, 5, 4, 6, 8, 2, 1, 7, 9]]
    
    # med = [
    # [5, 1, 7, 6, 0, 0, 0, 3, 4],
    # [2, 8, 9, 0, 0, 4, 0, 0, 0],
    # [3, 4, 6, 2, 0, 5, 0, 9, 0],
    # [6, 0, 2, 0, 0, 0, 0, 1, 0],
    # [0, 3, 8, 0, 0, 6, 0, 4, 7],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 9, 0, 0, 0, 0, 0, 7, 8],
    # [7, 0, 3, 4, 0, 0, 5, 6, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # ]
    # sudoku_formula = sudoku_board_to_sat_formula(med)
    # solution = satisfying_assignment(sudoku_formula)
    # print(f'{solution=}')
     
    # solved_sudoku = assignments_to_sudoku_board(solution, 9)
    # print(solved_sudoku)
    
    [[5, 1, 7, 6, 2, 9, 8, 3, 4], 
     [2, 8, 9, 1, 7, 4, 6, 5, 3], 
     [3, 4, 6, 2, 8, 5, 7, 9, 1], 
     [6, 7, 2, 8, 9, 3, 4, 1, 5], 
     [1, 3, 8, 9, 5, 6, 2, 4, 7], 
     [9, 6, 5, 3, 4, 7, 1, 8, 2], 
     [4, 9, 1, 5, 6, 2, 3, 7, 8], 
     [7, 2, 3, 4, 1, 8, 5, 6, 9], 
     [8, 5, 4, 7, 3, 1, 9, 2, 6]]
   
    # print(subgrid_helper(4))
    
    
