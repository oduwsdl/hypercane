import sys
import logging
import hypercane.errors
import traceback

module_logger = logging.getLogger('hypercane.report.sumgrams')

def generate_sumgrams(urimlist, cache_storage, added_stopwords=[]):

    import concurrent.futures
    import nltk
    from sumgram.sumgram import get_top_sumgrams
    from hypercane.utils import get_boilerplate_free_content
    from otmt import generate_raw_urim
    from datetime import datetime
    from string import punctuation

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
                hypercane.errors.errorstore.add( urim, traceback.format_exc() )

    now = datetime.now()
    current_year = now.year

    stopmonths = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december"
    ]

    stopmonths_short = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec"
    ]

    params = {
        "add_stopwords": ", ".join(added_stopwords),
        "top_sumgram_count": 20,
        'sentence_tokenizer': 'regex'
    }

    sumgrams = get_top_sumgrams(doc_lst, params=params)

    sf = []
    returned_terms = []

    if "top_sumgrams" in sumgrams:

        for sumgram in sumgrams["top_sumgrams"]:

            if len(sumgram["ngram"].split(' ')) > 10:
                module_logger.warning("sumgram [{}] is greater than 10 words, enacting workaround...")
                ngram = sumgram["sumgram_history"][0]["prev_ngram"]
            else:
                ngram = sumgram["ngram"]

            addsumgram = True

            # workaround for sumgram expanding dates
            for stopmonth in stopmonths:
                module_logger.info("checking if long stopmonth {} in {}".format(stopmonth, ngram))
                if stopmonth in ngram and str(current_year) in ngram:
                    module_logger.info("detected {} and {} in {}".format(stopmonth, current_year, ngram))
                    addsumgram = False
                    break

            for stopmonth in stopmonths_short:
                module_logger.info("checking if short stopmonth {} in {}".format(stopmonth, ngram))
                if stopmonth in ngram and str(current_year) in ngram:
                    module_logger.info("detected {} and {} in {}".format(stopmonth, current_year, ngram))
                    addsumgram = False
                    break

            if addsumgram == True:
                sf.append(
                    ( sumgram["term_freq"], sumgram["term_rate"], ngram )
                )

        for entry in sorted(sf, reverse=True):
            ngram = entry[2].strip(punctuation)
            returned_terms.append(
                ( ngram, entry[0], entry[1] )
            )

    return returned_terms
