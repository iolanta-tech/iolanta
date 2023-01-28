import rdflib

from iolanta.models import Triple


def reformat_blank_nodes(prefix: str, triple: Triple) -> Triple:
    """
    Prepend prefix to every blank node.

    JSON-LD flattening creates sequential identifiers in the form of _:bN
    for every blank node. See https://www.w3.org/TR/json-ld11/

    This means that subgraphs of the Octiron ConjunctiveGraph have clashing
    blank node identifiers.

    To avoid that, we prepend a prefix to every blank node identifier.
    """
    return Triple(
        *(
            rdflib.BNode(value=prefix + str(singleton)) if (
                isinstance(singleton, rdflib.BNode)
            ) else singleton
            for singleton in triple
        ),
    )
