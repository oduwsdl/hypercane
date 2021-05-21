Core Actions
============

.. _sample:

sample
------

Hypercane's ``sample`` action allows a user to provide input

* ``true-random`` - samples *k* mementos from the input, randomly
* ``filtered-random`` - removes off-topic mementos, near-duplicates, and then samples *k* mementos from the remainder, randomly
* ``dsa1`` - executes an updated version of `AlNoamany's original sampling algorithm <https://doi.org/10.1145/3091478.3091508>`_, may also be specified using alnoamany
* ``systematic`` - chooses every *jth* memento from the input

Hypercane's :ref:`sample` action can also execute the following algorithms on output provided by its :ref:`cluster` action:

* ``stratified-random`` - chooses *j* random mementos from each cluster
* ``stratified-systematic`` - chooses every *jth* memento from each cluster
* ``random-cluster`` - randomly chooses *j* clusters from the input and returns their mementos
* ``random-oversample`` - randomly chooses mementos from clusters until those clusters are the same size as the largest cluster
* ``random-undersample`` - randomly chooses mementos from clusters until those clusters are the same size as the smallest cluster

.. _report:

report
------

.. _synthesize:

synthesize
----------
