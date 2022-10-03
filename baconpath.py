#!/usr/bin/env python3

import pickle


def transform_data(raw_data):
   # create dicts of actor id: {set of costars} and movie id: {set of actors}
   actors, movies = { }, { }
   for t in raw_data:
        # add/update every actor-costar pair to actor dict
        if t[0] in actors and t[1] in actors:
            actors[t[0]].add(t[1])
            actors[t[1]].add(t[0])
        elif t[0] in actors and t[1] not in actors:
            actors[t[0]].add(t[1])
            actors[t[1]] = {t[0]} 
        elif t[0] not in actors and t[1] in actors:
            actors[t[0]] = {t[1]}
            actors[t[1]].add(t[0])
        else:
            actors[t[0]] = {t[1]}
            actors[t[1]] = {t[0]}
        # add/update every pair of actors to movie dict
        if t[2] in movies:
            movies[t[2]].update({t[0], t[1]})
        else:
            movies[t[2]] = {t[0], t[1]}
   # return data: tuple of two dicts
   return actors, movies
    

def acted_together(transformed_data, actor_id_1, actor_id_2):
    if actor_id_1 == actor_id_2:
        return True
    else:
        # containment check for 2nd actor in 1st actor's set of costars
        if actor_id_2 in transformed_data[0][actor_id_1]:
            return True
        else:
            return False

def actors_with_bacon_number(transformed_data, n):
    assigned, bacon = {4724}, set()
    # base case
    if n == 0:
        return assigned
    else:
        # loop until bacon number = n
        for i in range(1, n+1):
            # actors w/ bacon num i = costars of actors w/ assigned bacon nums
            # that have not been assigned bacon num
            bacon = { x for p in assigned for x in transformed_data[0] if acted_together(transformed_data, x, p) \
                      and x not in assigned }
            # update visited actors w current bacon set
            assigned.update(bacon)
            # break loop if no more bacon sets can be found
            if bacon == set():
                break
        return bacon
            

# Helper function for path-finding
def get_path(queue, visited, target, transformed_data):
    while queue:
        # remove 1st path in queue
        this_path = queue.pop(0)
        # check for target id, return path
        if target in transformed_data[0][this_path[-1]]:
            this_path.append(target)
            return this_path
        else:
            # each new path = current path extended by id of each costar of last
            # actor in current path (if not visited)
            new_paths = [ this_path+[c] for c in transformed_data[0][this_path[-1]] \
                         if c not in visited ]
            queue.extend(new_paths)
            # add costars of last actor in current path to visited
            visited.update(transformed_data[0][this_path[-1]])
    # no path found
    return None
        
        
def bacon_path(transformed_data, actor_id):
    # work queue of paths, set of visited actors
    queue, visited = [[4724]], {4724}
    return get_path(queue, visited, actor_id, transformed_data)
            
        
def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    queue, visited = [[actor_id_1]], {actor_id_1}
    if actor_id_1 == actor_id_2:
        return queue[0]
    else:
        return get_path(queue, visited, actor_id_2, transformed_data)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    else:
        # path queue
        paths = []
        # add paths from actor 1 to each valid actor to queue
        for a in transformed_data[0]:
            if goal_test_function(a):
                paths.append(actor_to_actor_path(transformed_data, actor_id_1, a))
        # check for empty queue, return shortest path
        if paths:
            shortest = paths[0]
            for p in paths:
                if len(p) < len(shortest):
                    shortest = p
            return shortest
        else:
            return None
        


def actors_connecting_films(transformed_data, film1, film2):
    def goal_function(actor):
        if actor in transformed_data[1][film2]:
            return True
        else:
            return False
    if film1 == film2:
        return [transformed_data[1][film1]][0]
    else:
        actors1, paths = transformed_data[1][film1], []
        paths.extend(actor_path(transformed_data, a, goal_function) for a in actors1)
        shortest = min(paths, key=lambda x: len(x))
        return shortest
    


if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)
        # print(f'{smalldb=}')
        data = transform_data(smalldb)
    with open("resources/names.pickle", "rb") as g:
        names = pickle.load(g)
        vals = list(names.values())
        i = [i for i in names if names[i] == 2343]
        # print(i)
    with open("resources/tiny.pickle", "rb") as h:
        tiny = pickle.load(h)
        # print(f'{tiny=}')
    with open("resources/large.pickle", "rb") as z:
        large = pickle.load(z)
        # print(f'{large=}')
    with open("resources/movies.pickle", "rb") as y:
        movies = pickle.load(y)
        # print(f'{movies=}')
    db_tiny = transform_data(tiny)
    db_large = transform_data(large)
    data = transform_data(smalldb)
    
    # ids1 = [names[j] for j in names if j == 'Stephen Blackehart' or j == 'Jonathan Sanders']
    # print(acted_together(data, *ids1))
    # ids2 = [names[x] for x in names if x == 'Dominique Ducos' or x == 'Philip Bosco']
    # print(acted_together(data, *ids2))
    # all_ids, num0 = {names[x] for x in names}, {4724}
    # num1 = {i for i in all_ids if acted_together(db_tiny, 4724, i) and i not in num0}
    # num0.update(num1)
    # print(num1)
    # num2 = { i for i in all_ids for p in num1 if acted_together(db_tiny, i, p) and i not in num0 }
    # num0.update(num2)
    # print(num2)
    # num3 = { i for i in all_ids for p in num2 if acted_together(db_tiny, i, p) and i not in num0 }
    # num0.update(num3)
    # print(num3)
    # num6 = actors_with_bacon_number(db_large, 6)
    # actors = { i for i in names if names[i] in num6 }
    # print(actors)
    
    # print(bacon_path(db_tiny, 1640))
    # print(bacon_path(data, 2884))
    # print(bacon_path(db_large, 1204))
    
    # ids3 = [names[x] for x in names if x == 'Arthur Thalasso']
    # kevin_path = bacon_path(db_large, *ids3)
    # actors_1 = [ n for i in kevin_path for n in names if names[n] == i ]
    # print(actors_1)
    # ids4 = [names[x] for x in names if x == 'Robert Maximillian' or x == 'Alfre Woodard']
    # free_path = actor_to_actor_path(db_large, ids4[1], ids4[0])
    # actors_2 = [ n for i in free_path for n in names if names[n] == i ]
    # print(actors_2)
    
    # ids5 = [names[n] for n in names if n == 'Sean T. Krishnan' or n == 'Iva Ilakovac']
    # free_path_2 = actor_to_actor_path(db_large, *ids5)
    # actors_3 = [ n for i in free_path_2 for n in names if names[n] == i ]
    # print(actors_3)
    # movie_ids = [ i for a in range(len(free_path_2)) for i in db_large[1] if \
    #               a < len(free_path_2) -1 and free_path_2[a] in db_large[1][i] and \
    #                   free_path_2[a+1] in db_large[1][i] ]
    # print(movie_ids)
    # movie_names = [ m for i in movie_ids for m in movies if movies[m] == i ]
    # print(movie_names)
    
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
