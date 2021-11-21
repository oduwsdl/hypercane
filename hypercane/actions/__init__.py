import sys

import hypercane.errors

def get_logger(appname, loglevel, logfile):

    import logging

    logger = logging.getLogger(appname)

    if logfile == sys.stdout:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            level=loglevel)
    else:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            level=loglevel,
            filename=logfile)

    return logger

def calculate_loglevel(verbose=False, quiet=False):

    import logging

    # verbose trumps quiet
    if verbose:
        return logging.DEBUG

    if quiet:
        return logging.WARNING

    return logging.INFO
