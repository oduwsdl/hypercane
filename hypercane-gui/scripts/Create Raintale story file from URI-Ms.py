import argparse
import os
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.sample
import hypercane.errors

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    prog="create Raintale story file by Collection ID.py",
    description="Submit a file containing a set of archived page URLs (i.e., mementos, captures, URI-Ms) and Hypercane will  synthesize a rich Raintale story file.",
    formatter_class=RawTextHelpFormatter
)
