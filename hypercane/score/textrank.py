import logging
import traceback
import hypercane.errors
import pprint
import sys

pp = pprint.PrettyPrinter(indent=4)

module_logger = logging.getLogger('hypercane.score.textrank')

# Note, the current version of gensim dropped summarization
# see docs for the code below here: https://web.archive.org/web/20200922143916/https://radimrehurek.com/gensim/summarization/summariser.html

def score_by_textrank(urimdata, cache_storage):

    from gensim.summarization.summarizer import summarize_corpus
    from gensim import corpora
    from hypercane.utils import get_web_session
    from hypercane.utils import get_boilerplate_free_content
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from collections import defaultdict
    import string

    module_logger.info("summarizing corpus of {} URI-Ms via TextRank...".format(len(urimdata.keys())))

    text_corpus = []
    urimlist = sorted(list(urimdata.keys()))
    urimlist_noerrors = []

    module_logger.info("acquiring boilerplate-free content from {} URI-Ms...".format(len(urimlist)))
    # 1. get boilerplate free content
    for urim in urimlist:
        module_logger.info("getting boilerplate-free content from URI-M: {}".format(urim))
        try:
            content = str(get_boilerplate_free_content(urim, cache_storage=cache_storage))
            print("#### {} ####".format(urim))
            print(content)
            print("####")
            text_corpus.append(content)
            urimlist_noerrors.append(urim)
        except Exception as exc:
            module_logger.exception('URI-M [{}] generated an exception: [{}]'.format(urim, repr(exc)))
            hypercane.errors.errorstore.add(urim, traceback.format_exc())

    module_logger.info("acquiring stop words for English...")
    # TODO: 2. determine the language of the content
    # 3. get a stoplist for a given language
    stop_words = stopwords.words('english')
    stop_words.extend(string.punctuation)

    module_logger.info("splitting content into words for {} documents".format(len(text_corpus)))
    # 4. split the content into words
    texts = [[word for word in word_tokenize(document) if word not in stop_words] for document in text_corpus]

    # print("texts:")
    # pp.pprint(texts)

    module_logger.info("computing term frequencies for {} texts".format(len(texts)))
    # 5. compute term frequencies
    frequency = defaultdict(int)
    for text in texts:
         for token in text:
             frequency[token] += 1

    processed_corpus = [[token for token in text if frequency[token] > 1] for text in texts]
    # print("processed corpus:")
    # pp.pprint(processed_corpus)

    module_logger.info("generating gensim Dictionary object from {} documents".format(len(processed_corpus)))
    # 6. id2word = create a gensim Dictionary object from the terms and frequencies - this produces an object that assigns IDs to words
    dictionary = corpora.Dictionary(processed_corpus)

    module_logger.info("generating gensim corpus from {} texts".format(len(texts)))
    # 7. corpus = create a gensim corpus object with doc2bow
    corpus = [dictionary.doc2bow(text) for text in texts]

    module_logger.info("generating the TextRank scores for {} texts".format(len(texts)))
    # 8. summarize the corpus
    docscores = summarize_corpus(corpus)

    for j in range(0, len(corpus)):

        docscores

    pp.pprint(docscores)
    sys.exit(255)
