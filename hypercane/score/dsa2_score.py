import logging

from numpy.core.fromnumeric import size

module_logger = logging.getLogger('hypercane.score.dsa2_score')

def score_by_dsa2_score(urimdata, cache_storage, card_weight, size_weight, image_count_weight):
    """
        The DSA2 score is a very simplistic score that weights the ability of a memento
        to create a card along with the size of the content and the number of images.

        If the card_weight is high, then only those pages with all of the
        necessary metadata to produce a social card will score highly.

        If a memento cannot create a card, it still has an opportunity to score highly
        if its text size and image count are greater than that of the others in the set.
        Both of these features are designed to ensure that sufficient data exists for
        card generation. Larger texts and more images provide a summarization algorithm
        with more opportunities to select a top image and or sentence for a card.
    """

    from ..utils import get_web_session
    from .card_score import compute_simple_card_scores
    from .document_size import compute_boilerplate_free_character_size
    from .image_count import score_by_image_count
    from scipy.stats import zscore

    module_logger.info("applying weights -- card weight: {}, size weight: {}, image count weight: {}".format(
        card_weight, size_weight, image_count_weight
    ))

    session = get_web_session(cache_storage)

    module_logger.info("computing all card scores")
    card_scores = compute_simple_card_scores(urimdata, session)

    module_logger.info("computing all size scores")
    size_scores = compute_boilerplate_free_character_size(urimdata, cache_storage, unit='characters')

    module_logger.info("computing all image count scores")
    image_count_scores = score_by_image_count(urimdata, session)

    all_card_scores = []
    all_size_scores = []
    all_image_count_scores = []

    urimlist = list(urimdata.keys())

    for urim in urimlist:

        try:
            all_card_scores.append(
                card_scores[urim]['Score---Card-Score']
            )

            all_size_scores.append(
                size_scores[urim]['Score---BoilerplateFreeCharacterSize']
            )

            all_image_count_scores.append(
                image_count_scores[urim]['Score---ImageCount']
            )
        except KeyError as e:
            module_logger.exception("URI-M [{}] was missing a necessary score value, setting_score to 0...".format(urim))
            all_card_scores.append(0)
            all_size_scores.append(0)
            all_image_count_scores(0)

    # note that DSA2 scores cannot be compared because the mean and std are relative to the set of data
    std_size_scores = zscore( all_size_scores )
    std_image_scores = zscore( all_image_count_scores )

    for i in range(0, len(urimlist)):

        urim = urimlist[i]

        module_logger.info("({} * {}) + ({} * {}) + ({} * {})".format(
            card_weight, all_card_scores[i],
            size_weight, std_size_scores[i],
            image_count_weight, std_image_scores[i]
        ))

        dsa2_score = (card_weight * all_card_scores[i]) + \
            (size_weight * std_size_scores[i]) + \
            (image_count_weight * std_image_scores[i])

        module_logger.info(" = {}".format(dsa2_score))

        urimdata[urim]["Score---DSA2-Score"] = dsa2_score

    return urimdata







