import textwrap
from dataclasses import dataclass, field
from typing import List

from documented import DocumentedError
from rdflib import Literal, URIRef
from rdflib.term import Node

from iolanta.models import NotLiteralNode


@dataclass
class PageNotFound(DocumentedError):
    """
    Page not found by IRI: `{self.iri}`.

    !!! error "Page not found by IRI: `{self.iri}`"
        Every page on your documentation site, just as any other entity described on
        it, has an IRI — a unique identifier similar to a URL. IRI can be generated
        in two alternative ways.

          1. If you wanted to use IRI generated automatically, then please confirm
             that in the `docs` directory there is a file under the following path:

             ```
             {self.possible_path}
             ```

          2. If you wanted to use IRI that you specified explicitly then confirm
             there is a Markdown file somewhere in `docs` directory which contains
             the following text in its header:

             ```markdown
             ---
             $id: {self.possible_id}
             ---
             ```
    """

    iri: URIRef

    @property
    def possible_path(self) -> str:
        """Guess on a possible path."""
        base_path = str(self.iri).replace('local:', '')
        return f'{base_path}.md'

    @property
    def possible_id(self) -> str:
        """Guess on a possible $id."""
        return str(self.iri).replace('local:', '')


@dataclass
class MultipleFacetsFoundForTypes(DocumentedError):
    """
    Multiple suitable facets found.

    Unable to render the node unambiguously.

      - Node: {self.node}
      - Types:
    {self.formatted_types}
      - Facets found:
    {self.formatted_facets}
    """

    node: Node
    types: List[URIRef]
    facets: List[URIRef]

    @property
    def formatted_facets(self):
        return '\n'.join([
            f'    - {facet}'
            for facet in self.facets
        ])

    @property
    def formatted_types(self):
        return '\n'.join([
            f'    - <{node_type}>'
            for node_type in self.types
        ])


@dataclass
class FacetNotCallable(DocumentedError):
    """
    Python facet not callable.

    !!! error "Cannot import an object or cannot call it."

          - Import path: `{self.path}`
          - Object imported: `{self.facet}`

        The imported Python object is not a callable and thus cannot be used as
        a facet.
    """

    path: str
    facet: object


@dataclass
class FacetNotFound(DocumentedError):
    """
    # Facet not found.

    No way to render the node you asked for.

    - **Node:** `{self.node}` *({self.node_type})*
    - **Environments tried:** `{self.environments}`
    """

    node: Node
    environments: List[NotLiteralNode]
    node_types: List[NotLiteralNode] = field(default_factory=list)

    @property
    def node_type(self) -> str:
        """Node type."""
        node_type = type(self.node).__name__
        if isinstance(self.node, Literal):
            datatype = self.node.datatype
            node_type = f'{node_type}, datatype={datatype}'

        return node_type


@dataclass
class FacetError(DocumentedError):
    """
    Facet rendering failed.

    !!! error "Facet has thrown an unhandled exception"
        - Node: `{self.node}`
        - Facet IRI: `{self.facet_iri}`

        ### Exception

        {self.indented_error}
    """

    node: Node
    facet_iri: URIRef
    error: Exception

    @property
    def indented_error(self):
        """Format the underlying error text."""
        return textwrap.indent(
            str(self.error),
            prefix='    ',
        )


@dataclass
class NotALiteral(DocumentedError):
    """
    Node `{self.node}` is not a literal.

    It is in fact a `{self.node_type}`. `BoolLiteral` facet only supports RDF
    literal objects.
    """

    node: Node

    @property
    def node_type(self):
        """Node type name."""
        return self.node.__class__.__name__
