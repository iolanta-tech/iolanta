import rdflib

LOCAL = rdflib.Namespace('local:')
IOLANTA = rdflib.Namespace('https://iolanta.tech/')
DATATYPES = rdflib.Namespace('https://iolanta.tech/datatypes/')
PYTHON = rdflib.Namespace('python://')
NP = rdflib.Namespace('https://www.nanopub.org/nschema#')
RDFG = rdflib.Namespace('https://www.w3.org/2004/03/trix/rdfg-1/')
SDO = rdflib.SDO

META = rdflib.URIRef('iolanta://_meta')


class DC(rdflib.DC):
    _NS = rdflib.Namespace('https://purl.org/dc/elements/1.1/')


class OWL(rdflib.OWL):
    _NS = rdflib.Namespace('https://www.w3.org/2002/07/owl#')


class RDFS(rdflib.RDFS):
    _NS = rdflib.Namespace('https://www.w3.org/2000/01/rdf-schema#')


class RDF(rdflib.RDF):
    _NS = rdflib.Namespace('https://www.w3.org/1999/02/22-rdf-syntax-ns#')


class DCTERMS(rdflib.DCTERMS):
    _NS = rdflib.Namespace('https://purl.org/dc/terms/')


class VANN(rdflib.VANN):
    _NS = rdflib.Namespace('https://purl.org/vocab/vann/')


class FOAF(rdflib.FOAF):
    _NS = rdflib.Namespace('https://xmlns.com/foaf/0.1/')


class XSD(rdflib.XSD):
    _NS = rdflib.Namespace('https://www.w3.org/2001/XMLSchema#')


class PROV(rdflib.PROV):
    _NS = rdflib.Namespace('https://www.w3.org/ns/prov#')
