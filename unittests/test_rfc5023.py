#! /usr/bin/env python

import unittest

import os, random, time
from StringIO import StringIO
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

HTTP_PORT=random.randint(1111,9999)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
	pass

class APPHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		response=FAKE_SERVER.get(self.path,None)
		if response is None:
			self.send_response(404)
			self.send_header("Content-Length","0")
			self.end_headers()
		else:
			self.send_response(response[0])
			self.send_header("Content-type", response[1])
			self.send_header("Content-Length",str(len(response[2])))
			self.end_headers()
			self.wfile.write(response[2])

	def log_request(code=None, size=None):
		# BaseHTTPRequestHandler.log_request(self,code,size)
		# Prevent successful requests logging to stderr
		pass

		
def runAPPServer():
	server=ThreadingHTTPServer(("localhost",HTTP_PORT), APPHandler)
	server.serve_forever()


def suite():
	# kick-off a thread to run an HTTP server	
	t=Thread(target=runAPPServer)
	t.setDaemon(True)
	t.start()
	print "APP tests starting HTTP server on localhost, port %i"%HTTP_PORT
	return unittest.TestSuite((
		unittest.makeSuite(APP5023Tests,'test'),
		unittest.makeSuite(APPElementTests,'test'),
		unittest.makeSuite(CategoriesTests,'test'),
		unittest.makeSuite(ServiceTests,'test'),
		unittest.makeSuite(WorkspaceTests,'test'),
		unittest.makeSuite(CollectionTests,'test'),
		unittest.makeSuite(ClientTests,'test'),
		unittest.makeSuite(ServerTests,'test')
		))


def load_tests(loader, tests, pattern):
	"""Called when we execute this file directly."""
	return suite()


from pyslet.rfc5023 import *

CAT_EXAMPLE_1="""<?xml version="1.0" ?>
<app:categories
   xmlns:app="http://www.w3.org/2007/app"
   xmlns:atom="http://www.w3.org/2005/Atom"
   fixed="yes" scheme="http://example.com/cats/big3">
 <atom:category term="animal" />
 <atom:category term="vegetable" />
 <atom:category term="mineral" />
</app:categories>"""

SVC_EXAMPLE_1="""<?xml version="1.0" encoding='utf-8'?>
<service xmlns="http://www.w3.org/2007/app"
		xmlns:atom="http://www.w3.org/2005/Atom">
 <workspace>
   <atom:title>Main Site</atom:title>
   <collection
	   href="http://example.org/blog/main" >
	 <atom:title>My Blog Entries</atom:title>
	 <categories
		href="http://example.com/cats/forMain.cats" />
   </collection>
   <collection
	   href="http://example.org/blog/pic" >
	 <atom:title>Pictures</atom:title>
	 <accept>image/png</accept>
	 <accept>image/jpeg</accept>
	 <accept>image/gif</accept>
   </collection>
 </workspace>
 <workspace>
   <atom:title>Sidebar Blog</atom:title>
   <collection
	   href="http://example.org/sidebar/list" >
	 <atom:title>Remaindered Links</atom:title>
	 <accept>application/atom+xml;type=entry</accept>
	 <categories fixed="yes">
	   <atom:category
		 scheme="http://example.org/extra-cats/"
		 term="joke" />
	   <atom:category
		 scheme="http://example.org/extra-cats/"
		 term="serious" />
	 </categories>
   </collection>
 </workspace>
</service>"""

SVC_EXAMPLE_2="""<?xml version="1.0" encoding='utf-8'?>
<service xmlns="http://www.w3.org/2007/app"
		xmlns:atom="http://www.w3.org/2005/Atom">
 <workspace>
   <atom:title>Test Workspace</atom:title>
   <collection
	   href="/collections/blog" >
	 <atom:title>Test Blog</atom:title>
   </collection>
   <collection
	   xml:base="/morecollections/" href="blog" >
	 <atom:title>Test Blog</atom:title>
   </collection>
 </workspace>
</service>"""

FEED_TEST_BLOG="""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>Test Blog Feed</title>
 <link href="http://example.org/"/>
 <updated>2003-12-13T18:30:02Z</updated>
 <author>
	<name>John Doe</name>
 </author>
 <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>
 <entry>
	<title>Atom-Powered Robots Run Amok</title>
	<link href="http://example.org/2003/12/13/atom03"/>
	<id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
	<updated>2003-12-13T18:30:02Z</updated>
	<summary>Some text.</summary>
 </entry>
</feed>"""

FAKE_SERVER={
	'/service':(200,ATOMSVC_MIMETYPE,SVC_EXAMPLE_2),
	'/collections/blog':(200,atom.ATOM_MIMETYPE,FEED_TEST_BLOG),
	'/morecollections/blog':(200,atom.ATOM_MIMETYPE,FEED_TEST_BLOG)
	}
	
class APP5023Tests(unittest.TestCase):
	def testCaseConstants(self):
		self.failUnless(APP_NAMESPACE=="http://www.w3.org/2007/app","Wrong APP namespace: %s"%APP_NAMESPACE)
		self.failUnless(ATOMSVC_MIMETYPE=="application/atomsvc+xml","Wrong APP service mime type: %s"%ATOMSVC_MIMETYPE)
		self.failUnless(ATOMCAT_MIMETYPE=="application/atomcat+xml","Wrong APP category mime type: %s"%ATOMCAT_MIMETYPE)

	def testCaseTBA(self):
		"""
		Atom Publishing Protocol XML Documents MUST be "namespace-well-
		formed" as specified in Section 7 of [REC-xml-names]
		
		Foreign markup can be used anywhere
		within a Category or Service Document unless it is explicitly
		forbidden.  Processors that encounter foreign markup MUST NOT stop
		processing and MUST NOT signal an error.
	   """
	   
class APPElementTests(unittest.TestCase):
	def testCaseConstructor(self):
		e=APPElement(None)
		self.failUnless(e.xmlname is None,'element name on construction')
		self.failUnless(e.GetBase() is None,"xml:base present on construction")
		self.failUnless(e.GetLang() is None,"xml:lang present on construction")
		self.failUnless(e.GetSpace() is None,"xml:space present on construction")
		attrs=e.GetAttributes()
		self.failUnless(len(attrs.keys())==0,"Attributes present on construction")

class CategoriesTests(unittest.TestCase):
	def testCaseConstructor(self):
		e=Categories(None)
		self.failUnless(e.ns==APP_NAMESPACE,'ns on construction')
		self.failUnless(e.xmlname=="categories",'element name on construction')
		self.failUnless(e.GetBase() is None,"xml:base present on construction")
		self.failUnless(e.GetLang() is None,"xml:lang present on construction")
		self.failUnless(e.GetSpace() is None,"xml:space present on construction")
		attrs=e.GetAttributes()
		self.failUnless(len(attrs.keys())==0,"Attributes present on construction")
		self.failUnless(e.href is None,"href present on construction")
		self.failUnless(e.fixed is None,"fixed on construction")
		self.failUnless(e.scheme is None,"scheme present on construction")
		self.failUnless(len(e.Category)==0,"Category  list non empty on construction")
		
class CollectionTests(unittest.TestCase):
	def testCaseConstructor(self):
		c=Collection(None)
		self.failUnless(isinstance(c,APPElement),"Collection not an APPElement")
		self.failUnless(c.xmlname=="collection","Collection XML name")
		self.failUnless(c.href is None,"HREF present on construction")
		attrs=c.GetAttributes()
		self.failUnless(len(attrs.keys())==0,"Attributes present on construction")
		self.failUnless(c.Title is None,"Title present on construction")
		self.failUnless(len(c.Accept)==0,"Accept list non-empty on construction")
		self.failUnless(len(c.Categories)==0,"Categories list non-empty on construction")
		
class WorkspaceTests(unittest.TestCase):
	def testCaseConstructor(self):
		ws=Workspace(None)
		self.failUnless(isinstance(ws,APPElement),"Workspace not an APPElement")
		self.failUnless(ws.xmlname=="workspace","Workspace XML name")
		attrs=ws.GetAttributes()
		self.failUnless(len(attrs.keys())==0,"Attributes present on construction")
		self.failUnless(ws.Title is None,"Title present on construction")
		collections=ws.Collection
		self.failUnless(len(collections)==0,"Collections present on construction")

class ServiceTests(unittest.TestCase):
	def testCaseConstructor(self):
		svc=Service(None)
		self.failUnless(isinstance(svc,APPElement),"Service not an APPElement")
		self.failUnless(svc.xmlname=="service","Service XML name")
		attrs=svc.GetAttributes()
		self.failUnless(len(attrs.keys())==0,"Attributes present on construction")
		workspaces=svc.Workspace
		self.failUnless(len(workspaces)==0,"Workspaces present on construction")

	def testCaseReadXML(self):
		doc=Document()
		doc.Read(src=StringIO(SVC_EXAMPLE_1))
		svc=doc.root
		self.failUnless(isinstance(svc,Service),"Example 1 not a service")
		wspace=svc.Workspace
		self.failUnless(len(wspace)==2,"Example 1 has no workspaces")
		ws=wspace[0]
		title=ws.Title
		self.failUnless(isinstance(title,atom.Text) and title.GetValue()=="Main Site","Example 1, workspace 1 title")
		collections=ws.Collection
		self.failUnless(len(collections)==2,"Example 1, workspace 1 has no collections")
		c=collections[0]
		self.failUnless(isinstance(c,Collection) and c.href=="http://example.org/blog/main","Collection type or href")
		title=c.Title
		self.failUnless(isinstance(title,atom.Text) and title.GetValue()=="My Blog Entries","Collection title")
		cats=c.Categories[0]
		self.failUnless(isinstance(cats,Categories) and cats.href=="http://example.com/cats/forMain.cats","Collection categories")
		accepts=collections[1].Accept
		self.failUnless(len(accepts)==3 and accepts[0].GetValue()=="image/png" and accepts[2].GetValue()=="image/gif","Collection accepts")
		cats=wspace[1].Collection[0].Categories[0]
		self.failUnless(cats.fixed,"Collection categories fixed")
		catList=cats.Category
		self.failUnless(len(catList)==2,"Collection category list")
		cat=catList[0]
		self.failUnless(isinstance(cat,atom.Category) and cat.scheme=="http://example.org/extra-cats/"
			and cat.term=="joke","Collection category 1")
		cat=catList[1]
		self.failUnless(isinstance(cat,atom.Category) and cat.scheme=="http://example.org/extra-cats/"
			and cat.term=="serious","Collection category 2")


class ClientTests(unittest.TestCase):
	def testCaseConstructor(self):
		client=Client()		
		self.failUnless(isinstance(client,http.HTTPRequestManager),'Client super')
		
	def testCaseAPPGet(self):
		doc=Document(baseURI='http://localhost:%i/service'%HTTP_PORT)
		client=Client()
		doc.Read(reqManager=client)
		svc=doc.root
		self.failUnless(isinstance(svc,Service),"GET /service")
		for ws in svc.Workspace:
			for c in ws.Collection:
				feedDoc=Document(baseURI=c.GetFeedURL())
				feedDoc.Read(reqManager=client)
				feed=feedDoc.root
				self.failUnless(isinstance(feed,atom.Feed),"Collection not a feed for %s"%c.Title)


class MockRequest(object):

	responses=BaseHTTPRequestHandler.responses

	def __init__(self,path='/'):
		self.client_address=("127.0.0.1","80")
		self.command="GET"
		self.path=path
		self.request_version="HTTP/1.0"
		self.headers={}
		self.rfile=StringIO()
		self.responseCode=None
		self.responseMessage=None
		self.responseHeaders={}
		self.wfile=None
		
	def send_response(self, code, message=None):
		assert self.responseCode is None
		if message is None:
			message,details=self.responses.get(code,('',''))
		self.responseCode=code
		self.responseMessage=message
		
	def send_header(self, keyword, value):
		assert self.responseCode is not None
		assert self.wfile is None
		self.responseHeaders[keyword]=value
	
	def end_headers(self):
		assert self.wfile is None
		self.wfile=StringIO()

			
class ServerTests(unittest.TestCase):
	def testCaseConstructor(self):
		s=Server("http://localhost/service")
		self.failUnless(isinstance(s.service,Service),"Service document")
		request=MockRequest('/service')
		s.HandleGET(request)
		self.failUnless(request.responseCode==200)
		cLen=int(request.responseHeaders['Content-Length'])
		cData=request.wfile.getvalue()
		self.failUnless(len(cData)==cLen,"Content-Length mismatch")
		doc=Document(baseURI="http://localhost/service")
		doc.Read(cData)
		svc=doc.root
		self.failUnless(isinstance(svc,Service),"Server: GET /service")
		self.failUnless(len(svc.Workspace)==0,"Server: no workspaces")

	def testCaseWorkspace(self):
		s=Server("http://localhost/service")
		ws=s.service.ChildElement(Workspace)
		title=ws.ChildElement(atom.Title)
		titleText="Some work space while others space work"
		title.SetValue(titleText)
		request=MockRequest('/service')
		s.HandleGET(request)
		doc=Document(baseURI="http://localhost/service")
		doc.Read(request.wfile.getvalue())
		svc=doc.root
		self.failUnless(len(svc.Workspace)==1,"Server: one workspace")
		self.failUnless(svc.Workspace[0].Title.GetValue()==titleText,"Server: one workspace title")

	def testCaseCollection(self):
		s=Server("http://localhost/service")
		ws=s.service.ChildElement(Workspace)
		title=ws.ChildElement(atom.Title)
		titleText="Collections"
		title.SetValue(titleText)
		c1=ws.ChildElement(Collection)
		c1.ChildElement(atom.Title).SetValue("Collection 1")
		c1.href="c1"
		c2=ws.ChildElement(Collection)
		c2.ChildElement(atom.Title).SetValue("Collection 2")
		c2.href="/etc/c2"
		request=MockRequest('/service')
		s.HandleGET(request)
		doc=Document(baseURI="http://localhost/service")
		doc.Read(request.wfile.getvalue())
		svc=doc.root
		self.failUnless(len(svc.Workspace[0].Collection)==2,"Server: two collections")
		c2Result=svc.Workspace[0].Collection[1]
		self.failUnless(c2Result.Title.GetValue()=="Collection 2","Server: two collections title")
		self.failUnless(c2Result.ResolveURI(c2Result.href)=="http://localhost/etc/c2","Server: collection href")

		
if __name__ == "__main__":
	unittest.main()
