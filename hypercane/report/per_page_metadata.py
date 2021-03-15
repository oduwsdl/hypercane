import hypercane.errors
import logging
import traceback

module_logger = logging.getLogger('hypercane.report.per_page_metadata')

def output_page_metadata_as_ors(uridata, cache_storage, output_filename):

    import concurrent.futures
    import json
    from ..utils import create_html_metadata_kv_pairs, get_web_session

    session = get_web_session(cache_storage=cache_storage)

    with open(output_filename, mode='w') as writer:

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

            future_to_uri = { executor.submit(create_html_metadata_kv_pairs, uri, session): uri for uri in uridata }

            for future in concurrent.futures.as_completed(future_to_uri):

                uri = future_to_uri[future]

                try:
                    html_metadata = future.result()
                    writer.write("{}\t{}\n".format(uri, json.dumps(html_metadata)))

                except Exception as exc:
                    module_logger.exception("URI [{}] generated an exception [{}], skipping...".format(uri, repr(exc)))
                    hypercane.errors.errorstore.add( uri, traceback.format_exc() )

