import os
import unittest
import tempfile
import logging

import pprint

pp = pprint.PrettyPrinter(indent=4)

from hypercane.actions.hfilter import remove_offtopic

cache_storage="mongodb://localhost/csHypercaneTesting"

scriptdir=os.path.dirname(os.path.realpath(__file__))

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class TestHfilterExcludeOfftopic(unittest.TestCase):

    def test_archiveit_694(self):

        output_filename = tempfile.mkstemp()[1]

        logging.disable(logging.ERROR)

        args = Namespace(
            cache_storage=cache_storage,
            input_type='archiveit',
            input_arguments='694',
            crawl_depth=1,
            timemap_measures={ "cosine": 0.12 },
            num_topics=10,
            verbose=True,
            output_filename=output_filename,
            allow_noncompliant_archives=False
        )

        remove_offtopic(args)

        output_lines = []

        with open(output_filename) as f:
            for line in f:
                line=line.strip()
                output_lines.append(line)

        # pp.pprint(output_lines)
        expected_output_lines = []

        with open('{}/694-ontopic.txt'.format(scriptdir)) as f:

            for line in f:

                line = line.strip()
                expected_output_lines.append(line)

        self.assertEqual(len(output_lines), len(expected_output_lines))
        self.assertEqual(set(output_lines), set(expected_output_lines))
        os.unlink(output_filename)  
