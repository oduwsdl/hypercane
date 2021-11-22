import argparse
import os
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.sample
import hypercane.errors

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    description="Submit a public web archive collection's ID and Hypercane will generate a file listing all archived page URLs (i.e., mementos, captures, URI-Ms).",
    formatter_class=RawTextHelpFormatter
)
