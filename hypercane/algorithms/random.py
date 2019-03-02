import random

class RandomAlgorithm:
    
    def __init__(self, collection_model):

        self.collection_model = collection_model

    def execute(self):
        
        urimlist = self.collection_model.getMementoURIList()

        random_choices = []

        while(len(random_choices) < 20):

            pick = random.choice(urimlist)

            if pick not in random_choices:
                random_choices.append(pick)

        return random_choices
            



