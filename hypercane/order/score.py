import sys
import logging
import hypercane.errors

module_logger = logging.getLogger("hypercane.order.score")

def order_by_score(urimdata, descending, scoring_field):

    score_to_urim = []

    sorting_scores = []

    module_logger.info("sorting by field {}".format(scoring_field))

    for urim in urimdata:

        sorting_scores.append( ( float(urimdata[urim][scoring_field]), urim ) )

    if descending == True:
        score_to_urim = [ u[1] for u in sorted(sorting_scores, reverse=True) ]
    else:
        score_to_urim = [ u[1] for u in sorted(sorting_scores) ]

    return score_to_urim
