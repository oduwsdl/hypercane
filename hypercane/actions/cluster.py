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

def time_slice(args):
    raise NotImplementedError("Time Slice Clustering Not Implemented Yet")

def dbscan(args):
    raise NotImplementedError("DBSCAN Clustering Not Implementing Yet")

supported_commands = {
    "time-slice": time_slice,
    "dbscan": dbscan
}

