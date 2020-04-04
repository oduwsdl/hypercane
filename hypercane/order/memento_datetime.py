import sys
import logging

module_logger = logging.getLogger("hypercane.order.memento_datetime")

def order_by_memento_datetime(urims, cache_storage):

    from ..utils import get_memento_http_metadata
    from datetime import datetime
    import concurrent.futures

    memento_datetime_to_urim = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=['memento-datetime']): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            try:
                urim = future_to_urim[future]
                mdt = future.result()
                mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
                memento_datetime_to_urim.append( (datetime.timestamp(mdt), urim) )
            except Exception as exc:
                module_logger.exception("Error: {}, Failed to determine memento-datetime for {}, skipping...".format(repr(exc), urim))

    memento_datetime_to_urim.sort()

    return memento_datetime_to_urim
