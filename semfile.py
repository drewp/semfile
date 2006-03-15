
"""
related:

http://crschmidt.net/semweb/wordnet/sparql

http://xmlns.com/foaf/0.1/

http://www.kanzaki.com/test/exif2rdf?u=http://kanzaki.com/works/2003/imagedesc/0817.jpg&xsl=on

http://dev.w3.org/cvsweb/~checkout~/java/classes/org/w3c/rdf/examples/ARPServlet.java?rev=1.79&content-type=text/plain
the validator's graphviz interface source code

http://esw.w3.org/topic/ImageDescription


todo:
sync tags into beagle for searching

"""

import socket, os, mimetypes
from rdflib import Graph, RDF, Namespace, URIRef
from twisted.python.util import sibpath

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
# these are like http://technorati.com/tag/ tags
TAG = Namespace("http://semfile.bigasterisk.com/tag#")
DC = Namespace("http://purl.org/dc/terms/")


graph_filename = os.getenv("SEMFILE_TAGS", sibpath(__file__, "tags.rdf"))

def read_or_create_graph(tags=None):
    # someday this will probably return a proxy to a shared, networked graph
    graph = Graph()
    try:
        graph.load(graph_filename)
    except OSError, e:
        print "starting new graph at %r" % graph_filename
    return graph

def close_graph(graph):
    graph.serialize(graph_filename)


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

def uriForFile(path):
    host = socket.getfqdn()
    if "." not in host:
        raise ValueError("set your FQDN to be FQ (maybe in /etc/hosts)")
    return URIRef("file://%s/%s" %
                  (host, os.path.abspath(path).strip("/")))

def foafType(path):
    """
    >>> foafType('foo.jpg')
    FOAF['Image']
    >>> foafType('a/mystery')
    None
    """
    mimetype, encoding = mimetypes.guess_type(path.lower())
    if mimetype is not None and mimetype.startswith("image/"):
        return FOAF['Image']

    return FOAF['Document'] # from my memory - check on this
