import hypercane.errors
import concurrent.futures
import logging
import traceback

module_logger = logging.getLogger('hypercane.report.generate_queries')

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

def generate_queries_from_metadata_with_doct5query(metadata, cache_storage, query_count):

    from transformers import T5Tokenizer, T5ForConditionalGeneration
    import torch

    query_data = {}
    doc_text = ""

    for field in metadata:

        if field != 'seed_list':

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

    # To avoid issue with "Token indices sequence length is longer than the specified maximum sequence length for this model (1853 > 512). Running this sequence through the model will result in indexing errors"
    doc_text = doc_text[0:512]

    query_data["input_text"] = doc_text

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    module_logger.info("using {} as floating point calculation device".format(device))

    module_logger.info("creating T5 tokenizer trained from MSMARCO")
    tokenizer = T5Tokenizer.from_pretrained('castorini/doc2query-t5-base-msmarco')

    module_logger.info("creating model from doc2query base MSMARCO")
    model = T5ForConditionalGeneration.from_pretrained('castorini/doc2query-t5-base-msmarco')

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
        query_data.setdefault("metadata", []).append( query )

    return query_data
