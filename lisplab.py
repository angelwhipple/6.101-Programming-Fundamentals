#!/usr/bin/env python3

import sys
import doctest

sys.setrecursionlimit(10_000)


#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    >>> number_or_symbol('cat')
    'cat'
    >>> number_or_symbol('(')
    '('
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x

def get_chars(string):
    yield from string


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    >>> tokenize('(cat (dog (tomato)))')
    ['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']
    
    """
    out, onlychars, lines = [], [], source.splitlines()
    # omit comments prefixed w/ semicolon by line
    for line in lines:
        colon = line.find(';')
        if colon != -1:
            # include subset of line up to semicolon
            substr = line[:colon]
            onlychars.extend(substr.split())
        # no comment found, split line by whitespace
        else:
            onlychars.extend(line.split())
            
    for elem in onlychars:
        token = ''
        for char in get_chars(elem):
            # append single parentheses as individual tokens
            if char in '()':
                # if ( or ) encountered while building a token, append + reset token
                if token:
                    out.append(token)
                    token = ''
                out.append(char)
            # anything else, extend token with char
            else:
                token += char
        # reach end of elem and token not empty str, append token
        if token:
            out.append(token)
    return out


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
        
    >>> parse(['2'])
    2
    >>> parse(['x'])
    'x'
    >>> parse(['cat'])
    'cat'
    >>> parse(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')'])
    ['cat', ['dog', ['tomato']]]
    >>> parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')'])
    ['+', 2, ['-', 5, 3], 7, 8]
    >>> parse(['(', 'define', 'circle-area', '(', 'lambda', '(', 'r', ')', '(', '*', '3.14', '(', '*', 'r', 'r', ')', ')', ')', ')'])
    ['define', 'circle-area', ['lambda', ['r'], ['*', 3.14, ['*', 'r', 'r']]]]
    """
    def parse_expression(index):
        token = number_or_symbol(tokens[index])
        # base: token is a num, variable, or symbol
        if not token == '(':
            return token, index+1
        # bad token
        elif ' ' in token or '\n' in token or ';' in token:
            raise SchemeSyntaxError
        else:
            subexpression = []
            # check next token for closing parentheses
            while tokens[index+1] != ')':
                token, index = parse_expression(index+1)
                subexpression.append(token)
                # decrement index to avoid skipping potential )
                index -= 1
            # increment index by 2 for position of 1 beyond matching )
            return subexpression, index+2
    
    # check for incorrect expressions before parsing
    if '(' and ')' in tokens:
        if tokens.count('(') != tokens.count(')') or tokens.index(')') < tokens.index('('):
            raise SchemeSyntaxError
    if ('(' in tokens and ')' not in tokens) or (')' in tokens and '(' not in tokens):
        raise SchemeSyntaxError
    # REVISE: keywords in expression that are not enclosed by parentheses
    if ('(' not in tokens) and ('define' in tokens or 'lambda' in tokens):
        raise SchemeSyntaxError
        
    parsed, next_index = parse_expression(0)
    return parsed
        
        


######################
# Built-in Functions #
######################
    
booleans = ['#t', '#f']

def is_list(obj):
    # check for empty list or cons cell
    if obj[0] == []:
        return booleans[0]
    elif not isinstance(obj[0], Pair):
        return booleans[1]
    else:
        cdr = scheme_builtins['cdr'](obj)
        return is_list([cdr])

def length(dalist):
    if dalist[0] == []:
        return 0
    elif not isinstance(dalist[0], Pair):
        raise SchemeEvaluationError 
    else:
        cdr = scheme_builtins['cdr'](dalist)
        return 1 + length([cdr])

def list_ref(arg):
    if not arg or len(arg) > 2:
        raise SchemeEvaluationError
    dalist, ind = arg[0], arg[1]
    # not a cons cell OR empty list, cannot index
    if not isinstance(dalist, Pair) or dalist == []:
        raise SchemeEvaluationError
    if ind == 0:
        return scheme_builtins['car']([dalist])
    # recurse on cdr, decrement index
    return list_ref([scheme_builtins['cdr']([dalist]), ind-1])
        
def append(lists):
    concat = ['list']
    if not lists:
        pass
    elif not all(is_list([dalist]) == booleans[0] for dalist in lists):
        raise SchemeEvaluationError
    else:
        for dalist in lists:
            stop = length([dalist])
            for i in range(stop):
                val = list_ref([dalist, i])
                if isinstance(val, Pair):
                    val = val.astokens()
                concat += [val]
    return evaluate(concat)
            
scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': lambda args: 1 if not args else args[0]*scheme_builtins['*'](args[1:]),
    '/': lambda args: (i for i in args).throw(SchemeEvaluationError) if not args else \
        (1/args[0] if len(args) == 1 else args[0]*scheme_builtins['*']([scheme_builtins['/']([arg]) for arg in args[1:]])),
    'equal?': lambda args: booleans[0] if all(args[i] == args[i+1] for i in range(len(args)-1)) else booleans[1],
    '>': lambda args: booleans[0] if all(args[i] > args[i+1] for i in range(len(args)-1)) else booleans[1],
    '>=': lambda args: booleans[0] if all(args[i] >= args[i+1] for i in range(len(args)-1)) else booleans[1],
    '<': lambda args: booleans[0] if all(args[i] < args[i+1] for i in range(len(args)-1)) else booleans[1],
    '<=': lambda args: booleans[0] if all(args[i] <= args[i+1] for i in range(len(args)-1)) else booleans[1],
    'not': lambda arg: (i for i in arg).throw(SchemeEvaluationError) if not arg or len(arg) > 1 else \
        (booleans[0] if arg[0] == booleans[1] else booleans[1]),
    '#t': '#t',
    '#f': '#f',
    'car': lambda arg: (i for i in arg).throw(SchemeEvaluationError) if not arg or len(arg) > 1 or not isinstance(arg[0], Pair) \
        else arg[0].car,
    'cdr': lambda arg: (i for i in arg).throw(SchemeEvaluationError) if not arg or len(arg) > 1 or not isinstance(arg[0], Pair) \
        else arg[0].cdr,
    'nil': [],
    'list?': is_list,
    'length': length,
    'list-ref': list_ref,
    'append': append,
    'begin': lambda args: args[-1]
}


##############
# Evaluation #
##############

class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
    
    def __repr__(self):
        return f'(cons {self.car}, {self.cdr})'
    
    def astokens(self):
        car, cdr = self.car, self.cdr
        if isinstance(self.car, Pair):
            car = self.car.astokens()
        if isinstance(self.cdr, Pair):
            cdr = self.cdr.astokens()
        if cdr == []:
            cdr = 'nil'
        return ['cons', car, cdr]

class Function:
    def __init__(self, params, body, enc_frame):
        self.params = params
        self.body = body
        self.enc_frame = enc_frame
    

class Frame:
    def __init__(self, parent_frame=None):
        self.variables = {}
        self.parent_frame = parent_frame
        
    def define_var(self, var_name, exp):
        self.variables[var_name] = exp  
        return exp

    def search_frames(self, var_name):
        if var_name in self.variables:
            return self.variables[var_name]
        while self.parent_frame is not None:
            self = self.parent_frame
            return self.search_frames(var_name)
        raise SchemeNameError 
        
    def find_nearest(self, var_name):
        if var_name in self.variables:
            return self
        while self.parent_frame is not None:
            self = self.parent_frame
            return self.find_nearest(var_name)
        raise SchemeNameError 
        
    def delete(self, var_name):
        if var_name in self.variables:
            var = self.variables[var_name]
            del self.variables[var_name]
            return var
        raise SchemeNameError
        
builtins = Frame()
for function in scheme_builtins:
    builtins.define_var(function, scheme_builtins[function])
    
def valid_name(name):
    return name.isascii() and '(' not in name and ')' not in name and ' ' not in name


def evaluate(tree, eval_frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if not eval_frame:
        eval_frame = Frame(builtins)
    
    # base: expression is a str representing a variable name or function symbol
    if isinstance(tree, str):
        return eval_frame.search_frames(tree)
    # base: expression is a number
    elif isinstance(tree, (float, int)):
        return tree
    # recursive: expression is a list (function OR special form)
    elif isinstance(tree, list):
        if not tree:
            pass
        # variable manipulation
        elif tree[0] == 'set!':
            var, expr = tree[1], evaluate(tree[2], eval_frame)
            nearest_frame = eval_frame.find_nearest(var)
            return nearest_frame.define_var(var, expr)
        elif tree[0] == 'let':
                names = [value[0] for value in tree[1]]
                variables = [evaluate(value[1], eval_frame) for value in tree[1]]
                lilframe = Frame(eval_frame)
                for name, variable in zip(names, variables):
                    lilframe.define_var(name, variable)
                return evaluate(tree[2], lilframe)
        elif tree[0] == 'del':
            return eval_frame.delete(tree[1])
        # lists
        elif tree[0] == 'list':
            if not tree[1:]:
                return evaluate('nil', eval_frame)
            rest = [elem for elem in tree[2:]]
            return evaluate(['cons', tree[1], ['list']+rest], eval_frame)
        elif tree[0] == 'cons':
            if len(tree[1:]) == 2:
                return Pair(evaluate(tree[1], eval_frame), evaluate(tree[2], eval_frame))
        # conditionals: COND, T_EXP, F_EXP may be boolean OR evaluable
        elif tree[0] == 'if':
            if (tree[1] not in booleans and evaluate(tree[1], eval_frame) == booleans[0]) \
                or tree[1] == booleans[0]:
                return tree[2] if tree[2] in booleans else evaluate(tree[2], eval_frame)
            return tree[3] if tree[3] in booleans else evaluate(tree[3], eval_frame)
        # boolean combinators
        elif tree[0] == 'and':
            for arg in tree[1:]:
                if (arg not in booleans and evaluate(arg, eval_frame) == booleans[1]) \
                    or arg == booleans[1]:
                    return booleans[1]
            return booleans[0]
        elif tree[0] == 'or':
            for arg in tree[1:]:
                if (arg not in booleans and evaluate(arg, eval_frame) == booleans[0]) \
                    or arg == booleans[0]:
                    return booleans[0]
            return booleans[1]
        # define/lambda statements
        elif tree[0] == 'define':
            # short syntax define
            if isinstance(tree[1], list):
                return eval_frame.define_var(tree[1][0], evaluate(['lambda', tree[1][1:], tree[2]], eval_frame))
            elif valid_name(tree[1]):
                return eval_frame.define_var(tree[1], evaluate(tree[2], eval_frame))
        elif tree[0] == 'lambda':
            return Function(tree[1], tree[2], eval_frame)
        # function operations
        else:
            # get built-in/custom function, apply to rest of expr
            func = evaluate(tree[0], eval_frame)
            if isinstance(func, Function):
                inputs, params = tree[1:], func.params
                if len(inputs) == len(params):
                    inputs = [evaluate(inp, eval_frame) for inp in inputs]
                    lil_frame = Frame(func.enc_frame)
                    for inp, par in zip(inputs, params):
                        lil_frame.define_var(par, inp)
                    return evaluate(func.body, lil_frame)
            # list expr w/ nonfunction 1st element
            elif not callable(func):
                pass
            else:
                return func([evaluate(elem, eval_frame) for elem in tree[1:]])
        print(f'{tree=}')
        raise SchemeEvaluationError

def result_and_frame(tree, eval_frame=None):
    if not eval_frame:
        eval_frame = Frame(builtins)
    return evaluate(tree, eval_frame), eval_frame

def evaluate_file(filename, eval_frame=None):
    if not eval_frame:
        eval_frame = Frame(builtins)
    file = open(filename)
    expression = file.read()
    tokens = tokenize(expression)
    parsed = parse(tokens)
    return evaluate(parsed, eval_frame)

########
# REPL #
########

# updated
def repl(raise_all=False, global_frame=None):
    # global_frame = None
    while True:
        # read the input.  pressing ctrl+d exits, as does typing "EXIT" at the
        # prompt.  pressing ctrl+c moves on to the next prompt, ignoring
        # current input
        try:
            inp = input("in> ")
            if inp.strip().lower() == "exit":
                print("  bye bye!")
                return
        except EOFError:
            print()
            print("  bye bye!")
            return
        except KeyboardInterrupt:
            print()
            continue

        try:
            # tokenize and parse the input
            tokens = tokenize(inp)
            ast = parse(tokens)
            # if global_frame has not been set, we want to call
            # result_and_frame without it (which will give us our new frame).
            # if it has been set, though, we want to provide that value
            # explicitly.
            args = [ast]
            if global_frame is not None:
                args.append(global_frame)
            result, global_frame = result_and_frame(*args)
            # finally, print the result
            print("  out> ", result)
        except SchemeError as e:
            # if raise_all was given as True, then we want to raise the
            # exception so we see a full traceback.  if not, just print some
            # information about it and move on to the next step.
            #
            # regardless, all Python exceptions will be raised.
            if raise_all:
                raise
            print(f"{e.__class__.__name__}:", *e.args)
        print()


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    # doctest.testmod(verbose=True)
    # doctest.run_docstring_examples(evaluate, globals(), verbose=True)
    
    g_frame = Frame(builtins)
    for filename in sys.argv[1:]:
        evaluate_file(filename, g_frame)
    repl(global_frame=g_frame)
    # repl(raise_all=True)
    
    # test2 = ';add the numbers 2 and 3 \n (+ ; this expression \n 2 ; spans multiple \n 3  ; lines \n)'
    # print(tokenize(test2))
    # print(tokenize(test2) == ['(', '+', '2', '3', ')'])
    # print(test2.splitlines())
    
    # test3 = ';abc def ; adne '
    # print(test3.split(';'))
    # start = test3.find(';')
    # print(test3.find(';', start+1))
    # print(test3.split(';'))
    # print(test3.rpartition(';'))
    
    # circle_area = '(define circle-area \n(lambda (r) \n(* 3.14 (* r r))\n))'
    # print(tokenize(circle_area))
    
    # print(parse(['2']))
    # print(parse(['x']))
    # print(parse(['cat']))
    # print(parse(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']))
    # print(parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')']))
    # print(parse(['bare-name']))

    # evaluate(['&', 5, 8, 1])
    # print(evaluate([['define', 'x', 7], ['+', 'x', 'x'], 'x']))
    # evaluate('x')
    # print(evaluate(['define', 'x', 7]))
    # foo = evaluate(['define', 'foo', ['lambda', ['x'], ['lambda', ['y'], ['+', 'x', 'y']]]])
    # print(f'{foo.params=}, {foo.body=}')
    # print(evaluate_file('test_files/small_test1.scm'))
    
#     test = '(begin \n \
#     (define (fib n) (fib-iter n 0 1)) \n \
#     (define (fib-iter n a b) \n \
#       (if (equal? n 1) \n \
#         b \n \
#         (if (equal? n 0) \n \
#           a \n \
#           (fib-iter (- n 1) b (+ a b)) \n \
#         ) \n \
#       ) \n \
#     ) \n \
#     (define (square x) (* x x)) \n \
# )'
#     tokens = tokenize(test)
#     parse(tokens)


    
    
    

# ((define x 7) (+ x x) x)
    
# ((define somevar (+ 1 2)) (+ 7 (* somevar 2 somevar)) (define x 2) (define y x))

# ((define spam x) eggs))
  