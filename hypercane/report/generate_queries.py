import hypercane.errors
import concurrent.futures
import logging
import traceback

module_logger = logging.getLogger('hypercane.report.generate_queries')

def generate_lexical_signatures_from_documents_with_tfidf(urimdata, cache_storage, threshold):

    from hypercane.utils import get_boilerplate_free_content
    from sklearn.feature_extraction.text import TfidfVectorizer
    from nltk.corpus import stopwords
    import string
    import random

    query_data = {}

    corpus = []
    urim_to_corpus = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_boilerplate_free_content, urim, cache_storage): urim for urim in urimdata.keys() }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                content = future.result()
                corpus.append( content )
                urim_to_corpus.append( urim )

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    stop_words = stopwords.words('english')
    stop_words.extend(string.punctuation)
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))
    X = vectorizer.fit_transform(corpus)

    for i in range(0, len(urim_to_corpus)):

        urim = urim_to_corpus[i]

        tfidf_per_word = sorted(
            [ (f, t) for t, f in dict(zip(vectorizer.get_feature_names(), X.toarray()[i])).items() ], reverse=True)

        # in case every word has the same TFIDF value
        topval = tfidf_per_word[0:threshold][0][0]
        topvalues = [ f for f, t in tfidf_per_word[0:threshold] ]
        if all(topval == f for f in topvalues):
            
            # does everyone have the same value?
            if all(topval == f for f, t in tfidf_per_word):
                lexical_signature = " ".join( [ t for f, t in random.sample(tfidf_per_word, k=threshold) ] )

            else:
                # what about those where topval refers to a lot of items?

                terms_to_consider = []

                for f, t in tfidf_per_word:

                    if f == topval:
                        terms_to_consider.append( t )

                lexical_signature = " ".join( random.sample(terms_to_consider, k=threshold) )

        else:

            lexical_signature = " ".join(
                [ t for f, t in tfidf_per_word[0:threshold] ]
            )
        
        module_logger.debug("generated query [{}] for URI-M {}".format(lexical_signature, urim))
        query_data.setdefault(urim, []).append( lexical_signature )

    return query_data

def generate_queries_from_documents_with_doct5query(urimdata, cache_storage, query_count):

    from hypercane.utils import get_boilerplate_free_content
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    import torch

    urim_to_content = {}
    query_data = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_boilerplate_free_content, urim, cache_storage): urim for urim in urimdata.keys() }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                content = future.result()
                urim_to_content[urim] = content

            except Exception as exc:
                module_logger.exception('URI-M [{}] generated an exception: [{}], skipping...'.format(urim, exc))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    module_logger.info("using {} as floating point calculation device".format(device))

    module_logger.info("creating T5 tokenizer trained from MSMARCO")
    tokenizer = T5Tokenizer.from_pretrained('castorini/doc2query-t5-base-msmarco')

    module_logger.info("creating model from doc2query base MSMARCO")
    model = T5ForConditionalGeneration.from_pretrained('castorini/doc2query-t5-base-msmarco')

    for urim in urim_to_content:
        module_logger.info("creating {} queries for {}".format(query_count, urim))
        
        doc_text = urim_to_content[urim].decode('utf8')
        # To avoid issue with "Token indices sequence length is longer than the specified maximum sequence length for this model (1853 > 512). Running this sequence through the model will result in indexing errors"
        doc_text = doc_text[0:512]
        input_ids = tokenizer.encode(doc_text, return_tensors='pt').to(device)
        outputs = model.generate(
            input_ids=input_ids,
            max_length=64,
            do_sample=True,
            top_k=10,
            num_return_sequences=query_count)

        for i in range(query_count):
            query = tokenizer.decode(outputs[i], skip_special_tokens=True)
            module_logger.debug("generated query [{}] for URI-M {}".format(query, urim))
            query_data.setdefault(urim, []).append( query )

    return query_data

def generate_metadata_as_document(metadata):

    doc_text = ""

    for field in metadata:

        module_logger.debug("examining field {} of type {}".format(field, type(metadata[field])))
        # module_logger.info("doc_text is now\n{}".format(doc_text))

        if field not in [ 'seed_list', 'metadata_timestamp', 'collection_uri', 'collected_by_uri' ]:

            if type(metadata[field]) == str:
                doc_text += "{} : {}\n".format( field, metadata[field] )
            elif type(metadata[field]) == list:
                doc_text += "{} : {}\n".format(field, ",".join(metadata[field]))

    for seed in metadata['seed_metadata']['seeds']:

        for subfield in metadata['seed_metadata']['seeds'][seed]['collection_web_pages'][0]:

            if type(metadata['seed_metadata']['seeds'][seed]['collection_web_pages'][0][subfield]) == str:

                doc_text += "{} : {}\n".format( subfield, metadata['seed_metadata']['seeds'][seed]['collection_web_pages'][0][subfield] )

            elif type(metadata['seed_metadata']['seeds'][seed]['collection_web_pages'][0][subfield]) == list:

                doc_text += "{} : {}\n".format( subfield, 
                    ",".join( metadata['seed_metadata']['seeds'][seed]['collection_web_pages'][0][subfield] )
                )

    return doc_text

def generate_queries_from_metadata_with_doct5query(metadata, cache_storage, query_count):

    from transformers import T5Tokenizer, T5ForConditionalGeneration
    import torch

    module_logger.info("query count is {} and is type {}".format(query_count, type(query_count)))

    query_data = {}
    doc_text = generate_metadata_as_document(metadata)

    module_logger.info("generated full collection metadata of length {} as:\n{}".format(len(doc_text), doc_text))

    query_data["input_text"] = doc_text

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    module_logger.info("using {} as floating point calculation device".format(device))

    module_logger.info("creating T5 tokenizer trained from MSMARCO")
    tokenizer = T5Tokenizer.from_pretrained('castorini/doc2query-t5-base-msmarco')

    module_logger.info("creating model from doc2query base MSMARCO")
    model = T5ForConditionalGeneration.from_pretrained('castorini/doc2query-t5-base-msmarco')

    # To avoid issue with "Token indices sequence length is longer than the specified maximum sequence length for this model (1853 > 512). Running this sequence through the model will result in indexing errors"
    doc_text = doc_text[0:512]
    module_logger.info("generated collection metadata of length {} as:\n{}".format(len(doc_text), doc_text))
    input_ids = tokenizer.encode(doc_text, return_tensors='pt').to(device)
    outputs = model.generate(
        input_ids=input_ids,
        max_length=64,
        do_sample=True,
        top_k=10,
        num_return_sequences=query_count)

    for i in range(query_count):
        query = tokenizer.decode(outputs[i], skip_special_tokens=True)
        module_logger.debug("generated query [{}] from metadata".format(query, metadata))
        query_data.setdefault("queries", []).append( query )

    return query_data

# def generate_queries_from_documents_with_topnterms(urimdata, cache_storage, threshold):

#     import concurrent.futures
#     from hypercane.report.terms import get_document_tokens

#     query_data = {}

#     # NLTK is not thread safe: https://github.com/nltk/nltk/issues/803
#     # urim_to_ngrams = {}
#     # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

#     #     future_to_urim = { executor.submit(get_document_tokens, urim, cache_storage, ngram_length=1, added_stopwords=[]): urim for urim in urimdata }

#     #     for future in concurrent.futures.as_completed(future_to_urim):

#     #         urim = future_to_urim[future]

#     #         try:
#     #             # TODO: we're storing the result in RAM, essentially storing the whole collection there, maybe a generator would be better?
#     #             document_ngrams = future.result()
#     #             urim_to_ngrams.setdefault(urim, []).append( document_ngrams )

#     #         except Exception as exc:
#     #             module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))

#     for urim in urimdata:
    
#         document_ngrams = get_document_tokens(urim, cache_storage, ngram_length=1)

#         from pprint import PrettyPrinter
#         pp = PrettyPrinter(indent=4)

#         pp.pprint(urim)
        
#         ngram_counts = {}
#         all_full_ngrams = []

#         for ngram in document_ngrams:

#             full_ngram = " ".join(ngram)

#             all_full_ngrams.append(full_ngram)

#         pp.pprint(all_full_ngrams)

#         for full_ngram in set(all_full_ngrams):

#             ngram_counts.setdefault( full_ngram, 0 )
#             ngram_counts[full_ngram] += all_full_ngrams.count(full_ngram)

#         pp.pprint(ngram_counts)
#         import sys
#         sys.exit(255)

#         tf = []
#         for ngram in ngram_counts:

#             tf.append( ( ngram_counts[ngram], ngram ) )

#         # from pprint import PrettyPrinter
#         # pp = PrettyPrinter(indent=4)
#         # pp.pprint(tf)

#         query_terms = " ".join( [ w[1] for w in sorted(tf, reverse=True)[0:threshold] ] )

#         query_data.setdefault(urim, []).append(query_terms)

#     return query_data

def generate_queries_from_documents_with_topentities(urimdata, cache_storage, threshold, entity_types):

    import concurrent.futures
    from hypercane.report.entities import get_document_entities

    query_data = {}

    urim_to_entities = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_document_entities, urim, cache_storage, entity_types=entity_types): urim for urim in urimdata }

        for future in concurrent.futures.as_completed(future_to_urim):

            urim = future_to_urim[future]

            try:
                # TODO: we're storing the result in RAM, essentially storing the whole collection there, maybe a generator would be better?
                document_entities = future.result()
                urim_to_entities[urim] = document_entities

            except Exception as exc:
                module_logger.exception("URI-M [{}] generated an exception [{}], skipping...".format(urim, repr(exc)))

    for urim in urim_to_entities:
    
        ef = []

        for term in set(urim_to_entities[urim]):

            ef.append( ( urim_to_entities[urim].count(term), term ) )

        query_terms = " ".join( [ e[1] for e in sorted(ef, reverse=True) ] [0:threshold] )

        query_data.setdefault(urim, []).append(query_terms)

    return query_data

def generate_queries_from_metadata_with_topentities(metadata, cache_storage, threshold, entity_types):

    import spacy
    import nltk

    nlp = spacy.load("en_core_web_sm")

    query_data = {}

    doc_text = generate_metadata_as_document(metadata)
    doc = nlp(doc_text)

    entities = []

    for ent in doc.ents:
        if ent.label_ in entity_types:
            entities.append(ent.text.strip().replace('\n', ' ').lower())

    entitycount = {}

    for entity in entities:
        entitycount.setdefault(entity, 0)
        entitycount[entity] += 1

    query = " ".join( [ e[1] for e in sorted( [ (v, k) for k, v in entitycount.items() ], reverse=True )[0:threshold] ] )

    query_data.setdefault("queries", []).append(query)

    return query_data

def generate_lexical_signature_from_metadata(metadata, cache_storage, threshold):

    from sklearn.feature_extraction.text import TfidfVectorizer
    from nltk.corpus import stopwords
    import string
    import random

    query_data = {}

    doc_text = generate_metadata_as_document(metadata)
    corpus = [ doc_text ]

    stop_words = stopwords.words('english')
    stop_words.extend(string.punctuation)
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))
    X = vectorizer.fit_transform(corpus)

    tfidf_per_word = sorted(
            [ (f, t) for t, f in dict(zip(vectorizer.get_feature_names(), X.toarray()[0])).items() ], reverse=True)

    topval = tfidf_per_word[0:threshold][0][0]
    topvalues = [ f for f, t in tfidf_per_word[0:threshold] ]
    if all(topval == f for f in topvalues):
        
        # does everyone have the same value?
        if all(topval == f for f, t in tfidf_per_word):
            lexical_signature = " ".join( [ t for f, t in random.sample(tfidf_per_word, k=threshold) ] )

        else:
            # what about those where topval refers to a lot of items?

            terms_to_consider = []

            for f, t in tfidf_per_word:

                if f == topval:
                    terms_to_consider.append( t )

            lexical_signature = " ".join( random.sample(terms_to_consider, k=threshold) )

    else:

        lexical_signature = " ".join(
            [ t for f, t in tfidf_per_word[0:threshold] ]
        )

    query_data.setdefault("queries", []).append(lexical_signature)

    return query_data
