import logging
import multiprocessing
from aiu import convert_LinkTimeMap_to_dict, get_uri_responses
from requests_futures.sessions import FuturesSession
from requests.exceptions import ConnectionError, TooManyRedirects
from statistics import mode, StatisticsError
from fractions import Fraction

module_logger = logging.getLogger('hypercane.report.growth')

cpu_count = multiprocessing.cpu_count()

def convert_mementos_list_into_mdts_pct_urim_pct_and_urir_pct(mementos, enddate=None):

    logger = logging.getLogger(__name__)

    mdts = []
    urims = []
    urirs = []

    mdts_pct = []
    urims_pct = []
    urirs_pct = []

    urimcount = 0
    urircount = 0

    urimtotal = 0
    urirtotal = 0

    logger.info("counting URI-Ms and URI-Rs")

    for memento in mementos:

        mdt = memento[0]
        urim = memento[1]
        urir = memento[2]

        if enddate:

            if mdt < enddate:

                mdts.append(mdt)

                if urim not in urims:
                    urimtotal += 1
                    urims.append(urim)

                if urir not in urirs:
                    urirtotal += 1
                    urirs.append(urir)

        else:

            mdts.append(mdt)

            if urim not in urims:
                urimtotal += 1
                urims.append(urim)

            if urir not in urirs:
                urirtotal += 1
                urirs.append(urir)

    logger.info("There are {} URI-Rs total".format(urirtotal))
    logger.info("There are {} URI-Ms total".format(urimtotal))

    firstmdt = min(mdts)

    logger.info("first memento-datetime: {}".format(firstmdt))

    logger.info("Calculating end date, taking specified enddate of {} "
        "into consideration".format(enddate))

    if enddate:
        lastmdt = enddate
    else:
        lastmdt = max(mdts)

    logger.info("last memento-datetime: {}".format(lastmdt))

    total_seconds = (lastmdt - firstmdt).total_seconds()

    logger.info("Total seconds is {}".format(total_seconds))

    if total_seconds == 0:

        if firstmdt == lastmdt:

            urimlen = len(urims)

            mdts = []
            urims = []
            urirs = []

            for i in range(0, urimlen):
                mdts_pct.append(1.0)
                urims_pct.append(1.0)
                urirs_pct.append(1.0)

            logger.warn("only 1 memento-datetime in collection, total seconds is 0")
            logger.warn("creating a list of {} mementos at 100%".format(urimlen))

        else:
            raise Exception("something strange happened")

    else:
        mdts = []
        urims = []
        urirs = []

        for memento in mementos:

            mdt = memento[0]
            urim = memento[1]
            urir = memento[2]

            if mdt < lastmdt:

                mdts_pct.append( (mdt - firstmdt).total_seconds() / total_seconds )

                # if the urim has not been seen yet, then it is new, so increment
                if urim not in urims:
                    urimcount += 1
                    urims.append(urim)

                urims_pct.append(urimcount / urimtotal)

                # if the urir has not been seen yet, then it is new, so increment
                if urir not in urirs:
                    urircount += 1
                    urirs.append(urir)

                urirs_pct.append(urircount / urirtotal)

            else:
                break

    logger.info("max datetime percentages: {}".format(max(mdts_pct)))

    # when enddate is set, we may reach the maximum % of URI-Rs
    # and URI-Ms before we get to the maximum % of time
    if max(mdts_pct) < 1.0:
        logger.info("adding an additional data point of 1.0 to all percentages")
        mdts_pct.append(1.0)
        urirs_pct.append(1.0)
        urims_pct.append(1.0)

    logger.info("memento records: {}".format(len(mementos)))
    logger.info("# MDT records: {}".format(len(mdts_pct)))
    logger.info("# URI-R records: {}".format(len(urirs_pct)))
    logger.info("# URI-M records: {}".format(len(urims_pct)))

    return mdts_pct, urims_pct, urirs_pct

def list_generator(input_list):
    """This function generates the next item in a list. It is useful for lists
    that have their items deleted while one is iterating through them.
    """

    module_logger.debug("list generator called")

    while len(input_list) > 0:
        for item in input_list:
            module_logger.debug("list now has {} items".format(len(input_list)))
            module_logger.debug("yielding {}".format(item))
            yield item

def calculate_number_of_mementos(timemap_data):

    totalcount = 0

    for urit in timemap_data:

        try:
            totalcount += len(timemap_data[urit]['mementos']['list'])
        except KeyError:
            module_logger.exception("cannot incorporate mementos into total count from URI-T {}".format(urit))

    return totalcount

def calculate_memento_seed_ratio(timemap_data):

    memcount = calculate_number_of_mementos(timemap_data)
    seedcount = len(timemap_data)

    memcount = Fraction(memcount, seedcount).numerator
    seedcount = Fraction(memcount, seedcount).denominator

    return "{}:{}".format(memcount, seedcount)

def calculate_mementos_per_seed(timemap_data):

    memcount = calculate_number_of_mementos(timemap_data)
    seedcount = len(timemap_data)

    return memcount / seedcount

def get_datetimes_list(timemap_data):

    datetimes = []

    for urit in timemap_data:

        tm = timemap_data[urit]

        try:

            for mem in tm['mementos']['list']:

                datetimes.append( mem['datetime'] )

        except KeyError:
            module_logger.exception("cannot acquire datetimes from URI-T: {}".format(urit))

    return datetimes

def parse_data_for_mementos_list(timemap_data):

    mementos = []

    for urit in timemap_data:

        if "original_uri" in timemap_data[urit]:

            urir = timemap_data[urit]["original_uri"]

            for memento in timemap_data[urit]["mementos"]["list"]:

                urim = memento["uri"]
                mdt = memento["datetime"]

                mementos.append( (mdt, urim, urir) )

    mementos.sort()

    return mementos

def get_first_memento_datetime(timemap_data):

    datetimes = get_datetimes_list(timemap_data)

    return min(datetimes)

def get_last_memento_datetime(timemap_data):

    datetimes = get_datetimes_list(timemap_data)

    return max(datetimes)

def process_timemaps_for_mementos(urit_list, session):

    timemap_data = {}
    errors_data = {}

    with FuturesSession(max_workers=cpu_count, session=session) as session:
        futures = get_uri_responses(session, urit_list)

    working_uri_list = list(futures.keys())

    for urit in list_generator(working_uri_list):

        module_logger.debug("checking if URI-T {} is done downloading".format(urit))

        if futures[urit].done():

            module_logger.debug("URI-T {} is done, extracting content".format(urit))

            try:
                response = futures[urit].result()

                http_status = response.status_code

                if http_status == 200:

                    timemap_content = response.text

                    module_logger.info("adding TimeMap content for URI-T {}".format(
                        urit))

                    timemap_data[urit] = convert_LinkTimeMap_to_dict(
                        timemap_content, skipErrors=True)

                else:

                    errors_data[urit] = {
                        "type": "http_error",
                        "data": response
                    }

                working_uri_list.remove(urit)

            except ConnectionError as e:

                module_logger.warning("There was a connection error while attempting "
                    "to download URI-T {}".format(urit))

                errors_data[urit] = {
                    "type": "exception",
                    "data": e
                }

                working_uri_list.remove(urit)

            except TooManyRedirects as e:

                module_logger.warning("There were too many redirects while attempting "
                    "to download URI-T {}".format(urit))

                errors_data[urit] = {
                    "type": "exception",
                    "data": e
                }

                working_uri_list.remove(urit)

    return timemap_data, errors_data

def draw_both_axes_pct_growth(
        mdts_pct, urims_pct, urirs_pct, outputfile,
        shape_percentage_of_whole=None,
        whole_text_x=None, whole_text_y=None, shape_name=None,
        enddate=None
    ):

    import numpy
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    fig, ax = plt.subplots(1)
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    fig.set_figheight(10)
    fig.set_figwidth(10)

    labels = []
    label = ax.plot(mdts_pct, urims_pct, label="% mementos", color="#ff0000", linewidth=3.0)
    labels.append(label)

    labels = []
    label = ax.plot(mdts_pct, urirs_pct, label="% original resources", color="#00ff00", linewidth=3.0)
    labels.append(label)

    if shape_percentage_of_whole:
        assert whole_text_x
        assert whole_text_y
        fmt_pct = "{0:.2f}%".format(shape_percentage_of_whole * 100)
        ax.text(whole_text_x, whole_text_y, "{}\nof collections\nhave the behavior\n{}".format(
                fmt_pct, shape_name),
               fontsize=32, color="#777777")

    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()

    if enddate:
        plt.xlabel("Time Percentage from Start of Collection to {}".format(enddate))
    else:
        plt.xlabel("Time Percentage of Life of Collection", fontsize=20)

    plt.ylabel("URI Percentage", fontsize=18)

    ax.set_ylim(-.05, 1.05)
    ax.set_xlim(-.05, 1.05)

    ax.set_xticks(numpy.arange(0, 1.05, 0.1))
    ax.set_yticks(numpy.arange(0, 1.05, 0.1))

    # thanks https://stackoverflow.com/questions/31357611/format-y-axis-as-percent
    xvals = ax.get_xticks()
    ax.set_xticklabels(['{:3.0f}%'.format(x*100) for x in xvals])

    yvals = ax.get_yticks()
    ax.set_yticklabels(['{:3.0f}%'.format(y*100) for y in yvals])

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(16)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(16)

    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc="upper left", fontsize=20)

    plt.savefig(outputfile)
