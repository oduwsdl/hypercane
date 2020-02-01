import sys

class OrderByDSA1PublicationAlgorithmError(Exception):
    pass

def order_by_dsa1_publication_alg(urims, cache_storage):

    from ..utils import get_newspaper_publication_date
    from datetime import datetime
    import concurrent.futures

    publication_datetime_to_urim = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_newspaper_publication_date, urim, cache_storage): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            try:
                urim = future_to_urim[future]
                pdt = future.result()
                pdt = datetime.strptime(pdt, "%a, %d %b %Y %H:%M:%S GMT")
                publication_datetime_to_urim.append( (datetime.timestamp(pdt), urim) )
            except Exception as exc:
                raise OrderByDSA1PublicationAlgorithmError("Failed to determine publication date for {} -- Details: {}".format(urim, repr(exc)))

    publication_datetime_to_urim.sort()

    return publication_datetime_to_urim