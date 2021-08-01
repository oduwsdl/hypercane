import argparse
from argparse import RawTextHelpFormatter

order_parser = argparse.ArgumentParser(prog="hc order",
    description="'hc order' orders the memento list input by some feature or function.",
    formatter_class=RawTextHelpFormatter
)

subparsers = order_parser.add_subparsers(help='ordering methods', dest="ordering method ('e.g., memento-datetime")
subparsers.required = True

pubdate_parser = subparsers.add_parser('pubdate-else-memento-datetime', help="order the documents according to AlNoamany's Algorithm")
pubdate_parser.set_defaults(which='pubdate-else-memento-datetime')

mementodatetime_parser = subparsers.add_parser('memento-datetime', help="order the documents by memento-datetime")
mementodatetime_parser.set_defaults(which='memento-datetime')

score_parser = subparsers.add_parser('score', help="order the documents by score")
score_parser.set_defaults(which='score')

score_parser.add_argument('--descending', help="If specified, sort such that highest scoring URI-Ms are first.",
    action='store_true', default=False, dest='descending'
)

score_parser.add_argument('--scoring-field', help="Specify the scoring field to sort by, default is first encountered",
    default=None, dest='scoring_field'
)