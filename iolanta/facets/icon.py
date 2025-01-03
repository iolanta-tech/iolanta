import funcy

from iolanta import Facet


class IconFacet(Facet[str]):
    """Icon of an object."""

    def show(self) -> str:
        """Render icon of a thing."""
        row = funcy.first(
            self.query(   # noqa: WPS462
                """
                SELECT * WHERE {
                    $iri iolanta:icon ?icon .
                }
                """,
                iri=self.iri,
            ),
        )

        if row:
            return row['icon']

        return ''
