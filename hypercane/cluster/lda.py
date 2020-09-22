import logging
import traceback
import hypercane.errors

module_logger = logging.getLogger('hypercane.cluster.lda')

def cluster_with_lda(urimdata, cache_storage, num_topics):

    from gensim.models import LdaModel
    from gensim import corpora
    from hypercane.utils import get_web_session
    from hypercane.utils import get_boilerplate_free_content
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from collections import defaultdict
    import string

    module_logger.info("learning existing cluster assignments from input of {} URI-Ms...".format(len(urimdata.keys())))
    # learn existing cluster assignments
    urim_to_cluster = {}
    clusters_to_urims = {}
    for urim in urimdata:

        try:
            clusters_to_urims.setdefault( urimdata[urim]['Cluster'], [] ).append(urim)
            urim_to_cluster[urim] = urimdata[urim]['Cluster']
        except KeyError:
            clusters_to_urims.setdefault( None, [] ).append(urim)
            urim_to_cluster[urim] = None

    text_corpus = []
    urimlist = sorted(list(urimdata.keys()))
    urimlist_noerrors = []

    module_logger.info("acquiring boilerplate-free content from {} URI-Ms...".format(len(urimlist)))
    # 1. get boilerplate free content
    for urim in urimlist:
        module_logger.info("getting boilerplate-free content from URI-M: {}".format(urim))
        try:
            text_corpus.append(
                str(get_boilerplate_free_content(urim, cache_storage=cache_storage))
            )
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

    module_logger.info("computing term frequencies for {} texts".format(len(texts)))
    # 5. compute term frequencies
    frequency = defaultdict(int)
    for text in texts:
         for token in text:
             frequency[token] += 1

    processed_corpus = [[token for token in text if frequency[token] > 1] for text in texts]

    module_logger.info("generating gensim Dictionary object from {} documents".format(len(processed_corpus)))
    # 6. id2word = create a gensim Dictionary object from the terms and frequencies - this produces an object that assigns IDs to words
    dictionary = corpora.Dictionary(processed_corpus)

    module_logger.info("generating gensim corpus from {} texts".format(len(texts)))
    # 7. corpus = create a gensim corpus object with doc2bow
    corpus = [dictionary.doc2bow(text) for text in texts]

    module_logger.info("creating the LDA model from the corpus")
    # 8. create the LDA Model
    id2word = dictionary
    lda = LdaModel(corpus, id2word=id2word, num_topics=10, chunksize=1)

    module_logger.info("acquiring the clusters from LDA model")
    # 9. acquire the clusters
    new_clusters = {}

    module_logger.info("size of corpus: {}".format(len(corpus)))
    module_logger.info("size of urimlist: {}".format(len(urimlist)))

    for j in range(0, len(corpus)):
        cluster = max([ (i[1], i[0]) for i in lda.get_document_topics( corpus[j] )])[1]
        urim = urimlist_noerrors[j]
        module_logger.info("cluster for document {} is {}".format(urim, cluster))
        new_clusters[urim] = cluster

    module_logger.info("assigning clusters to URI-Ms from input data")
    for urim in new_clusters:
        existing_cluster = urim_to_cluster[urim]
        new_cluster = new_clusters[urim]

        if existing_cluster is None:
            urimdata[urim]['Cluster'] = "{}".format(new_cluster)
        else:
            # preserve original cluster assignment
            urimdata[urim]['Cluster'] = "{}~~~{}".format(existing_cluster, new_cluster)

    return urimdata
