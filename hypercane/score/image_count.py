import logging
import requests.exceptions
from bs4 import BeautifulSoup

module_logger = logging.getLogger('hypercane.score.image_count')

def get_image_count(urim, session):

    from hypercane.utils import generate_raw_urim

    r = None

    try:
        raw_urim = generate_raw_urim(urim)
        r = session.get(raw_urim)

    except requests.exceptions.RequestException:
        module_logger.warning("Failed to download memento at URI-M {} ".format(urim))
        return 0

    try:
        soup = BeautifulSoup(r.text, 'html5lib')
        imagecount = 0

        img_tags = soup.find_all('img')

        for img in img_tags:

            if img.get('src') is not None:
                imagecount += 1
            
            if img.get('srcset') is not None:
                imagecount += 1

        return imagecount

    # there are generic exceptions in Beautiful Soup's code
    except Exception as e:
        module_logger.warning("Failed to process memento at URI-M {} -- exception: {}".format(urim, repr(e)))
        return 0

def score_by_image_count(urimdata, session):

    import concurrent.futures
    from hypercane.utils import get_boilerplate_free_content

    # force the order
    urimlist = sorted(urimdata.keys())

    image_counts = {}

    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_image_count, urim, session): urim for urim in urimlist }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                image_counts[urim] = future.result()

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))
                # sys.exit(255)

    for urim in urimlist:
        urimdata[urim]["Score---ImageCount"] = image_counts[urim]

    return urimdata
