Installation
============

We will update the installation soon.

Using PIP
---------

1. Install MongoDB
2. Clone `this repository <https://github.com/oduwsdl/hypercane>`_
3. Change into the cloned directory
4. type pip install .

This grants access to the ``hc`` command which provides the functionality of Hypercane.

Using Docker
------------

The software is still volatile, so you will need to build your own docker image.

1. Clone this repository
2. type docker build -t hypercane:dev .
3. run docker-compose run hypercane bash

From that prompt, you'll be able to execute the ``hc`` command.