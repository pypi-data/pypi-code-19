print('hello dera python is a great language for u')

def print_movie(the_list):
    for a_movie in the_list:
        if isinstance(a_movie, list):
            print_movie(a_movie)
        else:
            print(a_movie)
