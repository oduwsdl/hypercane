Hypercane: Intelligent Samping of Web Archive Collections
=========================================================

.. image:: images/hypercane-logo-alpha-sm.png

What tool can we rely on to automate the selection of mementos for summarizations and other purposes? Hypercane.

Hypercane is a command-line utility for sampling archived web pages (**mementos**) from a web archive collection. Hypercane leverages the `Memento Protocol <https://tools.ietf.org/html/rfc7089>`_ to discover resources in web archives so that a user can sample a subset of documents. With Hypercane a user can do things like search a subset of mementos, produce a sample for automated storytelling, or convert a set of meemnto URLs (URI-Ms) into WARCs for processing with other tools.

The core actions of Hypercane are:

* ``sample`` - for creating a sample of a collection
* ``report`` - for generating a report on collection metadata, named entities, curation behavior, and more
* ``synthesize`` - for generating output for other tools, like `Archives Unleashed Toolkit <https://github.com/archivesunleashed/aut>`_ or `Raintale <https://oduwsdl.github.io/raintale/>`_

To create their own algorithms, Hypercane also supports the following advanced actions:

* ``identify`` - for discovering one Memento object from another
* ``filter`` - for filtering the documents from the input based on some criteria
* ``cluster`` - for clustering the documents from the input based on an algorithm and features
* ``score`` - for scoring the documents from the input based on some scoring function
* ``order`` - for ordering the documents in the input based on some feature

.. toctree::
   :maxdepth: 2

   installation
   core_actions
   advanced_actions
   license
    