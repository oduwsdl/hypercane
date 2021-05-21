Core Actions
============

.. _sample:

``sample``
----------

Hypercane's ``sample`` action allows a user to provide input

* ``true-random`` - samples *k* mementos from the input, randomly
* ``filtered-random`` - removes off-topic mementos, near-duplicates, and then samples *k* mementos from the remainder, randomly
* ``dsa1`` - executes an updated version of `AlNoamany's original sampling algorithm <https://doi.org/10.1145/3091478.3091508>`_, may also be specified using alnoamany
* ``systematic`` - chooses every *jth* memento from the input

Hypercane's ``sample`` action can also execute the following algorithms on output provided by its :ref:`cluster` action:

* ``stratified-random`` - chooses *j* random mementos from each cluster
* ``stratified-systematic`` - chooses every *jth* memento from each cluster
* ``random-cluster`` - randomly chooses *j* clusters from the input and returns their mementos
* ``random-oversample`` - randomly chooses mementos from clusters until those clusters are the same size as the largest cluster
* ``random-undersample`` - randomly chooses mementos from clusters until those clusters are the same size as the smallest cluster

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

.. _synthesize:

``synthesize``
--------------

Hypercane's ``synthesize`` action allows users to generate output for other tools with output in other formats, like WARC, JSON, or a set of files in a directory.  The ``synthesize`` action has the following supported commands:

* ``warcs`` - for generating a directory of WARCs
* ``files`` - for generating a directory of mementos
* ``bpfree-files`` - for generating a directory of boilerplate-free mementos
* ``raintale-story`` - for generating a JSON file suitable as input for Raintale
* ``combine`` - combine the output from several Hypercane runs together
