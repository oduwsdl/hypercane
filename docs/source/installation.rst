Installation
============

We are in the process of streamlining these installation steps.

Using PIP
---------

1. Install MongoDB
2. Clone `this repository <https://github.com/oduwsdl/hypercane>`_
3. Change into the cloned directory
4. Type ``pip install .``

This grants access to the ``hc`` command which provides the functionality of Hypercane.

Using Docker
------------

The software is still volatile, so you will need to build your own docker image.

1. Clone `this repository <https://github.com/oduwsdl/hypercane>`_
2. Change into the cloned directory
3. Run `docker-compose run hypercane`

This may take a while to download and build necessary docker images.
Once done, it will run the caching server and connect to the hypercane container.
From that prompt, you'll be able to execute the ``hc`` command.
