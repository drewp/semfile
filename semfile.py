
"""
related:

http://crschmidt.net/semweb/wordnet/sparql

http://xmlns.com/foaf/0.1/

http://www.kanzaki.com/test/exif2rdf?u=http://kanzaki.com/works/2003/imagedesc/0817.jpg&xsl=on

http://dev.w3.org/cvsweb/~checkout~/java/classes/org/w3c/rdf/examples/ARPServlet.java?rev=1.79&content-type=text/plain
the validator's graphviz interface source code

http://esw.w3.org/topic/ImageDescription

"""


from rdflib import Graph, RDF, Namespace

def read_or_create_graph(graph_filename):
    # someday this will probably return a proxy to a shared, networked graph
    graph = Graph()
    try:
        graph.load(graph_filename)
    except OSError, e:
        print "starting new graph at %r" % graph_filename
    return graph

graph_filename = "tags.rdf"

def all_documents(graph):
    # this is hardly correct. what i want is all S with (S, RDF.type,
    # foaf:Document); but including any other types that are
    # subClassOf foaf:Document

    ## [06:12:15] <eikeon> This is one way:
    ## [06:12:16] <eikeon> allPeople = set()
    ## [06:12:16] <eikeon> for personType in store.transitive_subjects(RDFS.subClassOf, TERROR.Person):
    ## [06:12:16] <eikeon>     for person in store.subjects(RDF.type, personType):
    ## [06:12:16] <eikeon>         allPeople.add(person)
    
    return graph.subjects(predicate=RDF.type)

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
# these are like http://technorati.com/tag/ tags
TAG = Namespace("http://photo.bigasterisk.com/tag/")
DC = Namespace("http://purl.org/dc/terms/")
