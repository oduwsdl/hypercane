<img src="images/hypercane-logo.png" width="100px">

# Hypercane

Hypercane is a framework for building algorithms for sampling mementos from a web archive collection. Hypercane is the entry point of the [Dark and Stormy Archives (DSA) toolkit](https://oduwsdl.github.io/dsa/). A user can generate samples with Hypercane and then view those samples via the Web Archive Storytelling tool [Raintale](https://oduwsdl.github.io/raintale/), thus allowing the user to automatically summarize a web archive collection as a few small samples visualized as a social media story.

The possibilities with Hypercane do not stop there. Users can employ Hypercane actions to explore a web archive collection through different actions. This README will provide an overview of these actions, but more detailed documentation is forthcoming.

# Installing Hypercane

## Using PIP

1. Install [MongoDB](https://www.mongodb.com/download-center/community)
2. Clone this repository
3. Change into the cloned directory
4. Type `pip install .`
5. We are still working out some dependency issues, thus you will need to type `pip install -r requirements.txt` as a last step

This grants access to the `hc` command which provides the functionality of Hypercane.

## Using Docker

The software is still volatile, so you will need to build your own docker image.

1. Clone this repository
2. Run `docker-compose run hypercane hc --help`

This may take a while to download and build necessary docker images. When successful, `hc` CLI help will be printed.

# Running Hypercane

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

We are working on additional sampling algorithms and options for the advanced actions. Please feel free to submit issues and pull requests at https://github.com/oduwsdl/hypercane
