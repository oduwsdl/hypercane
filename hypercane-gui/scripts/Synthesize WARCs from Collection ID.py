import argparse
import os
import argparse

from argparse import RawTextHelpFormatter

import hypercane.actions.sample
import hypercane.errors

from hypercane.version import __useragent__

parser = argparse.ArgumentParser(
    description="Submit a public Collection ID and recieve a ZIP file containing WARCs synthesized from the collection.",
    formatter_class=RawTextHelpFormatter
)
