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
        "stanford_corenlp_server": False,
        "add_stopwords": "2019 read, abc news, apr 2019, april 2019, associated press, aug 2019, august 2019, com, dec 2019, december 2019, donald trump, feb 2019, february 2019, fox news, getty images, jan 2019, january 2019, jul 2019, july 2019, jun 2019, june 2019, last month, last week, last year, mar 2019, march 2019, may 2019, new york, nov 2019, november 2019, oct 2019, october 2019, pic, pm et, president donald, president donald trump, president trump, president trump’s, said statement, send whatsapp, sep 2019, september 2019, sign up, trump administration, trump said, twitter, united states, washington post, white house, york times, privacy policy, terms use, 2020 read, apr 2020, april 2020, aug 2020, august 2020, dec 2020, december 2020, feb 2020, february 2020, jan 2020, january 2020, jul 2020, july 2020, jun 2020, june 2020, mar 2020, march 2020, may 2020, nov 2020, november 2020, oct 2020, october 2020, sep 2020, september 2020"
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
