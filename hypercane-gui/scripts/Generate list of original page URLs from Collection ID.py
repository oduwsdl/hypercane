import argparse
import os
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.sample
import hypercane.errors

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    description="Submit a public web archive collection's ID and Hypercane will generate a file listing all original page URLs (i.e., original resources, URI-Rs).",
    formatter_class=RawTextHelpFormatter
)
