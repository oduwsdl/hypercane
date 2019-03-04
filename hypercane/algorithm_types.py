
from .algorithms.random import RandomNAlgorithm
from .algorithms.first20seedmementos import FirstNSeedMementos

supported_algorithms = {
    # "dsa1": DSA1Algorithm,
    "firstn": FirstNSeedMementos,
    "randomn": RandomNAlgorithm
}

full_download_required = {
    "firstn": False,
    "randomn": False
}

def get_algorithm(algorithm_name, collection_model, memento_count):

    return supported_algorithms[algorithm_name](collection_model, memento_count=memento_count)
