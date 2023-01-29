import html
import textwrap

from dominate.tags import table, tr, td, b
from dominate.util import raw, text

from iolanta.facet import Facet
import graphviz

from iolanta.models import NotLiteralNode


def as_graph_id(node: NotLiteralNode):
    return str(node).replace(':', '_')


def wrap_content(source: str) -> text:
    splitter = '<br align="left"/>'

    wrapped = splitter.join(
        textwrap.wrap(
            html.escape(source.replace('"', '')),
            width=20,
        ),
    )

    wrapped = f'{wrapped}{splitter}'

    return raw(wrapped)


class GraphvizRoadmap(Facet[str]):
    def show(self) -> str:
        graph = graphviz.Digraph(
            graph_attr={
                'rankdir': 'LR',
            }
        )

        tasks = {
            task['task']: task
            for task in self.stored_query('tasks.sparql', goal=self.iri)
        }

        for task in tasks.values():
            table_rows = [
                tr(
                    td(
                        b(
                            wrap_content(task['title']),
                        ),
                        align='left',
                    ),
                ),
            ]

            if description := task.get('description'):
                table_rows.append(
                    tr(
                        td(
                            wrap_content(description),
                            align='left',
                        ),
                    ),
                )

            label = table(
                *table_rows,
                border='0',
                cellborder='1',
                cellspacing='0',
                bgcolor='#AC6363' if task.get('is_bug') else 'white',
            ).render(indent='', pretty=False)

            graph.node(
                name=as_graph_id(task['task']),
                label=f'<{label}>',
                shape='none',
            )

        edges = self.stored_query('edges.sparql')
        for edge in edges:
            start, end = edge['blocker'], edge['blocked']

            if start in tasks and end in tasks:
                graph.edge(
                    as_graph_id(edge['blocker']),
                    as_graph_id(edge['blocked']),
                )

        graph.render(
            '/tmp/iolanta-roadmap.png',
            format='png',
            view=True,
        )
