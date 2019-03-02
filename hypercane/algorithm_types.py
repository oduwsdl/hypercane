
from .algorithms.random import RandomAlgorithm

supported_algorithms = {
    # "dsa1": DSA1Algorithm,
    # "first20": First20Algorithm,
    "random20": Random20Algorithm
}

def get_algorithm(algorithm_name, collection_model):

    return supported_algorithms[algorithm_name](collection_model)
