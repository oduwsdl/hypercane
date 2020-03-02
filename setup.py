from setuptools import setup, find_packages

# to get pylint to shut up
__appname__ = None
__appversion__ = None

# __appname__, __appversion__, and friends come from here
exec(open("hypercane/version.py").read())

setup(
    name=__appname__.lower(),
    version=__appversion__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiu',
        'archivenow',
        'distance',
        'newspaper3k',
        'guess-language-spirit',
        'MementoEmbed',
        'otmt',
        'pymongo',
        'requests',
        'requests_cache',
        'scrapy',
        'simhash',
        'spacy',
        'warcio'
    ],
    scripts=[
        'bin/hc'
    ],
    test_suite="tests"
)

import spacy
import sys

try:
    nlp = spacy.load('en')
except OSError:
    print('Downloading language model for the spaCy POS tagger\n'
        "(don't worry, this will only happen once)", file=sys.stderr)
    from spacy.cli import download
    download('en')
    nlp = spacy.load('en')