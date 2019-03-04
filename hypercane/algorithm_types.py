
from .algorithms.random import Random20Algorithm
from .algorithms.first20seedmementos import First20SeedMementos

supported_algorithms = {
    # "dsa1": DSA1Algorithm,
    "first20": First20SeedMementos,
    "random20": Random20Algorithm
}

full_download_required = {
    "first20": False,
    "random20": False
}

def get_algorithm(algorithm_name, collection_model):

    return supported_algorithms[algorithm_name](collection_model)
