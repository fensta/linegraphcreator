"""
Creates the line graph as described in 'Line graphs, link partitions, and overlapping communities' by Evans et al. But only equation (11) is implemented to transform a directed, unweighted graph
into a weighted, directed line graph on which any arbitrary community detection algorithm can be applied. A line graph L(G) is a projection of the normal graph G. G's edges are
transformed into nodes and the nodes into edges. Overlap is incorporated by construction in the line graph when nodes of L(G) are clustered into communities, actually the edges are 
clustered. Implementation details regarding the directed case of Evans et al. can be found in 'Line Graphs of Weighted Networks for Overlapping Communities'.

This version is optimized in that only all nodes of the graph will be checked sequentially and all possible combinations of the in- and out-degrees of this node will be present in
the line graph.

@author: Stefan Raebiger
"""

import csv
import os
import time
import argparse

def read_txt(path, delim, is_directed=True):
    """
    
    Reads an edge list from <path> in txt format
    
    Parameters:
    -----------
    path: Path to raw text file to be read which contains the edge list.
    delim: Delimiter to be used for distinguishing between values in the file.
    is_directed: True if graph is directed, otherwise False.
    
    Returns: Set of users, Dictionary of incoming edges{target1: set(src1, src2)} and dictionary of outgoing edges {src1: set(target1, target2)}.
    
    """
    data = []
    with open(path,"r") as f:
        data_temp = f.readlines()
        for line in data_temp:
            line = line.rstrip()
            data.append(line.split(delim))
            
    users, out_edges, in_edges = create_input(data, is_directed=is_directed)
    return users, out_edges, in_edges   
        

def create_input(data,is_directed):
    """
    
    Creates the input data required for running incremental line graph creator.
    
    Parameters:
    -----------
    data: Data used as input.
    is_directed: True if graph is directed, otherwise False.
    
    Returns: Set of users, Dictionary of incoming edges{target1: set(src1, src2)} and dictionary of outgoing edges {src1: set(target1, target2)}.
    
    """
    in_edges = {} # {src1: set(target1, target2)}
    out_edges = {} # {target1: set(src1, src2)}
    users = set()
    for line in data:
        s,t = int(line[0]),int(line[1])
        users.add(s)
        users.add(t)
        if is_directed:
            if not s in out_edges:
                out_edges[s] = set()
            out_edges[s].add(t)
            
            if not t in in_edges:
                in_edges[t] = set()
            in_edges[t].add(s)    
        else:
            if not s in out_edges:
                out_edges[s] = set()
            out_edges[s].add(t)
            
            if not t in out_edges:
                out_edges[t] = set()
            out_edges[t].add(s)
            
            if not t in in_edges:
                in_edges[t] = set()
            in_edges[t].add(s)
            
            if not s in in_edges:
                in_edges[s] = set()
            in_edges[s].add(t)

    return users, out_edges, in_edges


def read_csv(path, delim, is_directed=True):
    """
    
    Reads an edge list from <path> in txt format
    
    Parameters:
    -----------
    path: Path to csv file to be read which contains the edge list.
    delim: Delimiter to be used for distinguishing between values in the file.
    is_directed: True if graph is directed, otherwise False.
    
    Returns: Set of users, Dictionary of incoming edges{target1: set(src1, src2)} and dictionary of outgoing edges {src1: set(target1, target2)}.
    
    """
    data = csv.reader(open(path,'rb'),delimiter=delim,quotechar='|')
    users, out_edges, in_edges = create_input(data, is_directed=is_directed)
    return users, out_edges, in_edges


def read_edge_list(path, ext, delim, is_directed=True): 
    """
    
    Reads an edge list from <path> in csv or txt format.
    
    Parameters:
    -----------
    path: Path to csv file to be read which contains the edge list.
    delim: Delimiter to be used for distinguishing between values in the file. 
    is_directed: True if graph is directed, otherwise False.
    ext: Input file extension. Permissible values are "csv" for csv files and "txt" for raw files.
    
    Returns: List of tuples of edge pairs, e.g. [(src1,dst1), (src2,dst2)]. Secondly a dictionary containing source edge as key and target as value
    
    """
    if ext == "csv":
        return read_csv(path, delim=delim, is_directed=is_directed)
    else:
        return read_txt(path, delim=delim, is_directed=is_directed)


def write_data(data, dst):
    """
    
    Writes the data of L(G) to output file under <dst>.
    
    Parameters:
    -----------
    data: Dictionary
    dst: Destination where file should be saved.
    
    """
    with open(dst,"w") as f:
        for node,com in data.iteritems():
            f.write(str(node) + ":" + str(com) + "\n")


def renumber_edges(dictionary, edge):
    """
    Renumbers the edge and inserts new value into <dictionary>. Renumbering starts from 0 and ends with n.
    
    Parameters:
    -----------
    dictionary: Dictionary containing all renumbered edges
    edge: Edge to be renumbered.
    
    Returns: Renumbered edge.
    
    """
    edge = edge[0]
    if not edge in dictionary:
        dictionary[edge] = len(dictionary)
    return dictionary[edge] 


def incremental_lg(users, in_edges, out_edges, write_to_disk_after, mapping, is_verbose, outp=None, is_directed=True, is_weighted=False):
    """
    
    Implements the actual algorithm. It needs the edge list of G as input and for more efficient processing the dictionary of edges is also given as input to create line graph L(G). 
    L(G) transforms in general edges of original graph G into nodes in L(G) and nodes from G into edges in L(G). It yields exactly the same results as the original C++ version (https://sites.google.com/site/linegraphs/).
    This function also numbers edges in the output from 0...number of edges - 1. The original edge IDs can easily be calculated since each vertex v refers to the v-th edge in <edges>.
    For instance, given edges = [(1,2),(2,3),(3,1)] then vertex 0 in the output file refers to edge (1,2), 1 to (2,3) and 2 to (3,1). Hence, v could also be interpreted as index of the edge list.
    
    Parameters:
    -----------
    users: Users in graph.
    in_edges: Dictionary of incoming edges per user. {target1: set(source1, source2)}
    out_edges: Dictionary of outgoing edges per user. {source1: set(target1, target2)}
    outp: Path under which the results, L(G), should be saved. If not specified, it will be stored by default in the same directory as the script in a file called "line_graph.txt".
    write_to_disk_after: Number of data entries (edge pair and corresponding weight) that should be cached before writing them in one pass to the disk. This accelerates the algorithm significantly and can be tuned for each dataset. The only restriction is your RAM usage. 
                 If a memory error is thrown, reduce this value. The larger the value, the higher the RAM usage, but also the faster the algorithm. Writing to disk is a bottleneck.
                 Default value is 10000000 meaning that every 10000000 entries the data  will be written to the output file.
    mapping: File name that should be used for the mapping of the edges of G to the nodes in L(G).
    is_verbose: Produce more output for the user regarding the progress of the graph transformation.
    is_directed: True, if graph G is directed, False otherwise. Set to True by default.
    is_weighted: True, if graph G is weighted, otherwise False. Set to False by default.
    
    Basic Idea:
    -----------
    Consider the edges as a stream and iterate over them one by one. For each combination of edge pairs it has to be checked whether they share a node. In case they do, they would
    be connected in the line graph L(G) if the shared node has a degree > 1 (in the undirected case) or an in-degree > 0 and out-degree > 0 (in directed case). In the directed case two
    edges e1 and e2 in G share a node n_shared if e1(i,n_shared) and e2(n_shared,j) where i and j are also nodes in G. In other words, if the shared node has one of the two edges as incoming edge and the other one as outgoing edge, it is considered a shared node. 
    In the corresponding line graph L(G) e1 and e2 would be nodes connected by the edge n_shared.
    Thus, the algorithm computes the weight w the edge in L(G) (= n_shared) would receive. 
    Finally, the edge pair and corresponding weight are stored in a file.
    
    In the directed case only incoming edges of a node are considered as being incident/related and likewise, w is computed based on the out-degree of the respective node.
    Furthermore, w is computed by w(shared_node) = 1 / k_out(shared_node) where shared_node is the node that is shared between both edges.
    In the undirected case w is computed as follows: w(shared_node) = 1 / (k(shared_node) - 1).
    
    However, so far only unweighted, directed graphs can be transformed into weighted, directed line graphs according to equation 11 from 'Line graphs, link partitions, and overlapping communities'.
    Any other possible case (weighted/unweighted and undirected, weighted and directed) isn't implemented yet.
    
    """
    output_path = None
    if outp != None:
        output_path = outp
    else:
        base_dir = os.path.realpath(__file__).rsplit(os.sep, 1)[0] # Searches from right to left
        #print "base_dir",base_dir
        output_path = os.path.join(base_dir, "line_graph_test_optimized.txt") # File stored in same directory as incremental_line_graph_creator.py called "line_graph.txt"
        #print "default output path",output_path
    
    # v-th edge in G is vertex v in L(G)
    #vertices_in_lg = dict((v,edges[v]) for v in xrange(len(edges)))
    #renumbered_edges_in_g = dict((edge,v) for v,edge in vertices_in_lg.iteritems()) # Renumbering compresses output file significantly
    
    renumbered_edges_in_g = {}
    #print "vertices in L(G)",vertices_in_lg
    #print "edges in G:",renumbered_edge_in_g
        
    # Case: G is directed and unweighted
    if is_directed and not is_weighted:
        print "users",len(users)
        print "outgoing edges:",len(out_edges),"incoming edges:",len(in_edges)
        in_degrees = dict((n,len(incident)) for n,incident in in_edges.iteritems() if len(incident) > 0) # Stores in-degrees of all nodes which is simply the number of incoming nodes, but only if degree >0
        out_degrees = dict((n,len(out)) for n,out in out_edges.iteritems() if len(out) > 0) # Stores out-degress of all nodes which is simply the number of outgoing nodes, but only if degree >0 
        possible_edge_pair_combinations = 2 * sum([in_degrees[n] * out_degrees[n] for n in out_degrees if n in in_degrees])
        if is_verbose:
            print "Maximal number of edges in L(G):",possible_edge_pair_combinations
            #print "Maximal number of vertices in L(G)",len(dict(in_edges.iteritems() + out_edges.iteritems()))
        lines = []
        first_write = True # Determine whether to create a new file or to append
        
        # Loop over all users in graph
        start = time.time()
        edges_in_lg = 0
        for count, user in enumerate(users):
            # Make sure that there is at least one incoming and outgoing edge, otherwise no node will exist in L(G)
            if user in in_edges and user in out_edges:
                # Now compute for all edges that share <user> as node ( namely all incoming nodes of <user> with all outgoing nodes of <user>) their respective weight in L(G) as these
                # edge pairs will exist as nodes in L(G) connected by the edge <user> with the weight 1/out-degree of <user>
                shared_node = user
                
                for in_node in in_edges[user]:
                    for out_node in out_edges[user]:
                        w = 1.0 / (out_degrees[shared_node])
                        lines.append(str(renumber_edges(renumbered_edges_in_g, [(in_node, shared_node)])) + " " + str(renumber_edges(renumbered_edges_in_g, [shared_node, out_node])) + " " + str(w) + "\n")
                        edges_in_lg += 1
                    if len(lines) > write_to_disk_after: # Write chunks instead of each single line
                        write_lg(lines, output_path, init=first_write)
                        first_write = False
                        lines = [] # Reset list and empty RAM
            if count % 100 == 0 and count > 0:
                end = time.time()
                if is_verbose:
                    print "it took",end - start,"s to process",count,"users"
                start = end
                
        if len(lines) > 0: # Write remaining data
            write_lg(lines, output_path, init=first_write)
        
        print "Edges in L(G)",edges_in_lg
        # Store original mapping of edges by also writing vertices_in_lg to file! -> but we want the new edge name to be key instead of value, so we switch key, value pairs 
        dst = os.path.dirname(outp)
        renumbered_edges_in_g = {new_edge_no: edge for edge, new_edge_no in renumbered_edges_in_g.iteritems()}
        write_data(renumbered_edges_in_g, os.path.join(dst, mapping + ".dat"))
            
        print "#######################################"
        print "# Projected G successfully onto L(G)! #"
        print "#######################################"
    else:
        raise NotImplementedError("Not implemented yet")
    

def write_lg(data, dst, init=False):
    """
    
    Writes the data of L(G) to output file under <dst>.
    
    Parameters:
    -----------
    data: Edge pair (source,target) in L(G) followed by the corresponding weight w separated by a whitespace. Source is an edge in G, likewise target is. The edge weight is in G the shared node between both edges.
    dst: Destination where file should be saved.
    init: Indicates whether to append to an existing file or rather to create a new one. False means to append and True to create a new file. Default is "False".
    
    """
    if init: # New file
        with open(dst,"w") as f:
            for l in data:
                f.write(l)
    else:    # Append to file
        with open(dst,"a") as f:
            for l in data:
                f.write(l)
            

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description="Transform a graph into its corresponding line graph")
    parser.add_argument("-i", "--input", help="Specify input file for edge list", required=True)
    parser.add_argument("-o", "--output", help="Specify the output file under which results should be stored", required=True)
    parser.add_argument("-d", "--delimiter", help="Specify the delimiter separating the data in a single line of your input file.", required=True)
    parser.add_argument("-csv", "--csv", help="Interpret the input file as .csv file", action="store_true")
    parser.add_argument("-b", "--buffer", type=int, help="Specify after how many nodes the result should be stored in file. Larger values increase speed of algorithm, but use up more memory. Default is 1000000", default=1000000)
    parser.add_argument("-m", "--mapping", help="Type in the file name you desire for the mapping from the original graph to the line graph. Default is 'edge_mapping'", default="edge_mapping")
    parser.add_argument("-v", "--verbose", help="Print out more information about the progress of the graph transformation, but it might slowdown the algorithm. It is deactivated by default.", action="store_true")
    # parser.add_argument("-d", "--directed"), help="Interpret input file as directed graph", action="store_true") # Not implemented yet
    # parser.add_argument("-s", "--selflinks", help="Allow self-links to be present in the input graph", action="store_true") # Not implemented yet, respectively not tested
    args = parser.parse_args()
    
    extension = "txt"
    if args.csv:
        extension = "csv"

    users, out_edges, in_edges = read_edge_list(args.input, extension, args.delimiter)
    incremental_lg(users, out_edges, in_edges, args.buffer, args.mapping, args.verbose, outp=args.output)