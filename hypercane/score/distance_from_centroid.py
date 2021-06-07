import logging
import traceback

from sklearn.metrics.pairwise import _euclidean_distances_upcast
import hypercane.errors

module_logger = logging.getLogger('hypercane.score.distance_from_centroid')

def compute_distance_from_centroid(urimdata, cache_storage, more_similar=False):

    from sklearn.cluster import KMeans
    from hypercane.utils import get_boilerplate_free_content
    from sklearn.feature_extraction.text import TfidfVectorizer
    from otmt.timemap_measures import full_tokenize
    import concurrent.futures
    from sklearn.metrics.pairwise import euclidean_distances

    # 1. get number of clusters

    urim_to_cluster = {}
    clusters_to_urims = {}

    for urim in urimdata:

        try:
            clusters_to_urims.setdefault( urimdata[urim]['Cluster'], [] ).append(urim)
            urim_to_cluster[urim] = urimdata[urim]['Cluster']
        except KeyError:
            clusters_to_urims.setdefault( None, [] ).append(urim)
            urim_to_cluster[urim] = None

    urimlist_after_processing = []
    corpus = []
    
    for cluster in clusters_to_urims:

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

            future_to_urim = { executor.submit(get_boilerplate_free_content, urim, cache_storage): urim for urim in clusters_to_urims[cluster] }

            for future in concurrent.futures.as_completed(future_to_urim):

                urim = future_to_urim[future]

                try:
                    content = future.result()
                    # mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
                    corpus.append( content )
                    urimlist_after_processing.append(urim)
                except Exception as exc:
                    module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                    hypercane.errors.errorstore.add(urim, traceback.format_exc())

        module_logger.info("creating TF-IDF vectorizer from cluster corpus")

        tfidf_vectorizer = TfidfVectorizer(tokenizer=full_tokenize, stop_words=None)
        vectorized = tfidf_vectorizer.fit_transform(corpus)

        module_logger.info("computing k-means cluster centroid on corpus TF-IDF")

        km = KMeans(n_clusters=1)
        km.fit_predict(vectorized)
        centroid = km.cluster_centers_[0]
        distances = euclidean_distances( vectorized.toarray(), [ centroid ] )

        for urim in clusters_to_urims[cluster]:

            i = urimlist_after_processing.index(urim)
            distance = distances[i][0]

            if more_similar == True:
                distances = 0 - distance

            urimdata[urim]["Score---KMeans-Cluster-Centroid"] = distance

    return urimdata
