import sys
import logging

module_logger = logging.getLogger('hypercane.report.ranked_terms')
   
def get_document_tokens(urim, cache_storage):

    from hypercane.utils import get_boilerplate_free_content
    from nltk.corpus import stopwords
    from nltk import word_tokenize

    # TODO: stoplist based on language of the document
    stoplist = set(stopwords.words('english'))

    content = get_boilerplate_free_content(urim, cache_storage=cache_storage)
    doc_tokens = word_tokenize(content.decode('utf8').lower())
    doc_tokens = [ token for token in doc_tokens if token not in stoplist ]
    
    return doc_tokens


def generate_ranked_terms(urimlist, count, cache_storage, ngram_length=1):

    import concurrent.futures
    import nltk

    corpus_tokens = []

    # pre-generate boilerplate-free content
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_document_tokens, urim, cache_storage): urim for urim in urimlist }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                corpus_tokens.extend( future.result() )

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))
                sys.exit(255)

    ngrams = nltk.ngrams(corpus_tokens, ngram_length)
    fdist = nltk.FreqDist(ngrams)

    tf = []

    for term in fdist:
        tf.append( (fdist[term], term) )

    return sorted(tf, reverse=True)[0:count]
