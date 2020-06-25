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
    last_year = current_year - 1
    current_date = now.day

    # sumgram processes stop words at two levels:
    # 1. when the vocabulary is built
    # 2. stopwords are applied when finding sumgrams
    # start with single terms before moving on to bigrams, etc.

    # TODO: load these from a file
    # added_stopwords = [
    #     "associated press",
    #     "com",
    #     "donald trump",
    #     "fox news",
    #     "abc news",
    #     "getty images",
    #     "last month",
    #     "last week",
    #     "last year",
    #     "pic",
    #     "pinterest reddit",
    #     "pm et",
    #     "president donald",
    #     "president donald trump",
    #     "president trump",
    #     "president trump's",
    #     "print mail",
    #     "reddit print",
    #     "said statement",
    #     "send whatsapp",
    #     "sign up",
    #     "trump administration",
    #     "trump said",
    #     "twitter",
    #     "united states",
    #     "washington post",
    #     "white house",
    #     "whatsapp pinterest",
    #     "subscribe whatsapp",
    #     "york times",
    #     "privacy policy",
    #     "terms use"
    # ]

    # added_stopwords.append( "{} read".format(last_year) )
    # added_stopwords.append( "{} read".format(current_year) )

    # stopmonths = [
    #     "january",
    #     "february",
    #     "march",
    #     "april",
    #     "may",
    #     "june",
    #     "july",
    #     "august",
    #     "september",
    #     "october",
    #     "november",
    #     "december"
    # ]

    # # add just the month to the stop words
    # added_stopwords.extend(stopmonths)

    # stopmonths_short = [
    #     "jan",
    #     "feb",
    #     "mar",
    #     "apr",
    #     "may",
    #     "jun",
    #     "jul",
    #     "aug",
    #     "sep",
    #     "oct",
    #     "nov",
    #     "dec"
    # ]

    # added_stopwords.extend(stopmonths_short)

    # # add the day of the week, too
    # added_stopwords.extend([
    #     "monday",
    #     "tuesday",
    #     "wednesday",
    #     "thursday",
    #     "friday",
    #     "saturday",
    #     "sunday"
    # ])

    # added_stopwords.extend([
    #     "mon",
    #     "tue",
    #     "wed",
    #     "thu",
    #     "fri",
    #     "sat",
    #     "sun"
    # ])

    # # for i in range(1, 13):
    # #     added_stopwords.append(
    # #         datetime(current_year, i, current_date).strftime('%b %Y')
    # #     )
    # #     added_stopwords.append(
    # #         datetime(last_year, i, current_date).strftime('%b %Y')
    # #     )

    # # for i in range(1, 13):
    # #     added_stopwords.append(
    # #         datetime(current_year, i, current_date).strftime('%B %Y')
    # #     )
    # #     added_stopwords.append(
    # #         datetime(last_year, i, current_date).strftime('%B %Y')
    # #     )

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
