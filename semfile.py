
from rdflib import Graph

def read_or_create_graph(graph_filename):
    graph = Graph()
    try:
        graph.load(graph_filename)
    except OSError, e:
        print "starting new graph at %r" % graph_filename
    return graph

graph_filename = "tags.rdf"
