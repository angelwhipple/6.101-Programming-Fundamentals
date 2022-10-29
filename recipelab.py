# Recipes Database

import sys
import pickle

sys.setrecursionlimit(20_000)


def replace_item(recipes, old_name, new_name):
    """
    Returns a new recipes list based on the input list, where all mentions of
    the food item given by old_name are replaced with new_name.
    """
    def recursive_replace(ingredient):
        def swap(current_name):
            if current_name == old_name:
                return new_name
            return current_name
        
        if ingredient[0] == 'atomic':
            return ('atomic', swap(ingredient[1]), ingredient[2])
        elif ingredient[0] == 'compound':
            return ('compound', swap(ingredient[1]), recursive_replace(ingredient[2]))
        else:
            return [ (swap(i[0]), i[1]) for i in ingredient ] 
        
    return [ recursive_replace(ingredient) for ingredient in recipes ]

def transform_data(recipes):
    # data representation: dict of food_name: cost for atomic ingredients &
    # food_name: [ingredient lists] for compounds
    costs = { ingredient[1]: ingredient[2] for ingredient in recipes if \
             ingredient[0] == 'atomic' }
    compounds = [ ingredient for ingredient in recipes if ingredient[0] == 'compound' ]
    for ingredient in compounds:
        if ingredient[1] in costs: 
            costs[ingredient[1]].append(ingredient[2])
        else:
            costs[ingredient[1]] = [ ingredient[2] ]
    return costs

def lowest_cost(recipes, food_item, excluded=[]):
    """
    Given a recipes list and the name of a food item, return lowest cost of
    a full recipe for the given food item.
    """
    costs = transform_data(recipes)
   
    def lowest_cost(ingredient):
        # base: not in recipe/in list of excluded ingredients
        if not ingredient in costs or ingredient in excluded:
            return None
        else:
            # base: atomic ingredient
            if isinstance(costs[ingredient], (int, float)):
                return costs[ingredient]
            # recursive: sum costs across each ingredient list for that compound
            totals = []
            for variant in costs[ingredient]:
                # skip this variant if an ingredient is unavailable
                if [i[0] for i in variant if not i[0] in costs]:
                    continue
                try:
                    # try to sum across ingredient list
                    # skip if an ingredient cost returned None
                    totals.append(sum([ i[1]*lowest_cost(i[0]) for i in variant ]))
                except TypeError:
                    continue
            # if no valid cost sums for an ingredient exist, return None
            if totals:
                return min(totals)
            return None
    return lowest_cost(food_item)
   
    
# Helpers

def scale(flat_recipe, scalar):
    result = { i: flat_recipe[i]*scalar for i in flat_recipe }
    return result
    
    
def combine(flat_recipe_1, flat_recipe_2):
    result = { i: flat_recipe_1[i] for i in flat_recipe_1 }
    for i in flat_recipe_2:
        if i in result:
            result[i] += flat_recipe_2[i]
        else:
            result[i] = flat_recipe_2[i]
    return result

def compute_cost(flat_recipe, costs):
    cost = sum([ costs[i]*flat_recipe[i] for i in flat_recipe ])
    return cost
    
def create_combos(flats_list):
    flats = []
    if not flats_list:
        return []
    elif len(flats_list) == 1:
        return flats_list[0]
    else:
        list_1, list_2 = flats_list[0], create_combos(flats_list[1:])
        for elem_1 in list_1:
            for elem_2 in list_2:
                flats.append(combine(elem_1, elem_2))
    return flats

def cheapest_flat_recipe(recipes, food_item, excluded=[]):
    """
    Given a recipes list and the name of a food item, return dictionary
    (mapping atomic food items to quantities) representing a full recipe for
    the given food item.
    """
    costs = transform_data(recipes)
    
    def cheapest_flat_recipe(food_item):
        if not food_item in costs or food_item in excluded:
            return None
        else:
            # base: atomic ingredient
            if isinstance(costs[food_item], (int, float)):
                return { food_item: 1 }
            else:
                # recursive: search for a flat recipe across ingredient lists
                for variant in costs[food_item]:
                    # an ingredient is unavailable, skip
                    if [i[0] for i in variant if not i[0] in costs]:
                        continue
                    # initiate a flat recipe for this variant
                    flat_recipe = {}
                    # attempt to create/scale flat recipe for each ingredient,
                    # combine w/ initial flat recipe
                    for i in variant:
                        try:
                            scaled = scale(cheapest_flat_recipe(i[0]), i[1])
                            flat_recipe = combine(flat_recipe, scaled)
                        # an ingredient cost returned none, skip
                        except TypeError:
                            continue
                    # if flat recipe creates cheapest sum, return
                    if compute_cost(flat_recipe, costs) == lowest_cost(recipes, food_item, excluded):
                        return flat_recipe
                # no cheapest flat recipe exists among combos, return None
                return None
                   
    return cheapest_flat_recipe(food_item)


def all_flat_recipes(recipes, food_item, excluded=[]):
    """
    Given a list of recipes and the name of a food item, produce list (in any
    order) of all possible flat recipes for that category.
    """
    costs = transform_data(recipes)
    
    def all_flat_recipes(food_item):
        if not food_item in costs or food_item in excluded:
            return []
        else:
            if isinstance(costs[food_item], (int, float)):
                return [ {food_item: 1} ]
            else:
                all_flats_list = []
                for variant in costs[food_item]:
                    flat_recipes = []
                    for ingred in variant:
                        ingred_list, sub = [], all_flat_recipes(ingred[0])
                        while sub:
                            subflat = sub.pop()
                            scaled = scale(subflat, ingred[1])
                            flat = combine({}, scaled)
                            ingred_list.append(flat)
                        flat_recipes.append(ingred_list)
                    all_flats_list.extend(create_combos(flat_recipes))
                if all_flats_list:
                    return all_flats_list
                return []
    
    return all_flat_recipes(food_item)
            
                

if __name__ == "__main__":
    with open("test_recipes/examples_filter.pickle", "rb") as f:
        example_recipes = pickle.load(f)
        # print(example_recipes)

    
    smaller_recipes = [
    ('compound', 'chili', [('cheese', 2), ('protein', 3), ('tomato', 2)]),
    ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'protein', [('cow', 1)]),
    ('atomic', 'cow', 100),
    ('atomic', 'tomato', 10),
    ('atomic', 'milking stool', 5),
    ('atomic', 'time', 10000), ]
    # print(replace_item(smaller_recipes, 'milk', 'chocolate milk'))
    
    example_recipes = [
    ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    ('atomic', 'milking stool', 5),
    ('atomic', 'cutting-edge laboratory', 1000),
    ('atomic', 'time', 10000),
    ('atomic', 'cow', 100),
    ]
    # print(lowest_cost(example_recipes, 'cheese'))
    
    cookie_monsta = [
    ('compound', 'cookie sandwich', [('cookie', 2), ('ice cream scoop', 3)]),
    ('compound', 'cookie', [('chocolate chips', 3)]),
    ('compound', 'cookie', [('sugar', 10)]),
    ('atomic', 'chocolate chips', 200),
    ('atomic', 'sugar', 5),
    ('compound', 'ice cream scoop', [('vanilla ice cream', 1)]),
    ('compound', 'ice cream scoop', [('chocolate ice cream', 1)]),
    ('atomic', 'vanilla ice cream', 20),
    ('atomic', 'chocolate ice cream', 30),
    ]

    # print(lowest_cost(cookie_monsta, 'cookie sandwich'))
    
    dairy_recipes_2 = [
    ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    ('atomic', 'milking stool', 5),
    ('atomic', 'cutting-edge laboratory', 1000),
    ('atomic', 'time', 10000),
    ]
    # print(lowest_cost(dairy_recipes_2, 'cheese'))
    
    dairy_recipes_3 = [
    ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    ('atomic', 'milking stool', 5),
    ('atomic', 'cutting-edge laboratory', 1000),
    ('atomic', 'time', 10000),
    ]
    # print(cheapest_flat_recipe(example_recipes, 'cheese', ('milking stool')))
    print(all_flat_recipes(cookie_monsta, 'cookie sandwich'))
