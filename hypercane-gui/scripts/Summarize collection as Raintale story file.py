import argparse
import os
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.sample
import hypercane.errors

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    description="Submit a public web archive collection's ID and Hypercane will sample documents from the collection, generate metadata, and synthesize a rich story file for use with Raintale.",
    formatter_class=RawTextHelpFormatter
)

# 1 sample
# 2 metadata report
# 3 entity report
# 4 sumgram report
# 5 image report
# 6 Raintale story data file
