import functools

import jinja2

from iolanta.iolanta import Iolanta
from iolanta_jinja2.macros import template_render


def process_template(
    template: str,
    iolanta: Iolanta,
) -> str:
    """Render a document using Jinja2 against iolanta."""
    return jinja2.Template(template).render({
        'render': functools.partial(
            template_render,
            iolanta=iolanta,
        ),
    })
