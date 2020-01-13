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
        'distance',
        'otmt',
        'pymongo',
        'requests',
        'requests_cache',
        'scrapy',
        'simhash'
    ],
    scripts=[
        'bin/hc'
    ],
    test_suite="tests"
)
