import unittest, tempfile, commands, difflib
from rdflib import Graph
from common import testfileuri, testpath
from rdf2js import conv

class Test(unittest.TestCase):
    def test(self):
        graph = Graph()
        graph.load(testpath("rdf2js_tags1.rdf"))
        out = conv(graph, False)
        out_file = tempfile.NamedTemporaryFile(suffix=".html")
        out_file.write(out)
        out_file.flush()
        lynxed = commands.getoutput(
            'lynx -dump -width=999 %s | egrep -v "^$"' % out_file.name)
        diff = difflib.SequenceMatcher(a=lynxed, b="""
Topic:
   atag
   file://score.bigasterisk.com/home/drewp/projects/semfile/test/image1.jpg
   2006-03-12T00:49:55-07:00
   >
   [1]topic
   >
   [2]issued
References
   1. http://xmlns.com/foaf/0.1/topic
   2. http://purl.org/dc/terms/issued
""")
        # lynx sometimes flips the order in the references section :(
        self.assertTrue(diff.ratio() > .9)
        

unittest.main()
