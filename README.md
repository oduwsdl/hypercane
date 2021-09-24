<img src="images/hypercane-logo.png" width="100px">

# Hypercane

Hypercane is a framework for building algorithms for sampling mementos from a web archive collection. Hypercane is the entry point of the [Dark and Stormy Archives (DSA) toolkit](https://oduwsdl.github.io/dsa/). A user can generate samples with Hypercane and then view those samples via the Web Archive Storytelling tool [Raintale](https://oduwsdl.github.io/raintale/), thus allowing the user to automatically summarize a web archive collection as a few small samples visualized as a social media story.

The possibilities with Hypercane do not stop there. Users can employ Hypercane actions to explore a web archive collection through different actions. This README will provide an overview of these actions, but more detailed documentation is forthcoming.

# Installing Hypercane

## Using PIP

1. Install [MongoDB](https://www.mongodb.com/download-center/community)
2. Clone this repository
3. Change into the cloned directory
4. Type `pip install --upgrade pip` because this next step only works with the latest version of `pip`
5. Type `pip install -r requirements.txt` to ensure that you install the correct dependency library versions
6. Type `python -m spacy download en_core_web_sm` to download a language pipeline for entity detection - (Note: attempts to automated this step inside `setup.py` have not been successful)
7. Type `pip install . --use-feature=in-tree-build`

This grants access to the `hc` command which provides the functionality of Hypercane.

## Using Docker

The software is still volatile, so you will need to build your own docker image.

1. Clone this repository
2. Change into the cloned directory
3. Run `docker-compose run hypercane hc --help`

This may take a while to download and build necessary docker images. When successful, `hc` CLI help will be printed.

## Using the self-extracting installer on a Unix/Linux system

This installer only works on Unix and Linux.

1. Install MongoDB on a system accessible to the server chosen for Hypercane and record the URL for this MonboDB install. Hypercane will no longer work without a caching database.
2. Download the latest release of Hypercane
3. Run `./install-hypercane.sh --mongodb-url [MONGODB_URL]` where MONGODB_URL is the URL recorded in step 1

### Hypercane WUI

Hypercane comes with a web user interface (WUI) providing a more user-friendly method of executing Hypercane. The WUI is a web application. Starting this web application depends on your Unix/Linux system.

To start the Hypercane WUI on a generic Unix system:
`/opt/hypercane/start-hypercane-wui.sh`

#### Configuring the Hypercane WUI for Postgres

By default, the Hypercane WUI uses SQLite, which does not perform well for multiple users logging into the same Hypercane WUI system. For optimial user experience, the Hypercane WUI can be connected to a Postgres database.

1. Install Postgres on a system accessible to the server that the Hypercane WUI is running on. Record that system's host and the port Postgres is running on -- the default port is 5432.
2. Log into postgres and create a database with postgres for Hypercane.
3. Create a user and password.
4. Grant all privileges on the database from step 2 in step 3.
5. Run `/opt/hypercane/hypercane-gui/set-hypercane-database.sh --dbuser [DBUSER] --dbname [DBNAME] --dbhost [DBHOST] --dbport [DBPORT]` -- with DBUSER created from step 3, DBNAME replaced by the database you created in step 2, DBHOST and DBPORT recorded from step 1. The script will prompt you for the password.
6. Restart Hypercane as appropriate for your system.

#### Configuring the Hypercane WUI for RabbitMQ

For optimal process control, the Hypercane WUI can use a queueing service like RabbitMQ.

1. Install RabbitMQ on a system accessible to the server that the Hypercane WUI is running on. Record that system's hostname and the port that RabbitMQ is running on -- the default port is 5672.
2. Run `/opt/hypercane/hypercane-gui/set-hypercane-queueing-service.sh --amqp-url amqp://[HOST]:[PORT]/` where HOST is the host of the RabbitMQ server and PORT is its port

# Running the Hypercane CLI

Hypercane allows you to perform **actions** on web archive collections, TimeMaps, or lists of Mementos.

For example, the following `sample` action executes the `random` command to randomly sample mementos from the TimeMaps supplied by `timemap-file.txt` and writes the URI-Ms to `random-mementos.txt`:
```
hc sample true-random -i timemaps -a timemap-file.txt -o random-mementos.txt
```

At the moment, the following actions are supported:
* `sample` - generate a sample from the collection with various commands, some of the commands may execute various `filter`, `cluster`, `score`, and `order` actions
* `report` - generate a report on the collection according to various commands, different commands provide information on collection metadata or provide statistics on the collection
* `synthesize` - sythesize a web archive collection into the a directory containing files, such as warcs or files
* `identify` - produce a list of identifiers (URIs) from the collection based on the input, the different commands indicate the type of web resource desired
* `filter` - filter the given collection according to the criteria specified by the given command
* `cluster` - group the documents identified from the input into clusters, different commands provide different clustering algorithms
* `score` - score the mementos from the input based on the command issued
* `order` - order the mementos from the input based on the command issued

To discover the list of commands associated with an action, use the `--help` command-line option. For example, to discover the commands associated with the `filter` action, type `hc filter --help`.

## Running Hypercane with Docker Compose

1. Build the software as specified in the **Installing Hypercane - Using Docker** subsection above
2. Create a working directory for your project
3. Copy `docker-compose.yml` into your working directory
4. Type `docker-compose run hypercane`
5. Run your desired commands, output will appear within your working directory
6. When done, exit from the hypercane container by running `exit`
7. To stop and remove all the services (such as the cache), run `docker-compose down`

# The Future of Hypercane

We are working on additional sampling algorithms and options for the advanced actions. Please feel free to submit issues and pull requests at https://github.com/oduwsdl/hypercane.
