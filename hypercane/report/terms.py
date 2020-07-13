import sys
import logging

module_logger = logging.getLogger('hypercane.report.terms')

def get_document_tokens(urim, cache_storage, ngram_length, added_stopwords=[]):

    from hypercane.utils import get_boilerplate_free_content
    from nltk.corpus import stopwords
    from nltk import word_tokenize, ngrams
    import string

    # TODO: stoplist based on language of the document
    stoplist = list(set(stopwords.words('english')))
    stoplist.extend(added_stopwords)
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

def generate_ranked_terms(urimlist, cache_storage, ngram_length=1, added_stopwords=[]):

    import concurrent.futures
    import nltk

    corpus_ngrams = []
    document_frequency = {}

    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_document_tokens, urim, cache_storage, ngram_length, added_stopwords=added_stopwords): urim for urim in urimlist }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                # TODO: we're storing the result in RAM, essentially storing the whole collection there, maybe a generator would be better?
                document_ngrams = future.result()
                corpus_ngrams.extend( document_ngrams )

                for ngram in list(set(document_ngrams)):

                    full_ngram = " ".join(ngram)

                    document_frequency.setdefault(full_ngram, 0)
                    document_frequency[full_ngram] += 1

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))
                # sys.exit(255)

    module_logger.info("discovered {} tokens in corpus".format(len(corpus_ngrams)))

    # module_logger.info("corpus_ngrams: {}".format(corpus_ngrams))

    fdist = nltk.FreqDist(corpus_ngrams)

    tf = []

    for term in fdist:
        tf.append( (fdist[term], term) )

    module_logger.info("calculated {} term frequencies".format(len(tf)))

    returned_terms = []

    for entry in sorted(tf, reverse=True):
        full_ngram = " ".join(entry[1])
        returned_terms.append( (
            full_ngram, entry[0], float(entry[0])/float(len(tf)),
            document_frequency[full_ngram], document_frequency[full_ngram] / len(urimlist),
            entry[0] * (document_frequency[full_ngram] / len(urimlist))
        ) )

    return returned_terms
