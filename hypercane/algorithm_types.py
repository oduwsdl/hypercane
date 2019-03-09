
from .algorithms.random import RandomNAlgorithm
from .algorithms.firstseedmementos import FirstNSeedMementos, FirstNSeedMementosWithThumbnailCheck

supported_algorithms = {
    # "dsa1": DSA1Algorithm,
    "firstn": FirstNSeedMementos,
    "firstnthumbnailtest": FirstNSeedMementosWithThumbnailCheck,
    "randomn": RandomNAlgorithm
}

full_download_required = {
    "firstn": False,
    "firstnthumbnailtest": False,
    "randomn": False
}

require_mementoembed_api = [
    "firstnthumbnailtest"
]

def get_algorithm(algorithm_name, collection_model, memento_count, session, mementoembed_endpoint_api):

    if algorithm_name in require_mementoembed_api:
        return supported_algorithms[algorithm_name](
            collection_model, mementoembed_endpoint_api,
            session=session, memento_count=memento_count
        )
    else:
        return supported_algorithms[algorithm_name](
            collection_model, memento_count=memento_count
        )
