import logging
import concurrent.futures
import re

from ..utils import match_pattern

module_logger = logging.getLogger('hypercane.hfilter.patterns')

def filter_pattern(input_urims, cache_storage, regex_pattern, include):

    filtered_urims = []

    compiled_pattern = re.compile(regex_pattern)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = {executor.submit(match_pattern, urim, cache_storage, compiled_pattern): urim for urim in input_urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                match = future.result()

                if include == True and match is not None:
                    filtered_urims.append(urim)
                elif include == False and match is None:
                    filtered_urims.append(urim)

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}]'.format(urim, exc))
                module_logger.critical("failed to perform pattern match for [{}], skipping...".format(urim))

    return filtered_urims
