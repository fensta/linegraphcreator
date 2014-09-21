LineGraphCreator
================
Transforms a graph into a corresponding line graph.
It modifies the algorithm introduced by Evans and Lambiotte [[1](http://arxiv.org/pdf/0903.2181.pdf)] in that it requires a constant amount of memory for the transformation  - opposed to the original implementation (which stores the entire line graph in memory) - by storing the resulting line graph chunkwise in a file. Thus, the transformation takes a bit longer, but allows to process larger graphs (> 10000 nodes) without requiring a lot of memory.
The modification was developed for our paper: "XXX".


Usage
=====
`line_graph_creator.py` can be executed via the command line. So far, the following arguments are supported:

1. Required arguments:
  * -i [--input] - Defines the path to the input file.
  * -o [--output] - Defines the path to the output file for storing the line graph.
  * -d [--delimiter] - Specify the delimiter used in the input file for separating the values in a row.
2. Optional arguments:
  * -h [--help] - Show help and further explanation regarding the arguments.
  * -csv [--csv] - Interpret input file as .csv file instead of raw text. Default: raw text
  * -b [--buffer] - Determines how many edges of the line graph should be cached before writing them to the output file. The larger the value, the faster is the graph processed. Default: Store line graph every 1000000 newly created edges. This argument determines how much memory the algorithm is allowed to consume.
  * -m [--mapping] - Specify the file name of the mapping from the nodes in the line graph to the edges in the original graph. Otherwise the mapping is named 'edge_mapping' and stored in the same location as the output file.
  * -v [--verbose] - Yields more output to the user regarding the progress of the graph transformation. Note that this might slow down the transformation significantly. By default it is deactivated.

where the former two arguments are mandatory.

Examples:

`python LineGraphCreator -i /foo/bar/input.txt -o /baz/my_output.txt -d " " -b 200`

In this case the file input.txt is read as edge list and the whitespace delimiter is used to separate entries in each line. Once every 200 edges the newly created edges are appended to my_output.txt.
 
`python LineGraphCreator -i /foo/bar/input.csv -o /baz/my_output.txt csv -m bruz - d "."`

This time the file input.csv is read as a csv file and after applying the algorithm, the results are stored in 'my_output.txt'. This time every 1000000 edges all of them are stored in 'my_output'. The mapping is renamed to 'bruz' and the delimiter in the input file is a dot.


Input format
============
The algorithm expects as input the graph described as edge list and accepts two different formats for that purpose:

1. csv - each line contains a single edge represented by a pair of nodes. For instance "1,2" describes the edge from node 1 to node 2.
2. raw text - each line contains a single edge, in which both nodes are separated by a delimiter (that can be passed as argument).


Output format
=============
The algorithm outputs the line graph in raw text as edge list in the specified location.
Each line in the output represents an edge in the line graph. Hence, at first the source node, then the target node of the edge and also the edge weight are stored per line. They are separated by a whitespace.


How to find out which edge in the line graph corresponds to which node in the original graph?
=============================================================================================
Note that the edges in the line graph were renumbered, so it is **NOT** possible to map them directly back to the original graph. Instead, a file containing the mapping is created in the same location as the line graph. In this file, each entry describes a mapping of a node in the line graph to its corresponding edge in the original graph. Thus, an entry looks like this: 

`<Node in line graph>: (<Source node in original graph>, <Target node in original graph>)`

For instance, the entry "0: (1,2)" means the edge from node 1 to 2 in the orginal graph maps to node 0 in the line graph.


Next Milestones
===========
* allow to process undirected graphs
* let users decide whether self-links are allowed or not in the original graph and the resulting line graph


Citations
=========
In case you want to use this code in your research paper, please cite our paper "XXX". Thanks!


References
==========
[1] - Evans, T. S., & Lambiotte, R. (2009). Line graphs, link partitions, and overlapping communities. Physical Review E, 80(1), 016105.
