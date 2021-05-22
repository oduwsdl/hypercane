Core Actions
============

.. attention::
    All examples on this page assume that the ``HC_CACHE_STORAGE`` variable has been set. If you do not know what this means, read the :ref:`caching_and_being_nice` section first.

For sampling from a collection or converting it into different forms, Hypercane offers the core actions of:

* ``sample`` - for creating a sample of a collection
* ``report`` - for generating a report on collection metadata, named entities, curation behavior, and more
* ``synthesize`` - for generating output for other tools, like `Archives Unleashed Toolkit <https://github.com/archivesunleashed/aut>`_ or `Raintale <https://oduwsdl.github.io/raintale/>`_

.. _sample:

``sample``
----------

Hypercane's ``sample`` action allows a user to provide input

* ``true-random`` - samples *k* mementos from the input, randomly
* ``filtered-random`` - removes off-topic mementos, near-duplicates, and then randomly samples *k* mementos from the remainder
* ``dsa1`` - executes an updated version of `AlNoamany's original sampling algorithm <https://doi.org/10.1145/3091478.3091508>`_, may also be specified using ``alnoamany``
* ``systematic`` - chooses every *jth* memento from the input

For example, to randomly sample 5 mementos from Trove collection 8125, type the following:

.. code-block:: text

    hc sample true-random -i trove -a 8125 -k 5 -o randomly-sampled.tsv

or to intelligently sample a set of approximately 28 mementos from Archive-It collection 694:

.. code-block:: text

    hc sample dsa1 -i archiveit -a 694 -o sampled-with-dsa1.tsv

or to systematically sample every 4th memento from the mementos in *mementos.tsv*:

.. code-block:: text

    hc sample systematic -i mementos -a mementos.tsv -o sampled-systematically.tsv -j 4

Hypercane's ``sample`` action can also execute the following algorithms on output provided by its :ref:`cluster` action:

* ``stratified-random`` - chooses *j* random mementos from each cluster
* ``stratified-systematic`` - chooses every *jth* memento from each cluster
* ``random-cluster`` - randomly chooses *j* clusters from the input and returns their mementos
* ``random-oversample`` - randomly chooses mementos from clusters until those clusters are the same size as the largest cluster
* ``random-undersample`` - randomly chooses mementos from clusters until those clusters are the same size as the smallest cluster

Type ``hc sample --help`` for more information on all available options. The ``--help`` argument can also be supplied to a single option for more information, e.g., ``hc sample dsa1 --help``.

.. _report:

``report``
----------

Hypercane can produce reports for use in storytelling and rudimentary collection analysis.  The following report styles are available for use with the ``report`` action: 

* ``metadata`` - the metadata scraped from an Archive-It collection; output is a JSON file
* ``image-data`` - provides information about all embedded images discovered in the input and ranks them so Raintale has a striking image for the story; output is a JSON file
* ``seed-statistics`` - calculates metrics on the original resources discovered in the input, as mentioned in `Jones et al. in 2018 <https://doi.org/10.17605/OSF.IO/EV42P>`_; output is a JSON file
* ``metadata-statistics`` - calculates metrics on the metadata discovered in the input, as used across collections by `Jones et al. in 2019 <https://doi.org/10.1145/3357384.3358039>`_; output is a JSON file
* ``html-metadata`` - a report on the metadata available in each memento's HTML \texttt{META} tag, as applied by `Jones et al. in 2021 <https://arxiv.org/abs/2104.04116>`_ ; output is a JSON file
* ``growth`` - calculates metrics on the collection growth, as described in `Jones et al. in 2018 <https://doi.org/10.17605/OSF.IO/EV42P>`_; output is a JSON file
* ``terms`` - provides all terms discovered in the input, including their frequency, document frequency, probability, and corpus-wide TF-IDF; output is a tab-delimited file
* ``entities`` - provides a list of all entities discovered in the input, including frequency, probability, and corpus-wide TF-IDF; output is a tab-delimited file

For example, to generate a report on the metadata for Archive-It collection 8788 and save it in a file named *8788-metadata.json*:

.. code-block:: text

    hc report metadata -i archiveit -a 8788 -o 8788-metadata.json

or to do the same for Trove collection 13742:

.. code-block:: text

    hc report metadata -i trove -a 13742 -o 13742-metadata.json

or generate the entities from a list of mementos:

.. code-block:: text

    hc report entities -i mementos -a memento-file.tsv -o entity-report.json

Type ``hc report --help`` for more information on all available options. The ``--help`` argument can also be supplied to a single option for more information, e.g., ``hc report growth --help``.

.. _synthesize:

``synthesize``
--------------

Hypercane's ``synthesize`` action allows users to generate output for other tools with output in other formats, like WARC, JSON, or a set of files in a directory.  The ``synthesize`` action has the following supported output formats:

* ``warcs`` - (experimental) for generating a directory of WARCs
* ``files`` - for generating a directory of mementos
* ``bpfree-files`` - for generating a directory of boilerplate-free mementos
* ``raintale-story`` - for generating a JSON file suitable as input for Raintale
* ``combine`` - combine the output from several Hypercane runs together

To synthesize Archive-It collection 694 into a set of WARCs stored in *output-directory*:

.. code-block:: text

    hc synthesize warcs -i archiveit -a 694 -o output-directory

To synthesize a list of mementos into a set of WARCs stored in *output-directory* without any embedded images, JavaScript, or stylesheets:

    .. code-block:: text
    
        hc synthesize warcs -i archiveit -a 694 -o output-directory --no-download-embedded

To synthesize a Raintale story built from the output of other Hypercane commands:

.. code-block:: text

    hc synthesize raintale-story -i mementos -a story-mementos.tsv \
        --imagedata imagedata.json --termdata sumgrams.json \
        --entitydata entities.json --collection_metadata metadata.json \ 
        --title "Archive-It Collection" -o raintale-story.json

Type ``hc synthesize --help`` for more information on all available options. The ``--help`` argument can also be supplied to a single option for more information, e.g., ``hc synthesize warcs --help``.

For more examples and a discussion of using ``synthesize`` please `read this blog post <https://ws-dl.blogspot.com/2020/06/2020-06-10-hypercane-part-2.html>`_.
