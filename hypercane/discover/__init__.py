from aiu import ArchiveItCollection

def generate_archiveit_urits(cid, seed_uris):
    """This function generates TimeMap URIs (URI-Ts) for a list of `seed_uris`
    from an Archive-It colleciton specified by `cid`.
    """

    urit_list = []

    for urir in seed_uris:
        urit = "http://wayback.archive-it.org/{}/timemap/link/{}".format(
            cid, urir
        )

        urit_list.append(urit)  

    return urit_list

def list_seed_uris(collection_id, session):

    aic = ArchiveItCollection(collection_id, session=session)

    return aic.list_seed_uris()