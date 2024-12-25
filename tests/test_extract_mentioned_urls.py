from iolanta.cyberspace.processor import extract_mentioned_urls_from_query
from iolanta.namespaces import IOLANTA, SDO


def test_extract_mentioned_urls_from_query():
    query = """
    SELECT ?output_datatype ?facet WHERE {
        ?class iolanta:hasInstanceFacet ?facet .
        ?facet iolanta:outputs ?output_datatype .
        FILTER(?class IN (
            <https://iolanta.tech/Graph>,
            <https://schema.org/Person>
        )) .
    }
    """

    _query, urls = extract_mentioned_urls_from_query(
        query=query,
        bindings={},
        base=None,
        namespaces={
            'iolanta': IOLANTA,
        },
    )

    assert {
        IOLANTA.Graph,
        SDO.Person,
    }.issubset(urls), urls
