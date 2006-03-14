import unittest, os, subprocess, time
from sets import Set
from rdflib import RDF, URIRef

from common import call, numTriples, testfileuri, testpath, CleanTags
from semfile import read_or_create_graph, FOAF, TAG, DC

imagePath = testpath("image1.jpg")
imageUri = testfileuri("image1.jpg")

class Test(CleanTags):

    def testCreateOneTag(self):
        call("stag", testpath("somefile1"), "atag")
        graph = read_or_create_graph()
        u = testfileuri("somefile1")
        self.assertEqual(graph.value(u, FOAF['topic']), TAG['atag'])
        self.assertNotEqual(graph.value(u, DC['issued'], None), None)
        self.assertEqual(graph.value(u, RDF.type, None), None)

    def testCreateImageTag(self):
        call("stag", imagePath, "atag")
        graph = read_or_create_graph()
        self.assertEqual(graph.value(imageUri, RDF.type), FOAF['Image'])

    def testCreateTwoTags(self):
        call("stag", imagePath, "tag1", "tag2")
        graph = read_or_create_graph()
        self.assertEqual(Set(graph.objects(imageUri, FOAF['topic'])),
                         Set([TAG['tag1'], TAG['tag2']]))

    def testRemove(self):
        call("stag", imagePath, "tag1")
        call("stag_remove", "--yes")
        graph = read_or_create_graph()
        self.assertEqual(numTriples(graph, imageUri), 0)

    def testRemoveRecentOnly(self):
        call("stag", testpath("oldImage.jpg"), "tag1")
        time.sleep(1.2)
        call("stag", imagePath, "tag2")
        call("stag_remove", "--yes", "--max_gap_time", "1")
        graph = read_or_create_graph()
        self.assertEqual(numTriples(graph, testfileuri("oldImage.jpg")), 3)
        self.assertEqual(numTriples(graph, imageUri), 0)
        
unittest.main()
