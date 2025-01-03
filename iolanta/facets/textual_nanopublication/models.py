from enum import Enum


class TermPositionInTriple(Enum):
    """Position of the term in a triple."""

    SUBJECT = 'subject'
    PREDICATE = 'predicate'
    OBJECT = 'object'
