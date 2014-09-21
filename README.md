linegraphcreator
================

Transforms a graph into a corresponding line graph.
It modifies the algorithm introduced by Evans and Lambiotte [1] in that it requires a constant amount of memory for the transformation  - opposed to the original implementation (which stores the entire line graph in memory) - by storing the resulting line graph chunkwise in a file. Thus, the transformation takes a bit longer, but allows to process larger graphs (> 10000 nodes) without requiring a lot of memory.

It can be executed via the command line. So far, the following arguments are supported:
-i [--input] - defines path to input file.
-o [--output] - defines path to output file for storing the line graph.
-csv [--csv] - interpret input file as .csv file
-b [--buffer] - determines how many chunks of the line graph should be written to file. The larger the value, the faster is                 the graph processed.
where the former two arguments are mandatory.

Input format
============
The algorithm accepts two formats:

[1] - Evans, T. S., & Lambiotte, R. (2009). Line graphs, link partitions, and overlapping communities. Physical Review E, 80(1), 016105.
