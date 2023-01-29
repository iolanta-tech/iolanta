import csv
import sys

from classes import typeclass
from rdflib import Graph

from ldflex.ldflex import QueryResult, SelectResult


@typeclass
def csv_print(query_result: QueryResult) -> None:
    """Print as CSV."""


@csv_print.instance(SelectResult)
def _csv_select(select_result: SelectResult):
    if not select_result:
        return

    first_row = select_result[0]
    fieldnames = first_row.keys()

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(select_result)


@csv_print.instance(Graph)
def _construct_print(graph: Graph):
    if not graph:
        return

    writer = csv.writer(sys.stdout)
    writer.writerow(('subject', 'predicate', 'object'))
    writer.writerows(graph)
