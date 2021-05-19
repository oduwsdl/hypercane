import logging
import traceback

import hypercane.errors

module_logger = logging.getLogger('hypercane.score.card_score')

def compute_simple_card_score(urim, session):

    from ..utils import create_html_metadata_kv_pairs

    card_score = 0

    try:

        meta_kv_pairs = create_html_metadata_kv_pairs(urim, session)

        for card_part in ['twitter:card']:

            if card_part in meta_kv_pairs:
                if len(meta_kv_pairs[card_part]) > 0:
                    card_score += 1
                    break

        for title_part in ['twitter:title', 'og:title']:
            if title_part in meta_kv_pairs:
                if len(meta_kv_pairs[title_part]) > 0:
                    card_score += 1
                    break

        for description_part in ['twitter:description', 'og:description']:
            if description_part in meta_kv_pairs:
                if len(meta_kv_pairs[description_part]) > 0:
                    card_score += 1
                    break

        for image_part in ['twitter:image', 'og:image', 'og:image:url', 'twitter:image:url', 'twitter:image:src']:
            if image_part in meta_kv_pairs:
                if len(meta_kv_pairs[image_part]) > 0:
                    card_score += 1
                    break

        card_score = card_score / 4

        return card_score

    # there are generic exceptions in Beautiful Soup's code
    except Exception as e:
        module_logger.warning("Failed to process memento at URI-M {} -- exception: {}".format(urim, repr(e)))
        return 0
        

def compute_simple_card_scores(urimdata, session):

    import concurrent.futures

    urims = list(urimdata.keys())
    urim_to_score = {}
    total_urims = len(urims)
    completed_urims = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(compute_simple_card_score, urim, session): urim for urim in urims}

        for future in concurrent.futures.as_completed(future_to_urim):
            completed_urims += 1
            module_logger.info("extracting score result for {}/{}".format(completed_urims, total_urims))

            try:
                urim = future_to_urim[future]
                urim_to_score[urim] = future.result()
            except Exception as exc:
                module_logger.exception("Error: {}, failed to compute score for {}, skipping...".format(repr(exc), urim))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())


    for urim in urim_to_score:
        urimdata[urim]['Rank---Card-Score'] = urim_to_score[urim]

    return urimdata
    
