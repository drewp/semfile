#!/usr/bin/python

"""
http://dannyayers.com/archives/2005/06/25/node-and-arc-diagrams-with-javascript/ is the challenge

http://www.w3.org/2001/02pd/ is very related, but I think mine is
different because I want to recapture the graphviz layout and then do
additional style on the results. Doing the style as more rdf is
probably a great idea, though, so maybe I can reuse a lot.

related:
http://www.decafbad.com/blog/2005/07/02/drag_the_boxes_stretch_the_lines

todo:
use namespaces in the graph labels, and put a key to the side. the
labels should still be links to their full uris

"""

from __future__ import division
import sys, tempfile, os, shlex, urlparse, sets
from md5 import md5
from rdflib import Graph, RDF, Namespace
from nevow import tags as T
from nevow.flat.ten import flatten
from semfile import FOAF
sys.path.append("/my/site/quickwit")
try:
    import resizeimg
except ImportError:
    class _:
        def writethumbnail(self, *args):
            print "missing thumbnail code"
    resizeimg = _()

def css_attrs(**kw):
    return "; ".join(["%s: %s" % (k.replace('_','-'),v)
                      for k,v in kw.items() if v is not None])

class Jsrender:
    # http://www.walterzorn.com/jsgraphics/jsgraphics_e.htm

    scale = 120,120 # pixels per graphviz unit
    def __init__(self):
        self.draw_cmds = ""
        self.html_cmds = []

    def worldx(self, gx, _idx=0):
        wx = gx * self.scale[_idx]
        return wx
    def worldy(self, gy):
        return self.worldx(gy, 1)

    def rect(self,x,y,w,h):
        """x,y is at the center"""
        self.draw_cmds += "jg.drawRect(%s,%s,%s,%s);\n" % (
            self.worldx(x - w / 2),
            self.worldy(y - h / 2),
            self.worldx(w),
            self.worldy(h))
        
    def label(self, x, y, w=None, h=None, textAlign=None, html="",
              background=None, border=None):
        attrs = dict(position="absolute",
                     left="%spx" % self.worldx(x),
                     top="%spx" % self.worldy(y),
                     z_index=2,
                     border=border,
                     background=background,
                     )
        if w is not None:
            attrs.update(dict(word_wrap="break-word",
                            width="%spx" % self.worldx(w),
                            height="%spx" % self.worldy(h),
                            text_align=textAlign))

        self.html_cmds += [T.div(style=css_attrs(**attrs))[html]]

    def polyline(self,xy):
        def jsarray(l,mapfunc):
            return "new Array(%s)" % ",".join([str(mapfunc(c)) for c in l])
        xs = jsarray(xy[::2], lambda x: self.worldx(float(x)))
        ys = jsarray(xy[1::2], lambda y: self.worldy(float(y)))
        self.draw_cmds += "jg.drawPolyline(%s,%s);\n" % (xs, ys)

    def output(self):
        return flatten(
            T.html[
              T.head[T.script(type="text/javascript", src="wz_jsgraphics.js")],
              T.body(bgcolor="#cdcdb4")[
                T.script(type="text/javascript")[
                     "var jg = new jsGraphics();",
                     self.draw_cmds,
                     "jg.paint();",
                     ],
                self.html_cmds
            ]])

class DotParse:
    """parse output from 'dot -Tplain' etc

    format at http://www.graphviz.org/cvs/doc/info/output.html#d:plain
    
    should i use SVG? i didn't notice that choice before
    """
    def __init__(self,infile):
        for line in infile:
            words = shlex.split(line)
            if words[0] == "graph":
                pass
            elif words[0] == "node":
                name,x,y,width,height = words[1:6]
                x,y,width,height = map(float, (x,y,width,height))
                self.node(name, x, y, width, height)                
            elif words[0] == "edge":
                tail,head,n = words[1:4]
                n = int(n)
                xy = map(float,words[4:4 + n * 2])
                if len(words) > 4 + n * 2 + 3: # untested
                    label,xl,yl = words[4 + n * 2:4 + n * 2 + 3]
                else:
                    label,xl,yl = None,None,None
                style,color = words[-2:]
                if style != "invis":
                    self.edge(label, xy, xl, yl)
            elif words[0] == "stop":
                break
            else:
                raise ValueError("cannot parse dot line %r" % line)
        
    def node(self, name, x, y, width, height):
        raise NotImplementedError

    def edge(self, label, xy):
        raise NotImplementedError
        
class DotToJs(DotParse):
    def __init__(self, infile, jsrender, node_html):
        self.jsr, self.node_html = jsrender, node_html
        DotParse.__init__(self, infile)
        
    def node(self, name, x, y, width, height):
        self.jsr.label(x - width / 2, y - height / 2, 
                       width, height, "center", self.node_html.get(name,""),
                       background="white", border="1px solid")

    def edge(self, label, xy, xl, yl):
        self.jsr.polyline(xy)
        self.jsr.label(xy[-2],xy[-1],html=">") # arrowheads :)
        label = T.a(href=label)[label[label.rfind('/')+1:]]
        if label is not None:
            self.jsr.label(float(xl), float(yl),
                           html=label)


class GraphvizOut:
    # format at http://www.graphviz.org/cvs/doc/info/lang.html
    # attrs at http://www.graphviz.org/cvs/doc/info/attrs.html
    def __init__(self, write_func, digraph=False):
        self.wr = write_func
        self.digraph = digraph
        graph_keyword = "graph"
        if digraph:
            graph_keyword = "digraph"
        self.wr("""%s G {

  graph [margin=2, rankdir=LR, ratio="auto", mclimit=100, epsilon=.00001,
         headclip=true, tailclip=true, packmode="node"];
  node [fixedsize=true, width=1, height=1];
  edge [len=2];

""" % (graph_keyword))

    def _fmtattrs(self, attrs):
        def no_unicode(s):
            if isinstance(s,basestring):
                s = '"%s"' % str(s).encode('string-escape')
            return s
        return ", ".join([("%s=%s" % (k,no_unicode(v)))
                          for k,v in attrs.items()])        

    def edge(self, s, e, **attrs):
        connector = "--"
        if self.digraph:
            connector = "->"
        self.wr('  "%s" %s "%s" [%s]\n' % (s, connector, e,
                                           self._fmtattrs(attrs)))

    def node(self, n, **attrs):
        self.wr('  "%s" [%s]\n' % (n, self._fmtattrs(attrs)))

    def close(self):
        self.wr("}\n")


def conv(graph, show_dot=False):
    node_html = {} # urlstr : path

    dotfile = tempfile.NamedTemporaryFile(prefix="rdf2js_graph_",suffix=".dot")

    if 1:
        layout_prog = "neato"
        digraph = False
    else:
        layout_prog = "dot"
        digraph = True
    go = GraphvizOut(dotfile.write, digraph)


    edge_clique = sets.Set()

    for s,p,o in graph.triples((None,None,None)):
        weight = 1

        addr,netloc,path,params,query,frag = urlparse.urlparse(s)
        if (p, o) == (RDF.type, FOAF['Image']):

            thumb = os.path.join("thumbs",
                                 md5(s).hexdigest() + os.path.splitext(s)[1])
            resizeimg.writethumbnail(s[7:], thumb)
            imgpath = thumb
            go.node(s, width=200/120, height=200/120)
            node_html[str(s)] = T.img(src=imgpath, alt=s)
            continue # no type edge/node needed

        if str(s) not in node_html:
            node_html[str(s)] = s

        addr,netloc,path,params,query,frag = urlparse.urlparse(o)
        if p == FOAF['topic']:
            go.node(o, width=.6, height=.3)
            node_html[str(o)] = ["Topic:", T.br, path.split('/')[-1]]
            edge_clique.add(o)

        if str(o) not in node_html:
            node_html[str(o)] = o

        go.edge(s, o, label=p, weight=weight)


    for e in edge_clique:
        for e2 in edge_clique:
            if e2 != e:
                go.edge(e, e2, weight=2, style="invis")

    go.close()
    dotfile.flush()

    if show_dot:
        print open(dotfile.name).read()

    jsr = Jsrender()

    DotToJs(os.popen('%s -Tplain %s' % (layout_prog, dotfile.name)),
            jsr, node_html)

    return jsr.output()

