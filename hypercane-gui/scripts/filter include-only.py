import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(prog="hc filter include-only",
    description="'filter include-only' generates a list of mementos that only include the given feature",
    formatter_class=RawTextHelpFormatter
)

if __name__ == '__main__':

    args = parser.parse_args()

    print("Not implemented yet.")
