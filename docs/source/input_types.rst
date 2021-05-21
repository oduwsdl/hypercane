Input Types
============

Hypercane supports several types of input across all of its commands. An input type is supplied with the ``-i`` argument.  For each input type, the ``-a`` argument specifies the collection identifier or the file containing the input. In the following example, we sample 28 mementos from collection 13742, specified by ``-a``, archived by `Trove <https://trove.nla.gov.au/>`_, specified by ``-i``:

.. code-block:: 

    hc sample true-random -k 28 -i trove -a 13742 -o random-sample.tsv

All Hypercane commands accept the following values for the ``-i`` argument to specify the type of input to be provided in the ``-a`` argument:

* ``archiveit`` -  the input is an `Archive-It <https://archive-it.org/>`_  collection identifier
* ``trove`` -  the input is a `Trove <https://trove.nla.gov.au/>`_ collection identifier
* ``pandora-collection`` -  the input is a `Pandora <http://pandora.nla.gov.au/>`_ collection identifier
* ``pandora-subject`` -  the input is a `Pandora <http://pandora.nla.gov.au/>`_ subject identifier
* ``mementos`` -  the input is a tab-separated file containing a list of mementos identified by their URI-Ms
* ``timemaps`` -  the input is a tab-separated file containing a list of TimeMaps identified by their URI-Ts
* ``original-resources`` -  the input is a tab-separated file containing a list of live web resources identified by their URI-Rs

Below are some examples of using the different input types with different Hypercane commands.

1. Randomly sample 10 mementos from Archive-It collection 8788

.. code-block::

    hc sample true-random -i archiveit -a 8788 -o seed-output-file.txt -k 10

2. Use the DSA1 algorithm to sample mementos from the TimeMaps found in the file timemaps.tsv

.. code-block::

    hc sample dsa1 -i timemaps -a timemaps.tsv -o dsa1-sample.tsv

3. Generate an entity report for the mementos in the file memento-file

.. code-block::

    hc report entities -i mementos -a memento-file.tsv -o entity-report.json

4. Generate a metadata report for Trove collection 13742

.. code-block::

    hc report metadata -i trove -a 13742 -o 13742-metadata.json

5. Synthesize a directory containing mementos from the TimeMaps in timemap-file.tsv

.. code-block::

    hc synthesize files -i timemaps -a timemap-file.tsv -o output-directory

6. Save the URI-Ms of all mementos in Pandora Collection 10121 into the file mementos.tsv

.. code-block::

    hc identify mementos -i pandora-collection -a 10121 -o mementos.tsv
