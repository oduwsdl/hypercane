import argparse
import os
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.sample
import hypercane.errors

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    prog="create Raintale story file from URI-Ms.py",
    description="Submit a file containing a set of archived page URLs (i.e., mementos, captures, URI-Ms) and Hypercane will  generate metadata and synthesize a rich story file for use with Raintale.",
    formatter_class=RawTextHelpFormatter
)
