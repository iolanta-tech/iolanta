from pathlib import Path

import funcy
from docutils.nodes import row
from rdflib import Literal, Namespace
from rich.table import Table

from iolanta import Facet
from iolanta.namespaces import DATATYPES, LOCAL

LEXINFO = Namespace('https://www.lexinfo.net/ontology/2.0/lexinfo#')


class RichDeclensionTable(Facet[Table]):
    """Declension forms of something."""

    META = Path(__file__).parent / 'data' / 'declension.yamlld'

    def show(self) -> Table:
        """Render declension forms of something."""
        rows = self.stored_query('declension.sparql', this=self.this)
        form_by_number_and_person = [
            ((row['number'], row['person']), self.render(row['declension'], as_datatype=DATATYPES.title))
            for row in rows
        ]

        declensions = funcy.group_values(form_by_number_and_person)

        table = Table('', 'Singular', 'Plural', title='Declension')

        table_rows = [
            [
                ', '.join(declensions[number, person])
                for number in [LEXINFO.singular, LEXINFO.plural]
            ]
            for person in [LEXINFO.firstPerson, LEXINFO.secondPerson, LEXINFO.thirdPerson]
        ]

        row_titles = ['1st', '2nd', '3rd']

        for title, table_row in zip(row_titles, table_rows):
            table.add_row(title, *table_row)

        return table
