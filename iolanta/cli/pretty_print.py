from datetime import date
from typing import Union

from classes import typeclass


@typeclass
def render_literal_value(literal_value) -> str:
    """Render a literal value nicely for printing."""


@render_literal_value.instance(None)
def _render_none(literal_value: None) -> str:
    return f'∅ {literal_value}'


@render_literal_value.instance(bool)
def _render_bool(literal_value: bool) -> str:
    icon = '✅' if literal_value else '❌'
    return f'{icon} {literal_value}'


@render_literal_value.instance(int)
def _render_int(literal_value: Union[int, float]) -> str:
    return f'🔢 {literal_value}'


@render_literal_value.instance(str)
def _render_str(literal_value: str) -> str:
    return f'🔡 {literal_value}'


@render_literal_value.instance(date)
def _render_date(literal_value: date) -> str:
    return f'📅 {literal_value}'


@render_literal_value.instance(object)
def _render_default(literal_value: object) -> str:
    return f'❓ {literal_value}'
