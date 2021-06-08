import logging
import traceback
import hypercane.errors

module_logger = logging.getLogger('hypercane.score.text_size')

def compute_boilerplate_free_character_size(urimdata, cache_storage, unit='characters'):

    from hypercane.utils import get_boilerplate_free_content
    import concurrent.futures
    from nltk import word_tokenize, ngrams, sent_tokenize
    import string

    table = str.maketrans('', '', string.punctuation)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_boilerplate_free_content, urim, cache_storage): urim for urim in urimdata }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                content = future.result()

                if unit == 'characters':
                    urimdata[urim]["Score---BoilerplateFreeCharacterSize"] = len(content)
                elif unit == 'words':
                    tokens = word_tokenize(content.decode('utf8').lower())
                    table = str.maketrans('', '', string.punctuation)
                    tokens = [ w.translate(table) for w in tokens ]
                    tokens = [ w for w in tokens if len(w) > 0 ]
                    doc_ngrams = ngrams(tokens, 1)
                    urimdata[urim]["Score---WordSize"] = len(list(doc_ngrams))
                elif unit == 'sentences':
                    sentences = sent_tokenize(content.decode('utf8').lower())
                    urimdata[urim]["Score---SentenceSize"] = len(sentences)
                else:
                    raise NotImplementedError("Unit of type '{}' not yet supported for size calculations".format(unit))
                

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    return urimdata

def compute_character_size(urimdata, cache_storage, bytes=False):

    import concurrent.futures
    from hypercane.utils import get_web_session
    from sys import getsizeof

    session = get_web_session(cache_storage)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(session.get, urim): urim for urim in urimdata }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                response = future.result()
                if bytes == True:
                    urimdata[urim]["Score---ByteSize"] = getsizeof(response.content)
                else:
                    urimdata[urim]["Score---CharacterSize"] = len(response.content)

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())           

    return urimdata

