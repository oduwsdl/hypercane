import uuid
import logging

import aiu

from requests_futures.sessions import FuturesSession

from .collectionmodel import DSACollectionModel

module_logger = logging.getLogger('hypercane.input_types')


def generate_archiveit_urit(cid, seed_uri):
    """This function generates a TimeMap URI (URI-Ts) for a seed_uris
    from an Archive-It collection specified by `cid`.
    """

    urit = "https://wayback.archive-it.org/{}/timemap/link/{}".format(
        cid, seed_uri
    )

    return urit

def get_collection_model_from_archiveit(collection_id, working_directory, session, download_anyway=False):
    
    module_logger.info("gathering metadata for collection {}".format(collection_id))

    aic = aiu.ArchiveItCollection(collection_id, session=session)

    fs = FuturesSession(session=session)

    cm = DSACollectionModel(collection_id, working_directory, session=fs)

    cm.metadata["collection_id"] = collection_id
    cm.metadata["collection_name"] = aic.get_collection_name()
    cm.metadata["collected_by"] = aic.get_collectedby()
    cm.metadata["archived_since"] = aic.get_archived_since()
    cm.metadata["is_private"] = aic.is_private()
    cm.metadata["does_exist"] = aic.does_exist()
    
    for key in aic.list_optional_metadata_fields():
        cm.metadata[key] = aic.get_optional_metadata(key)
    
    seed_uris = aic.list_seed_uris()

    cm.seedlist = seed_uris

    for seeduri in cm.seedlist:

        urit = generate_archiveit_urit(collection_id, seeduri)

        cm.seed_urits[seeduri] = urit

        if download_anyway is True:
            # fetch each URI-T and insert into collection model
            # fetch each URI-M from the TimeMaps and insert into collection model
            module_logger.info("downloading timemaps and mementos for collection...")
            cm.add_TimeMapMementos(urit)
            cm.collect_all_results()
        else:
            cm.add_TimeMap(urit)

    return cm

# def get_collection_model_from_timemap(urits, working_directory, session, download_anyway=False):

#     fs = FuturesSession(session=session)

#     cm = DSACollectionModel("TM-{}".format(uuid.uuid1().hex), working_directory, session=fs)

#     for urit in urits:
#         if download_anyway is True:
#             # fetch each URI-T and insert into collection model
#             # fetch each URI-M from the TimeMaps and insert into collection model
#             cm.add_TimeMapMementos(urit)
#             cm.collect_all_results()
#         else:
#             cm.add_TimeMap(urit)

#     return cm 

supported_input_types = {
    'archiveit': get_collection_model_from_archiveit
    # 'timemap': get_collection_model_from_timemap
}

def get_collection_model(input_type, arguments, working_directory, session, download_anyway=False):

    module_logger.debug("download_anyway is {}".format(download_anyway))

    if input_type == 'archiveit':
        collection_id = arguments[0]
        return supported_input_types[input_type](
            collection_id, working_directory, 
            session, download_anyway=download_anyway)
    else:
        return supported_input_types[input_type](
            arguments, working_directory, session,
            download_anyway=download_anyway
            )

    
    