
# def execute_ds1(cid, cache_storage):

#   ontopic_urims = detect_off_topic(dbconn, session, urits, urims, timemap_measures, num_topics)
#   filtered_urims = filter_near_duplicates(ontopic_urims, cache_storage)
#   filtered_urims = filter_by_language(filtered_urims, cache_storage)
#   clustered_urims = cluster_with_timeslice(filtered_urims, cache_storage)
#   clustered_urims = cluster_with_dbscan(filtered_urims, cache_storage, "tf-simhash")
#   clustered_urims = rank_by_dsa1_score(clustered_urims, cache_storage)
#   filtered_urims = filter_by_top_rank(clustered_urims, cache_storage)
#   ordered_urims = order_by_dsa1_publication(clustered_urims, cache_storage)
