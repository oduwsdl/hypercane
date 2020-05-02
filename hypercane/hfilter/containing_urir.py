import logging

module_logger = logging.getLogger("hypercane.hfilter.near_datetime")

def filter_by_urir(urims, cache_storage, urir_pattern):

    from ..utils import get_memento_http_metadata
    from datetime import datetime
    import concurrent.futures
    import re

    filtered_urims = []

    compiled_pattern = re.compile(urir_pattern)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=['original']): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            try:
                urim = future_to_urim[future]
                urir = future_to_urim.result()

                if compiled_pattern.match(urir) is not None:
                    filtered_urims.append(urim)

            except Exception as exc:
                module_logger.exception("Error: {}, Failed to determine memento-datetime for {}, skipping...".format(repr(exc), urim))

    return filtered_urims
