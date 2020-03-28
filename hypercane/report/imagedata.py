import logging

module_logger = logging.getLogger('hypercane.report.imagedata')

def get_managed_session(cache_storage):

    import os
    from urllib.parse import urlparse
    from pymongo import MongoClient
    from requests import Session
    from requests_cache import CachedSession
    from requests_cache.backends import MongoCache
    from mementoembed.sessions import ManagedSession
    from hypercane.version import __useragent__
    # from mementoembed.version import __useragent__

    proxies = None

    http_proxy = os.getenv('HTTP_PROXY')
    https_proxy = os.getenv('HTTPS_PROXY')

    if http_proxy is not None and https_proxy is not None:
        proxies = {
            'http': http_proxy,
            'https': https_proxy
        }
       
    o = urlparse(cache_storage)
    if o.scheme == "mongodb":
        # these requests-cache internals gymnastics are necessary 
        # because it will not create a database with the desired name otherwise
        dbname = o.path.replace('/', '')
        dbconn = MongoClient(cache_storage)
        session = ManagedSession(backend='mongodb')
        session.cache = MongoCache(connection=dbconn, db_name=dbname)
        session.proxies = proxies
        session.headers.update({'User-Agent': __useragent__})
        return session
    else:
        raise RuntimeError("Caching is required for image analysis.")

def generate_image_data(urimdata, cache_storage):

    from mementoembed.imageselection import generate_images_and_scores, scores_for_image

    managed_session = get_managed_session(cache_storage)

    imagedata = {}

    module_logger.info("generating image data with MementoEmbed libraries...")

    for urim in urimdata:
        # TODO: cache this information?
        imagedata[urim] = generate_images_and_scores(urim, managed_session)

    return imagedata

def output_image_data_as_jsonl(uridata, output_filename, cache_storage):

    from mementoembed.imageselection import generate_images_and_scores, scores_for_image
    import jsonlines

    managed_session = get_managed_session(cache_storage)
    module_logger.info("generating image data with MementoEmbed libraries...")

    with jsonlines.open(output_filename, mode='w') as writer:

        for urim in uridata:
            # TODO: cache this information?
            imagedata = { "uri": urim, "imagedata": generate_images_and_scores(urim, managed_session) }

            writer.write(imagedata)

    return imagedata

def rank_images(imagedata):

    imageranking = []

    for urim in imagedata:
        module_logger.info("processing images for URI-M {}".format(urim))
        for image_urim in imagedata[urim]:

            module_logger.info("processing image at {}".format(image_urim))

            module_logger.debug("image data: {}".format(imagedata[urim][image_urim]))

            if imagedata[urim][image_urim] is None:
                module_logger.warning("no data found for image at {} -- skipping...")
                continue

            if 'colorcount' in imagedata[urim][image_urim]:

                colorcount = float(imagedata[urim][image_urim]['colorcount'])
                ratio = float(imagedata[urim][image_urim]['ratio width/height'])

                N = imagedata[urim][image_urim]['N'] 
                n = imagedata[urim][image_urim]['n'] 

                if N == 0:
                    noverN = 0
                else:
                    noverN = n / N

                module_logger.debug("report for image {}:\n  colorcount: {}\n  ratio width/height: {}\n  n/N: {}\n".format(
                    image_urim, colorcount, ratio, noverN
                ))

                too_similar = False
                for entry in imageranking:
                    if entry[0] == colorcount:
                        if entry[1] == 1 / ratio:
                            if entry[2] == noverN:
                                too_similar = True

                if too_similar is False:

                    imageranking.append(
                        ( 
                            colorcount,
                            1 / ratio,
                            noverN,
                            image_urim
                        )
                    )

    return sorted(imageranking, reverse=True)
