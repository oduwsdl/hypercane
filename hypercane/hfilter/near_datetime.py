import logging

module_logger = logging.getLogger("hypercane.hfilter.near_datetime")

def filter_by_memento_datetime(urims, cache_storage, lower_datetime, upper_datetime):

    from ..utils import get_memento_http_metadata
    from datetime import datetime
    import concurrent.futures
    import traceback
    import hypercane.errors

    filtered_urims = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=['memento-datetime']): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            try:
                urim = future_to_urim[future]
                mdt = future_to_urim.result()
                mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")

                if mdt >= lower_datetime and mdt <= upper_datetime:
                    filtered_urims.append(urim)

            except Exception as exc:
                module_logger.exception("Error: {}, Failed to determine memento-datetime for {}, skipping...".format(repr(exc), urim))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    return filtered_urims
