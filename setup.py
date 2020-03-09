from setuptools import setup, find_packages
from setuptools.command.install import install as _install

# to get pylint to shut up
__appname__ = None
__appversion__ = None

# __appname__, __appversion__, and friends come from here
exec(open("hypercane/version.py").read())

class Install(_install):
    def run(self):
        _install.run(self)
        import nltk
        nltk.download("stopwords")
        nltk.download("punkt")

        import spacy
        import sys

        try:
            nlp = spacy.load('en')
        except OSError:
            print('Downloading language model for spaCy\n'
                "(don't worry, this will only happen once)", file=sys.stderr)
            from spacy.cli import download
            download('en')
            nlp = spacy.load('en')

setup(
    name=__appname__.lower(),
    cmdclass={'install': Install},
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
        'sumgram',
        'warcio'
    ],
    scripts=[
        'bin/hc'
    ],
    test_suite="tests"
)

