import unittest, os, subprocess, time
from sets import Set
from rdflib import RDF, URIRef

def testpath(localpath):
    return os.path.join(os.path.dirname(__file__), localpath)

os.environ['SEMFILE_TAGS'] = testpath("tags.rdf")
# semfile reads env SEMFILE_TAGS, so you need to do import common
# before using semfile.py


def testfileuri(localpath):
    return URIRef("file://score.bigasterisk.com/home/drewp/projects/semfile/test/%s" % localpath)

def call(*args):
    status = subprocess.call([testpath(os.path.join("..", args[0]))] +
                           list(args[1:]),
                           env={'SEMFILE_TAGS' : testpath("tags.rdf")})
    if status >> 8 != 0:
        raise RuntimeError("command failed")

def numTriples(graph, subj):
    return len(list(graph.triples((subj, None, None))))

class CleanTags(unittest.TestCase):
    """via environ['SEMFILE_TAGS'], semfile will be looking at a
    scratch tags.rdf file in the test directory. this test setup will
    remove that tag file before each test"""
    
    def setUp(self):
        os.unlink(testpath("tags.rdf"))
        
