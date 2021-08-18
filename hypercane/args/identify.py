import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime

import hypercane.actions.identify

identify_parser = argparse.ArgumentParser(prog="hc identify",
    description="'identify' discovers resource identifiers in a web archive collection, a list of TimeMaps, original resources, or mementos",
    formatter_class=RawTextHelpFormatter
)

subparsers = identify_parser.add_subparsers(help='identifying methods', dest='identifying method (timemaps, mementos, or original-resources)')
subparsers.required = True

memento_parser = subparsers.add_parser('mementos', help="Discover the mementos in a web archive collection.")
memento_parser.set_defaults(
    which='mementos',
    exec=hypercane.actions.identify.discover_mementos
)

memento_parser.add_argument('--timegates',
    default=[
        "https://timetravel.mementoweb.org/timegate/",
        "https://web.archive.org/web/"
    ], required=False, dest='timegates',
    help='(only for original resource input type)\n'
    'use the given TimeGate endpoints to discover mementos',
    type=lambda s: [i.strip() for i in s.split(',')]
)

memento_parser.add_argument('--accept-datetime', '--desired-datetime',
    default=None, required=False, dest='accept_datetime',
    help='(only for original resource input type)\n'
    'discover mementos closest to this datetime in YYYY-mm-ddTHH:MM:SS format',
    type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
)

timemap_parser = subparsers.add_parser('timemaps', help="Discover the TimeMaps in a web archive collection.")
timemap_parser.set_defaults(
    which='timemaps',
    exec=hypercane.actions.identify.discover_timemaps
)

# note: this is just for testing purposes, but do not remove this argument
timemap_parser.add_argument('--faux-tms-acceptable', 
    # help="accept faux URI-Ts as output; if you do not understand this, you likely do not want this option",
    help=argparse.SUPPRESS,
    action='store_true', required=False,
    dest='faux_tms_acceptable')

originalresource_parser = subparsers.add_parser('original-resources', help="Discover the original resources in a web archive collection.")
originalresource_parser.set_defaults(
    which='original-resources',
    exec=hypercane.actions.identify.discover_original_resources
)
