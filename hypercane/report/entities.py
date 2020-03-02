
import sys
import logging

module_logger = logging.getLogger('hypercane.report.entities')

def get_document_entities(urim, cache_storage, entity_types):
    import spacy
    from nltk.corpus import stopwords
    from hypercane.utils import get_boilerplate_free_content

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

    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:

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

    module_logger.info("discovered {} entities in corpus".format(len(corpus_entities)))

    fdist = nltk.FreqDist(corpus_entities)

    tf = []

    for term in fdist:
        tf.append( (fdist[term], term) )

    module_logger.info("calculated {} term frequencies".format(len(tf)))

    returned_terms = []

    for entry in sorted(tf, reverse=True):
        entity = entry[1]
        returned_terms.append( (
            entity, entry[0], float(entry[0])/float(len(tf)), 
            document_frequency[entity], document_frequency[entity] / len(urimlist),
            entry[0] * (document_frequency[entity] / len(urimlist))
        ) )

    return returned_terms
