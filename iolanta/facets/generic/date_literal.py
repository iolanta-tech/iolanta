from datetime import date, datetime
from typing import cast

from rdflib import Literal

from iolanta.facets.facet import Facet


class DateLiteral(Facet):
    """Render a date."""

    def show(self):
        """Render date or datetime as a date."""
        literal = cast(Literal, self.iri)

        date_value = literal.value

        if isinstance(date_value, datetime):
            return str(date_value.date())

        if isinstance(date_value, date):
            return str(date_value)

        raise ValueError('Not a date! {}'.format(date_value))
