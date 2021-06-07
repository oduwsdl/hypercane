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

        # import spacy
        # import sys

        # try:
        #     nlp = spacy.load('en_core_web_sm')
        # except OSError:
        #     print('Downloading language model for spaCy\n'
        #         "(don't worry, this will only happen once)", file=sys.stderr)
        #     from spacy.cli import download
        #     download('en')
        #     nlp = spacy.load('en_core_web_sm')

setup(
    name=__appname__.lower(),
    cmdclass={'install': Install},
    version=__appversion__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiu',
        'archivenow==2020.7.18.12.19.44',
        'boilerpy3',
        'distance',
        'newspaper3k',
        'guess-language-spirit',
        'jsonlines',
        'MementoEmbed',
        'nltk',
        'otmt',
        'pymongo',
        'rank_bm25',
        'requests',
        'requests_cache==0.5.2',
        'scrapy',
        'sentencepiece',
        'simhash',
        'spacy',
        'sumgram',
        'surt',
        'transformers',
        'torch',
        'warcio'
    ],
    # setup_requires=[
    #     'nltk',
    #     # 'spacy'
    # ],
    scripts=[
        'bin/hc'
    ]
)

