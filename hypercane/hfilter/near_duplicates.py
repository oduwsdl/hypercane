import logging
import traceback
import concurrent.futures
from datetime import datetime
import hypercane.errors

module_logger = logging.getLogger('hypercane.hfilter.near_duplicates')

def filter_near_duplicates(urims, cache_storage):

    from simhash import Simhash
    from ..utils import get_memento_http_metadata, get_tf_simhash

    module_logger.info("discovered {} mementos in input, downloading or extracting from cache...".format(len(urims)))

    urim_to_simhash = {}
    simhashes_completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        # TODO: allow user to choose tf-simhash rather than raw simhash
        future_to_urim = { executor.submit(get_tf_simhash, urim, cache_storage): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):
            urim = future_to_urim[future]

            try:
                simhash = future.result()
                module_logger.info("associating Simhash {} with URI-M {}".format(simhash, urim))
                urim_to_simhash[urim] = simhash
                simhashes_completed += 1
                module_logger.info("completed {}/{} simhashes, {} left".format(
                    simhashes_completed, len(urims), len(urims) - simhashes_completed))

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, repr(exc)))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    comparison_structure = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=["memento-datetime", "timemap"]): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):
            urim = future_to_urim[future]

            try:
                memento_datetime, urit = future.result()

                comparison_structure.setdefault(urit, []).append(
                    (
                        memento_datetime, # datetime.strptime(memento_datetime, "%a, %d %b %Y %H:%M:%S GMT"),
                        int(urim_to_simhash[urim]),
                        urim
                    )
                )

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    output_urims = []

    for urit in comparison_structure.keys():

        last_simhash = 0

        for entry in sorted(comparison_structure[urit]):
            simhash = entry[1]
            urim = entry[2]
            distance = Simhash(simhash).distance(Simhash(last_simhash))/64.0

            # if the Simhash is great enough, then we have enough of
            # a change that we are dealing with a non-near duplicate
            # TODO: allow user to set raw simhash threshold
            if distance > 0.2:
                last_simhash = simhash
                output_urims.append(urim)

    module_logger.debug("returning: {}".format(output_urims))

    return output_urims
