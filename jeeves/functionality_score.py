import requests
from rich.console import Console
from rich.table import Table

console = Console()


def calculate_functionality_score_for_rare_predicates():
    """Calculate Functionality Score for 10 rarest predicates using QLever API."""
    endpoint = 'https://qlever.dev/api/wikidata'
    headers = {
        'Content-Type': 'application/sparql-query',
        'Accept': 'application/sparql-results+json',
    }

    # Find 20 rarest predicates with count > 1 and their labels (labels required)
    rare_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wikibase: <http://wikiba.se/ontology#>

SELECT ?predicate ?label ?count
WHERE {
  {
    SELECT ?predicate (COUNT(*) AS ?count)
    WHERE {
      ?s ?predicate ?o .
    }
    GROUP BY ?predicate
    HAVING (COUNT(*) > 3)
    ORDER BY ASC(COUNT(*))
    LIMIT 200
  }
  ?propertyEntity wikibase:claim ?predicate .
  ?propertyEntity rdfs:label ?label .
  FILTER(LANG(?label) = "en" || LANG(?label) = "")
  FILTER(!CONTAINS(STR(?label), "ID"))
}
"""
    response = requests.post(endpoint, data=rare_query, headers=headers)
    if response.status_code != 200:
        console.print(f'Error: {response.text}')
        return
    results = response.json()['results']['bindings']

    if not results:
        console.print('No results found')
        return

    predicates = [binding['predicate']['value'] for binding in results]
    counts = {binding['predicate']['value']: binding['count']['value'] for binding in results}
    labels = {binding['predicate']['value']: binding['label']['value'] for binding in results}
    values_clause = ' '.join(f'<{p}>' for p in predicates)

    # Calculate functionality scores for all predicates using VALUES
    score_query = f"""
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
  ?predicate
  (xsd:decimal(COUNT(DISTINCT ?s)) / xsd:decimal(COUNT(*)) AS ?functionalityScore)
WHERE {{
  VALUES ?predicate {{ {values_clause} }}
  ?s ?predicate ?o .
}}
GROUP BY ?predicate
"""
    response = requests.post(endpoint, data=score_query, headers=headers)
    scores = {
        binding['predicate']['value']: binding['functionalityScore']['value']
        for binding in response.json()['results']['bindings']
    }

    table = Table()
    table.add_column('Property')
    table.add_column('Label')
    table.add_column('Occurrences')
    table.add_column('Functionality Score')

    for predicate_uri in predicates:
        label = labels[predicate_uri]
        occurrences = counts[predicate_uri]
        score = scores.get(predicate_uri, 'N/A')
        table.add_row(predicate_uri.split('/')[-1], label, occurrences, score)

    console.print(table)