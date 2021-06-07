from random import weibullvariate
import hypercane.errors
import logging
import traceback

module_logger = logging.getLogger('hypercane.report.http_status')

def record_http_response_data(urim, session):

    from datetime import datetime
    from requests.exceptions import ConnectionError, TooManyRedirects, \
        RequestException, RetryError, HTTPError

    outputdata = {}

    outputdata['URI-M'] = urim
    outputdata['Memento-Datetime'] = None
    outputdata['URI-R'] = None
    outputdata['URI-T'] = None
    outputdata['HTTP Status'] = None
    outputdata['Redirect'] = None
    outputdata['Redirect Target'] = None
    outputdata['Redirect Target Status'] = None

    outputdata['Datetime of check'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    try:
        response_end = session.get(urim)

        if len(response_end.history) > 0:
            response_start = response_end.history[0]
            outputdata['Redirect'] = 'Yes'
            outputdata['Redirect Target'] = response_end.url
            outputdata['Redirect Target Status']= response_end.status_code
        else:
            response_start = response_end
            outputdata['Redirect'] = 'No'

        outputdata['HTTP Status'] = response_start.status_code

        try:
            outputdata['Memento-Datetime'] = response_end.headers['memento-datetime']
        except KeyError:
            outputdata['Memento-Datetime'] = 'Not Found In Headers'

        try:
            outputdata['URI-R'] = response_end.links['original']['url']
        except KeyError:
            outputdata['URI-R'] = 'Not Found In Headers'

        try:
            outputdata['URI-T'] = response_end.links['timemap']['url']
        except KeyError:
            outputdata['URI-T'] = 'Not Found In Headers'

    except ConnectionError:
        outputdata['HTTP Status'] = 'ConnectionError'

    except TooManyRedirects:
        outputdata['HTTP Status'] = 'TooManyRedirects'

    except RequestException:
        outputdata['HTTP Status'] = 'RequestException'

    except RetryError:
        outputdata['HTTP Status'] = 'RetryError'

    except HTTPError:
        outputdata['HTTP Status'] = 'HTTPError'

    return outputdata


def output_http_status_as_tsv(urimdata, cache_storage, output_filename):

    import concurrent.futures
    from ..utils import get_web_session
    import csv

    session = get_web_session(cache_storage=cache_storage)

    fieldnames = ['URI-M', 'Datetime of check', 'Redirect', 'Redirect Target', 'HTTP Status', 'URI-R', 'URI-T', 'Memento-Datetime', 'Redirect Target Status']

    with open(output_filename, mode='w') as tsvfile:

        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, dialect='excel-tab')
        writer.writeheader()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

            future_to_urim = { executor.submit(record_http_response_data, urim, session): urim for urim in urimdata }

            for future in concurrent.futures.as_completed(future_to_urim):

                urim = future_to_urim[future]

                try:
                    status_data = future.result()
                    writer.writerow(status_data)

                except Exception as exc:
                    module_logger.exception("URI [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))
                    hypercane.errors.errorstore.add( urim, traceback.format_exc() )

    
