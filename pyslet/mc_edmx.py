#! /usr/bin/env python
"""This module implements the EDMX specification defined by Microsoft.

http://msdn.microsoft.com/en-us/library/dd541284(v=prot.10)"""

import pyslet.xml20081126.structures as xml
import pyslet.xmlnames20091208 as xmlns
import pyslet.rfc2396 as uri
import pyslet.mc_csdl as edm


EDMX_NAMESPACE="http://schemas.microsoft.com/ado/2007/06/edmx"		#: Namespace to use for EDMX elements

class EDMXElement(xmlns.XMLNSElement):
	pass


class DataServices(EDMXElement):
	XMLNAME=(EDMX_NAMESPACE,'DataServices')

	def __init__(self,parent):
		EDMXElement.__init__(self,parent)
		self.Schema=[]


class Reference(EDMXElement):
	XMLNAME=(EDMX_NAMESPACE,'Reference')
	
	XMLATTR_Url=('url',uri.URIFactory.URI,str)
	
	def __init__(self,parent):
		EDMXElement.__init__(self,parent)
		self.url=None
	
	
class AnnotationsReference(EDMXElement):
	XMLNAME=(EDMX_NAMESPACE,'AnnotationsReference')
	
	XMLATTR_Url=('url',uri.URIFactory.URI,str)
	
	def __init__(self,parent):
		EDMXElement.__init__(self,parent)
		self.url=None
	
	
class Edmx(EDMXElement):
	"""Represents the Edmx root element."""
	XMLNAME=(EDMX_NAMESPACE,'Edmx')
	DataServicesClass=DataServices

	XMLATTR_Version='version'
	
	def __init__(self,parent):
		EDMXElement.__init__(self,parent)
		self.version="1.0"
		self.Reference=[]
		self.AnnotationsReference=[]
		self.DataServices=self.DataServicesClass(self)
	
	def GetChildren(self):
		for child in itertools.chain(
			self.Reference,
			self.AnnotationsReference):
			yield child
		yield self.DataServices
		for child in EDMXElement.GetChildren(self):
			yield child


class Document(xmlns.XMLNSDocument):
	"""Represents an Edmx document."""

	classMap={}

	def __init__(self,**args):
		xmlns.XMLNSDocument.__init__(self,**args)
		self.defaultNS=EDMX_NAMESPACE
		self.MakePrefix(EDMX_NAMESPACE,'edmx')

	def GetElementClass(self,name):
		"""Overrides :py:meth:`pyslet.xmlnames20091208.XMLNSDocument.GetElementClass` to look up name."""
		eClass=Document.classMap.get(name,Document.classMap.get((name[0],None),xmlns.XMLNSElement))
		return eClass
	
xmlns.MapClassElements(Document.classMap,globals())
xmlns.MapClassElements(Document.classMap,edm,edm.EDM_NAMESPACE_ALIASES)

		