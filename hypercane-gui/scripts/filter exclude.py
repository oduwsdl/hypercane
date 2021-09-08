import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(prog="hc filter exclude",
    description="'filter exclude' generates a list of mementos that do not contain the given feature",
    formatter_class=RawTextHelpFormatter
)

if __name__ == '__main__':

    args = parser.parse_args()

    print("Not implemented yet.")
