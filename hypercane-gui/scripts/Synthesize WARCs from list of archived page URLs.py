import argparse
import os
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.sample
import hypercane.errors

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    description="Submit a file containing a set of archived page URLs (i.e., mementos, captures, URI-Ms) and Hypercane will generate a ZIP file containing WARCs synthesized from these URLs.",
    formatter_class=RawTextHelpFormatter
)
