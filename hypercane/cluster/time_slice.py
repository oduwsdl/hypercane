import logging
import hypercane.errors

module_logger = logging.getLogger('hypercane.cluster.time_slice')

def execute_time_slice(urimdata, cache_storage):

    import concurrent.futures
    import math
    from datetime import datetime
    from ..utils import get_memento_http_metadata
    import traceback

    mementos = []

    # extract the memento datetimes
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_http_metadata, urim, cache_storage, metadata_fields=[ "memento-datetime"]): urim for urim in urimdata.keys() }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                mdt = future.result()[0]
                mdt = datetime.strptime(mdt, "%a, %d %b %Y %H:%M:%S GMT")
                mementos.append( (mdt, urim) )
            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    # calculate the number of slices 28 + math.log(len(mementos))
    number_of_slices = math.ceil(28 + math.log(len(mementos)))

    module_logger.info("The collection will be divided into {} slices".format(number_of_slices))

    # divide the number of mementos by the number of slices to determine mementos/slice
    mementos_per_slice = math.ceil(len(mementos) / number_of_slices)

    module_logger.info("There will be {} mementos in each slice".format(mementos_per_slice))

    slices = []

    # sort mementos by memento-datetime
    # iterate through mementos, filling each slice
    current_slice = []

    module_logger.info("Slicing {} mementos into {} slices".format(len(mementos), number_of_slices))

    for memento in sorted(mementos):

        if len(current_slice) < mementos_per_slice:
            current_slice.append(memento[1])
        else:
            slices.append(current_slice)
            current_slice = []
            current_slice.append(memento[1])

    # the last slice that might be unfilled
    if len(current_slice) > 0:
        slices.append(current_slice)

    module_logger.info("We have filled {} slices".format(len(slices)))

    for i in range(0, len(slices)):

        for urim in slices[i]:

            if 'Cluster' in urimdata[urim]:
                # preserve original cluster assignment
                urimdata[urim]['Cluster'] = "{}~~~{}".format( urimdata[ urim['Cluster'] ], i )
            else:
                urimdata[urim]['Cluster'] = i

    return urimdata
