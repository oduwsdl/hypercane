import logging
from rank_bm25 import BM25Okapi

module_logger = logging.getLogger('hypercane.score.bm25')

def rank_by_bm25(urimdata, session, query, cache_storage):

    import concurrent.futures
    from hypercane.utils import get_boilerplate_free_content

    # force the order
    urimlist = sorted(urimdata.keys())

    corpus = {}

    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_boilerplate_free_content, urim, cache_storage): urim for urim in urimlist }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                # TODO: we're storing the result in RAM, essentially storing the whole collection there, maybe a generator would be better?
                document_text = future.result()
                corpus[urim] = document_text.decode('utf8').split(" ")

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))
                # sys.exit(255)

    tokenized_corpus = []

    # ensure we keep things in the same order
    for urim in sorted(corpus.keys()):
        tokenized_corpus.append( corpus[urim] )

    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)

    for i in range(0, len(urimlist)):
        urim = urimlist[i]
        urimdata[urim]['Score---BM25'] = doc_scores[i]

    return urimdata

def bm25_by_entites(urimdata, session, cache_storage, k, entity_types):

    from hypercane.report.entities import generate_entities

    entity_data = generate_entities(list(urimdata.keys()), cache_storage, entity_types)

    top_entities = entity_data[0:k]
    query = " ".join([ entity[0] for entity in top_entities ])

    urimdata = rank_by_bm25(urimdata, session, query, cache_storage)

    return urimdata
