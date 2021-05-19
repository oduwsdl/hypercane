import logging

module_logger = logging.getLogger('hypercane.score.card_score')

def compute_simple_card_score(urim, session):

    from ..utils import create_html_metadata_kv_pairs

    card_score = 0

    try:

        meta_kv_pairs = create_html_metadata_kv_pairs(urim, session)

        for title_part in ['twitter:title', 'og:title']:
            if title_part in meta_kv_pairs:
                if len(meta_kv_pairs[title_part]) > 0:
                    card_score += 1
                    break

        for description_part in ['twitter:description', 'og:description', 'description']:
            if description_part in meta_kv_pairs:
                if len(meta_kv_pairs[description_part]) > 0:
                    card_score += 1
                    break

        for image_part in ['twitter:image', 'og:image', 'og:image:url', 'twitter:image:url']:
            if image_part in meta_kv_pairs:
                if len(meta_kv_pairs[image_part]) > 0:
                    card_score += 1
                    break

        card_score = card_score / 3

        return card_score

    # there are generic exceptions in Beautiful Soup's code
    except Exception as e:
        module_logger.warning("Failed to process memento at URI-M {} -- exception: {}".format(urim, repr(e)))
        return 0
        


    
