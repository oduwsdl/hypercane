import sys
import logging

module_logger = logging.getLogger('hypercane.report.sumgrams')

def generate_sumgrams(urimlist, cache_storage):

    import concurrent.futures
    import nltk
    from sumgram.sumgram import get_top_sumgrams
    from hypercane.utils import get_boilerplate_free_content
    from otmt import generate_raw_urim

    doc_lst = []

    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_boilerplate_free_content, urim, cache_storage): urim for urim in urimlist }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                # TODO: we're storing the result in RAM, essentially storing the whole collection there, maybe a generator would be better?
                document_text = future.result()
                doc_lst.append(
                    {
                        "id": urim,
                        "text": document_text.decode('utf8')
                    }
                )

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))
                # sys.exit(255)
    
    params = {
        "stanford_corenlp_server": False
    }

    sumgrams = get_top_sumgrams(doc_lst, params=params)

    sf = []
    returned_terms = []

    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)

    # pp.pprint(sumgrams)
    # sys.exit(255)

    for sumgram in sumgrams["top_sumgrams"]:
        sf.append( 
            ( sumgram["term_freq"], sumgram["term_rate"], sumgram["ngram"] ) 
        )

    for entry in sorted(sf, reverse=True):
        returned_terms.append(
            ( entry[2], entry[0], entry[1] )
        )

    return returned_terms
