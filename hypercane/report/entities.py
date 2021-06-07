
import sys
import logging

module_logger = logging.getLogger('hypercane.report.entities')

def get_document_entities(urim, cache_storage, entity_types):
    import spacy
    from nltk.corpus import stopwords
    from hypercane.utils import get_boilerplate_free_content

    module_logger.debug("starting entity extraction process for {}".format(urim))

    content = get_boilerplate_free_content(urim, cache_storage=cache_storage)

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(content.decode('utf8'))

    entities = []

    for ent in doc.ents:
        if ent.label_ in entity_types:
            entities.append(ent.text.strip().replace('\n', ' ').lower())

    return entities

def generate_entities(urimlist, cache_storage, entity_types):

    import concurrent.futures
    import nltk

    corpus_entities = []
    document_frequency = {}

    completed_count = 0

    # with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_document_entities, urim, cache_storage, entity_types): urim for urim in urimlist }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                document_entities = future.result()
                corpus_entities.extend( document_entities )

                for entity in list(set(document_entities)):
                    document_frequency.setdefault(entity, 0)
                    document_frequency[entity] += 1

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))

            completed_count += 1

            if completed_count % 100 == 0:
                module_logger.info("extracted entities from ({}/{}) mementos".format(completed_count, len(urimlist)))

    module_logger.info("discovered {} entities in corpus".format(len(corpus_entities)))

    fdist = nltk.FreqDist(corpus_entities)

    tf = []

    for term in fdist:
        tf.append( (fdist[term], term) )

    module_logger.info("calculated {} term frequencies".format(len(tf)))

    returned_terms = []

    for entry in sorted(tf, reverse=True):
        entity = entry[1]
        frequency_in_corpus = entry[0]
        probability_in_corpus = float(entry[0])/float(len(tf))
        inverse_document_frequency = document_frequency[entity] / len(urimlist)
        corpus_tfidf = entry[0] * (document_frequency[entity] / len(urimlist))
        returned_terms.append( (
            entity, frequency_in_corpus, probability_in_corpus,
            document_frequency[entity], inverse_document_frequency,
            corpus_tfidf
        ) )

    return returned_terms
