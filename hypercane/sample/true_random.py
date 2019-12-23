import random

from ..discover import list_seed_mementos

def select_true_random(cid, session, sample_count):

    urims = list_seed_mementos(cid, session)
    sampled_urims = random.choices(urims, k=int(sample_count))

    return sampled_urims
