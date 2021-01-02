from random import randint

def get_stance_size(num):
    """Calculate nearest square number to a given number"""
    square = 1
    i = 1
    while square < num:
        square = i * i
        i += 1

    return i




def probability(chance):
    return randint(1, 100) <= chance