import sys
import os
import argparse
import json

from ..actions import add_input_args, add_default_args

def process_input_args(args, parser):

    parser = add_input_args(parser)

    # TODO: add clustered-mementos= as an input argument

    parser = add_default_args(parser)

    args = parser.parse_args(args)

    return args

def dsa1_publication_alg(args):
    raise NotImplementedError("DSA1 Publication Algorithm Ordering Not Implemented Yet")

supported_commands = {
    "dsa1-publication-alg": dsa1_publication_alg
}

