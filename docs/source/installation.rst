Installation
============

**Hypercane requires MongoDB for caching. Install MongoDB as appropriate for your environment first. Hypercane will no longer work without a caching database.**

Installing Hypercane on Linux or Unix
-------------------------------------

CentOS 8
~~~~~~~~

If you would like to use the RPM installer for RHEL 8 and CentOS 8 systems:

1. `Install MongoDB for CentOS 8/RHEL 8 <https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-centos-8>`_. MongoDB does not come with the CentOS/RHEL distributions, so you will need to add a new repository to your system.
2. Download the RPM and save it to the Linux server (e.g., hypercane-0.20211022230926-1.el8.x86_64.rpm).
3. Type ``dnf install hypercane-0.20211022230926-1.el8.x86_64.rpm``
4. Type ``systemctl start hypercane-django.service``

.. Ubuntu 21.04
.. ------------

.. If you would like to use the DEB installer for Ubuntu 21.04 systems:

.. 1. `Install MongoDB for Ubuntu 21.04 <https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/>`_. MongoDB does not come with the Ubuntu distribution, so you will need to add a new repository to your system.
.. 2. Download the DEB and save it to the Linux server (e.g., hypercane-0.20211022230926.deb).
.. 3. Type ``apt-get install ./hypercane-0.20211022230926.deb``
.. 4. Type ``systemctl start hypercane-django.service``

Using the self-extracting installer on a generic Unix/Linux system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This installer only works on Unix and Linux.

1. Install MongoDB on a system accessible to the server chosen for Hypercane and record the URL for this MonboDB install. Hypercane will no longer work without a caching database.
2. Download the latest release of Hypercane
3. Run ``./install-hypercane.sh -- --mongodb-url [MONGODB_URL]`` where MONGODB_URL is the URL recorded in step 1

Hypercane comes with a web user interface (WUI) providing a more user-friendly method of executing Hypercane. The WUI is a web application. Starting this web application depends on your Unix/Linux system.

To start the Hypercane WUI on a generic Unix system:
``/opt/hypercane/start-hypercane-wui.sh``

Installing Hypercane with PIP
-----------------------------

1. `Install MongoDB <https://docs.mongodb.com/manual/installation/>`_
2. Clone `this repository <https://github.com/oduwsdl/hypercane>`_
3. Change into the cloned directory
4. Type ``pip install --upgrade pip``
5. Type ``pip install -r requirements.txt``
6. Type ``python -m spacy download en_core_web_sm`` to download a language pipeline for entity detection - (Note: attempts to automated this step inside ``setup.py`` have not been successful)
7. Type ``pip install . --use-feature=in-tree-build``
8. (optional) To sample with the ``dsa1`` algorithm originally developed by AlNoamany et al. in 2017, you will need to install a `Memento Damage <https://github.com/oduwsdl/web-memento-damage>`_ server.

This grants access to the ``hc`` command which provides the functionality of Hypercane.

Improving the Hypercane WUI's Performance
-----------------------------------------

Configuring the Hypercane WUI for Postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


By default, the Hypercane WUI uses SQLite, which does not perform well for multiple users logging into the same Hypercane WUI system. For optimial user experience, the Hypercane WUI can be connected to a Postgres database.

1. Install Postgres on a system accessible to the server that the Hypercane WUI is running on. Record that system's host and the port Postgres is running on -- the default port is 5432.
2. Log into postgres and create a database with postgres for Hypercane.
3. Create a user and password.
4. Grant all privileges on the database from step 2 in step 3.
5. Run ``/opt/hypercane/hypercane-gui/set-hypercane-database.sh --dbuser [DBUSER] --dbname [DBNAME] --dbhost [DBHOST] --dbport [DBPORT]`` -- with DBUSER created from step 3, DBNAME replaced by the database you created in step 2, DBHOST and DBPORT recorded from step 1. The script will prompt you for the password.
6. Restart Hypercane as appropriate for your system.

Configuring the Hypercane WUI for RabbitMQ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For optimal process control, the Hypercane WUI can use a queueing service like RabbitMQ.

1. Install RabbitMQ on a system accessible to the server that the Hypercane WUI is running on. Record that system's hostname and the port that RabbitMQ is running on -- the default port is 5672.
2. Run ``/opt/hypercane/hypercane-gui/set-hypercane-queueing-service.sh --amqp-url amqp://[HOST]:[PORT]/`` where HOST is the host of the RabbitMQ server and PORT is its port
