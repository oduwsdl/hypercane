import logging
import io
import gzip
import numpy as np

module_logger = logging.getLogger('hypercane.report.metadatastats')

ignore_fields = [
    "videos"
]

default_metadata_fields = [
    "title",
    "creator",
    "subject",
    "description",
    "publisher",
    "contributor",
    "date",
    "type",
    "format",
    "identifier",
    "source",
    "relation",
    "coverage",
    "rights",
    "collector",
    "language"
]

def get_pct_seeds_with_metadata(ait_metadata):

    cid = ait_metadata['id']
    seed_metadata = ait_metadata['seed_metadata']['seeds']
    seedcount = len(seed_metadata)

    seeds_with_metadata = []

    for seed in seed_metadata:

        try:

            for entry in seed_metadata[seed]['collection_web_pages']:

                for key in entry:

                    if key.lower() not in ignore_fields:

                       seeds_with_metadata.append(seed)

        except KeyError as e:
            print("error in cid {}, seed {} -- e: {}".format(cid, seed, e))
            pass


    return len(set(seeds_with_metadata)) / seedcount

def get_pct_seeds_with_specific_field(ait_metadata, fieldname):

    cid = ait_metadata['id']
    seed_metadata = ait_metadata['seed_metadata']['seeds']
    seedcount = len(seed_metadata)

    seeds_with_metadata = []

    for seed in seed_metadata:

        try:

            for entry in seed_metadata[seed]['collection_web_pages']:

                for key in entry:

                    if key.lower() not in ignore_fields:

                        if key.lower() == fieldname:

                           seeds_with_metadata.append(seed)

        except KeyError as e:
            print("error in cid {}, seed {} -- e: {}".format(cid, seed, e))
            pass


    return len(set(seeds_with_metadata)) / seedcount


def get_pct_seeds_with_title(ait_metadata):

    return get_pct_seeds_with_specific_field(ait_metadata, 'title')

def get_pct_seeds_with_description(ait_metadata):

    return get_pct_seeds_with_specific_field(ait_metadata, 'description')

def get_mean_raw_field_count(ait_metadata):

    cid = ait_metadata['id']
    seed_metadata = ait_metadata['seed_metadata']['seeds']
    seedcount = len(seed_metadata)

    seed_metadata_count = {}

    for seed in seed_metadata:

        metadata_fields = []

        try:

            for entry in seed_metadata[seed]['collection_web_pages']:

                for key in entry:

                    if key.lower() not in ignore_fields:

                        metadata_fields.append( key )

        except KeyError as e:
            print("error in cid {}, seed {} -- e: {}".format(cid, seed, e))
            pass

        seed_metadata_count[seed] = len(set(metadata_fields))

    return np.mean(list(seed_metadata_count.values()))

def get_mean_default_field_score(ait_metadata):

    cid = ait_metadata['id']
    seed_metadata = ait_metadata['seed_metadata']['seeds']
    seedcount = len(seed_metadata)

    seed_metadata_count = {}

    for seed in seed_metadata:

        metadata_fields = []

        try:

            for entry in seed_metadata[seed]['collection_web_pages']:

                for key in entry:

                    if key.lower() not in ignore_fields:

                        if key.lower() in default_metadata_fields:

                            metadata_fields.append( key )

        except KeyError as e:
            print("error in cid {}, seed {} -- e: {}".format(cid, seed, e))
            pass

        seed_metadata_count[seed] = len(set(metadata_fields)) / 16

    return np.mean(list(seed_metadata_count.values()))

def get_metadata_compression_ratio(ait_metadata):

    cid = ait_metadata['id']
    seed_metadata = ait_metadata['seed_metadata']['seeds']

    metadata_as_string = ""

    for seed in seed_metadata:

#        metadata_as_string += "URL: {}".format(seed)

        try:

            for entry in seed_metadata[seed]['collection_web_pages']:

                for key in entry:

                    if key.lower() not in ignore_fields:

                        value = entry[key]

                        metadata_as_string += "{}: {}\n".format(key, value)

        except KeyError as e:
            print("error in cid {}, seed {} -- e: {}".format(cid, seed, e))
            pass

    # thanks SO/GitHub: https://gist.github.com/Garrett-R/dc6f08fc1eab63f94d2cbb89cb61c33d
    out = io.BytesIO()

    with gzip.GzipFile(fileobj=out, mode='w') as fo:
        fo.write(metadata_as_string.encode())

    compressed_bytes = out.getvalue()

    if len(compressed_bytes) > 0 and len(metadata_as_string.encode()) > 0:

        #return len(metadata_as_string.encode()) / len(compressed_bytes)
        return len(compressed_bytes) / len(metadata_as_string.encode())

    else:
        return 0
