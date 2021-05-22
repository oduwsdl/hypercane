.. _caching_and_being_nice:

Caching and being nice to web archives
======================================

Hypercane is designed for researchers and storytellers. Hypercane is based on the recognition that web archives are big data. It gives the user the ability to automate the download of many resources from a web archive. We want web archives to remain capable of fulfilling our research needs, especially as big data. To that end, Hypercane tries very hard to be nice to web archives, employing techniques such as caching and honoring HTTP retry requests from the archive. 

**We want Hypercane to be successful and recognize that we would not be here without web archives. If you run a web archive and find that a someone using Hypercane is causing problems for your archive, please** `contact us <https://github.com/oduwsdl/hypercane/issues/new/choose>`_ **so we can work toward a solution.**

Caching with ``-cs``
--------------------

Hypercane stores a cache of all objects it encounters in MongoDB through the requests-cache library. While some commands do not require caching, a number will not execute unless the user specifies a caching database. **This is to protect the web archive from unnecessarily high traffic load and improve performance across Hypercane commands.** Hypercane commands can be executed in any order, meaning that a user may hit the cache numerous times while working with a collecition.

A user specifies the MongoDB database they want to use for caching through the `-cs` argument supplied to any command. For example, to randomly sample all of the mementos in Archive-It collection 694, apply the `-cs` argument like so:

.. code-block:: text

    hc sample true-random -i archiveit -a 694 -o random-mementos.tsv -cs mongodb://localhost/cs694

This ensures that every collection page, TimeMap, memento, and other content is stored in the MongoDB database named *cs694* running on your local machine. This way, running subsequent commands, like the one below, do not need to spend time downloading the same content again, and reuse the content in *cs694*.

.. code-block:: text

    hc score path-depth -i mementos -a random-mementos.tsv -o scored-mementos.tsv -cs mongodb://localhost/cs694



Caching with the ``HC_CACHE_STORAGE`` environment variable
----------------------------------------------------------

So that the user does not need to specify `-cs` every time, they can specify the database cache's URL once via the ``HC_CACHE_STORAGE`` environment variable, like so:

.. code-block:: text

    export HC_CACHE_STORAGE="mongodb://localhost/mycache"

All subsequent Hypercane commands run in the same shell will use this database as their cache. When working with a single collection, this is often the best choice.

.. note::
    `We are evaluating whether or not caching services like Squid might successfully store HTTPS responses sent to Hypercane. <https://github.com/oduwsdl/hypercane/issues/16>`_ Once we make this determination, we may abandon MongoDB in favor of more standardized caching.
