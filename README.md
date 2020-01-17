<img src="images/hypercane-logo.png" width="100px">

# Hypercane

Hypercane is a framework for building algorithms for sampling mementos from a web archive collection. Hypercane is the entry point of the [Dark and Stormy Archives (DSA) toolkit](https://oduwsdl.github.io/dsa/). A user can generate samples with Hypercane and then view those samples via the Web Archive Storytelling tool [Raintale](https://oduwsdl.github.io/raintale/), thus allowing the user to automatically summarize a web archive collection as a few small samples visualized as a social media story.

The possibilities with Hypercane do not stop there. Users can employ Hypercane actions to explore a web archive collection through different actions. This README will provide an overview of these actions, but more detailed documentation is forthcoming.

# Installing Hypercane

1. Clone this repository
2. change into the cloned directory
3. type `pip install .`

This grants access to the `hc` command which provides the functionality of Hypercane.

# Running Hypercane

Hypercane allows you to perform **actions** on web archive collections, TimeMaps, or lists of Mementos.

For example, the following `sample` action executes the `random` command to randomly sample mementos from the TimeMaps supplied by `timemap-file.txt` and writes the URI-Ms to `random-mementos.txt`:
```
hc sample random -i timemaps=timemap-file.txt -o random-mementos.txt
```

At the moment, the following actions are supported:
* `sample` - generate a sample from the collection with various commands, some of the commands may execute various `reduce`, `cluster`, `rank`, and `order` actions
* `identify` - produce a list of identifiers (URIs) from the collection based on the input, the different commands indicate the type of web resource desired
* `report` - generate a report on the collection according to various commands, different commands provide information on collection metadata or provide statistics on the collection
* `reduce` - reduce the given collection according to the criteria specified by the given command
* `cluster` - group the documents identified from the input into clusters, different commands provide different clustering algorithms
* `rank` - rank the mementos from the input based on the command issued
* `order` - order the mementos from the input based on the command issued

To discover the list of commands associated with an action, use the `--help` command-line option. For example, to discover the commands associated with the `reduce` action, type `hc reduce --help`.
