import logging
import concurrent.futures

from ..utils import get_language

module_logger = logging.getLogger('hypercane.hfilter.languages')

def language_included(language, desired_languages):

    if language in desired_languages:
        return True

    return False

def language_not_included(language, desired_languages):

    if language not in desired_languages:
        return True

    return False

def filter_languages(input_urims, cache_storage, desired_languages, comparison_function):

    filtered_urims = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = {executor.submit(get_language, urim, cache_storage): urim for urim in input_urims }

        for future in concurrent.futures.as_completed(future_to_urim):
            urim = future_to_urim[future]

            try:
                language = future.result()
                if comparison_function(language, desired_languages):
                    filtered_urims.append(urim)
            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}]'.format(urim, exc))
                module_logger.critical("failed to detect language for [{}], skipping...".format(urim))

    return filtered_urims

