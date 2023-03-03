import pydoc
from typing import Type, cast

from rdflib import URIRef

from iolanta.facets.errors import FacetNotCallable
from iolanta.facets.facet import Facet
from iolanta.resolvers.base import Resolver


class PythonImportResolver(Resolver):
    def __getitem__(self, item: URIRef) -> Type[Facet]:
        url = str(item)

        if not url.startswith('python://'):
            raise Exception(
                'Iolanta only supports facets which are importable Python '
                'callables. The URLs of such facets must start with '
                '`python://`, '
                'which {url} does not comply to.'.format(
                    url=url,
                ),
            )

        # It is impossible to use `urlpath` for this operation because it (or,
        # rather, one of upper classes from `urllib` that `urlpath` depends
        # upon)
        # will lowercase the URL when parsing it - which means, irreversibly. We
        # have to resort to plain string manipulation.
        import_path = url.replace('python://', '').strip('/')

        facet = cast(Type['iolanta.Facet'], pydoc.locate(import_path))

        if not callable(facet):
            raise FacetNotCallable(
                path=import_path,
                facet=facet,
            )

        return facet
