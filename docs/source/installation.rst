Installation
============

We are in the process of streamlining these installation steps.

Using PIP
---------

1. `Install MongoDB <https://docs.mongodb.com/manual/installation/>`_
2. Clone `this repository <https://github.com/oduwsdl/hypercane>`_
3. Change into the cloned directory
4. Type ``pip install --upgrade pip``
5. Type ``pip install -r requirements.txt``
6. Type ``python -m spacy download en_core_web_sm`` to download a language pipeline for entity detection - (Note: attempts to automated this step inside ``setup.py`` have not been successful)
7. Type ``pip install . --use-feature=in-tree-build``
8. (optional) To sample with the ``dsa1`` algorithm originally developed by AlNoamany et al. in 2017, you will need to install a `Memento Damage <https://github.com/oduwsdl/web-memento-damage>`_ server.

This grants access to the ``hc`` command which provides the functionality of Hypercane.

Using Docker
------------

The software is still volatile, so you will need to build your own docker image.

1. Create a working directory in the terminal and change into it
2. Download `this docker-compose file into that directory <https://raw.githubusercontent.com/oduwsdl/hypercane/master/docker-compose.yml>`_
3. Run ``docker-compose run hypercane hc --help`` to print the help statement

This may take a while to download and build necessary docker images. Once done, it will run the caching server and connect to the hypercane container. From that prompt, you'll be able to execute the ``hc`` command.
