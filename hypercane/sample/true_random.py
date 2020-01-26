import random

def select_true_random(urims, sample_count):

    sampled_urims = random.choices(urims, k=int(sample_count))

    return sampled_urims
