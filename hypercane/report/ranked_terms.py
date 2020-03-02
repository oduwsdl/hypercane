import sys
import logging

module_logger = logging.getLogger('hypercane.report.ranked_terms')
   
def get_document_tokens(urim, cache_storage, ngram_length):

    from hypercane.utils import get_boilerplate_free_content
    from nltk.corpus import stopwords
    from nltk import word_tokenize, ngrams
    import string

    # TODO: stoplist based on language of the document
    stoplist = list(set(stopwords.words('english')))
    punctuation = [ i for i in string.punctuation ]
    additional_stopchars = [ '’', '‘', '“', '”', '•', '·', '—', '–', '›', '»']
    stop_numbers = [ str(i) for i in range(0, 11) ]
    allstop = stoplist + punctuation + additional_stopchars + stop_numbers

    content = get_boilerplate_free_content(urim, cache_storage=cache_storage)
    doc_tokens = word_tokenize(content.decode('utf8').lower())
    doc_tokens = [ token for token in doc_tokens if token not in allstop ]
    table = str.maketrans('', '', string.punctuation)
    doc_tokens = [ w.translate(table) for w in doc_tokens ]
    doc_tokens = [ w for w in doc_tokens if len(w) > 0 ]
    doc_ngrams = ngrams(doc_tokens, ngram_length)
    
    return list(doc_ngrams)

def generate_ranked_terms(urimlist, count, cache_storage, ngram_length=1):

    import concurrent.futures
    import nltk

    corpus_ngrams = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_document_tokens, urim, cache_storage, ngram_length): urim for urim in urimlist }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                corpus_ngrams.extend( future.result() )

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))
                sys.exit(255)

    module_logger.info("discovered {} tokens in corpus".format(len(corpus_ngrams)))

    fdist = nltk.FreqDist(corpus_ngrams)

    tf = []

    for term in fdist:
        tf.append( (fdist[term], term) )

    module_logger.info("calculated {} term frequencies".format(len(tf)))

    returned_terms = []

    if count == 0:
        for entry in sorted(tf, reverse=True):
            returned_terms.append( ( entry[1][0], entry[0], float(entry[0])/float(len(tf)) ) )
    else:
        for entry in sorted(tf, reverse=True)[0:count]:
            returned_terms.append( ( entry[1][0], entry[0], float(entry[0])/float(len(tf)) ) )

    return returned_terms
