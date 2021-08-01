import argparse
from argparse import RawTextHelpFormatter

order_parser = argparse.ArgumentParser(prog="hc order",
    description="'hc order' orders the memento list input by some feature or function.",
    formatter_class=RawTextHelpFormatter
)

subparsers = order_parser.add_subparsers(help='ordering methods', dest="ordering method ('e.g., memento-datetime")
subparsers.required = True

pubdate_parser = subparsers.add_parser('pubdate-else-memento-datetime', help="order the documents according to AlNoamany's Algorithm")

mementodatetime_parser = subparsers.add_parser('memento-datetime', help="order the documents by memento-datetime")

score_parser = subparsers.add_parser('score', help="order the documents by score")