LineGraphCreator
================

Transforms a graph into a corresponding line graph.
It modifies the algorithm introduced by Evans and Lambiotte [1] in that it requires a constant amount of memory for the transformation  - opposed to the original implementation (which stores the entire line graph in memory) - by storing the resulting line graph chunkwise in a file. Thus, the transformation takes a bit longer, but allows to process larger graphs (> 10000 nodes) without requiring a lot of memory.
The modification was developed for our paper: "XXX".

Usage
=====
It can be executed via the command line. So far, the following arguments are supported:
-i [--input] - defines path to input file.
-o [--output] - defines path to output file for storing the line graph.
-csv [--csv] - interpret input file as .csv file
-b [--buffer] - determines how many chunks of the line graph should be written to file. The larger the value, the faster is                 the graph processed. Default: Store line graph every 1000000 newly created edges. This argument determines                 how much memory the algorithm is allowed to use up.
-d [--delimiter] - in case of raw text as input, pass in the delimiter separating both nodes per line in the input file.                      Default is whitespace.
where the former two arguments are mandatory.

Input format
============
The algorithm expects as input the graph described as edge list and accepts two different formats for that purpose:
(1) csv - each line contains a single edge represented by a pair of nodes. For instance "1,2" describes the edge from node 1 to node 2.
(2) raw text - each line contains a single edge, in which both nodes are separated by a delimiter (that can be passed as argument).

Output format
=============
The algorithm outputs the line graph in raw text as edge list in the specified location.
Each line in the output represents an edge in the line graph. Hence, at first the source node, then the target node of the edge and also the edge weight are stored per line. They are separated by a whitespace.

How to find out which edge in the line graph corresponds to which node in the original graph?
=============================================================================================
Note that the edges in the line graph were renumbered, so it is NOT possible to map them directly back to the original graph. Instead, a file containing the mapping is created in the same location as the line graph. In this file, each entry describes a mapping of a node in the line graph to its corresponding edge in the original graph. Thus, an entry looks like this: 
<Node in line graph>: (<source node in original graph>, <target node in original graph>)
For instance, the entry "0: (1,2)" means the edge from node 1 to 2 in the orginal graph maps to node 0 in the line graph.

Limitations
===========
As of now, the input file is interpreted as directed graph. So far, it is also impossible to adjust whether self-links are allowed or not in the original graph and resulting line graph.

Citations
=========
In case you want to use this code in your research paper, please cite our paper "XXX". Thanks!

References
==========
[1] - Evans, T. S., & Lambiotte, R. (2009). Line graphs, link partitions, and overlapping communities. Physical Review E, 80(1), 016105.
