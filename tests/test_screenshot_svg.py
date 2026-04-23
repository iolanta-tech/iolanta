from textwrap import dedent

import pytest

from tests.screenshot_svg import stable_svg_lines


def svg_with_text(
    text: str,
    class_name: str = 'terminal-123-r7',
    x_coordinate: str = '1',
) -> str:
    """Build a minimal SVG fixture with Textual-like volatile markup."""
    return dedent(
        f'''\
        <svg xmlns="http://www.w3.org/2000/svg">
          <style>
            .{class_name} {{ fill: #ffffff; }}
          </style>
          <clipPath id="terminal-123-clip-terminal">
            <rect x="0" y="0" width="100" height="100" />
          </clipPath>
          <text class="{class_name}" x="{x_coordinate}" y="2">{text}</text>
        </svg>
        ''',
    )


@pytest.mark.parametrize(
    ('first_svg', 'second_svg'),
    [
        (
            svg_with_text('Cyberspace', 'terminal-123-r7'),  # noqa: WPS226
            svg_with_text('Cyberspace', 'terminal-456-r9'),  # noqa: WPS226
        ),
        (
            svg_with_text('2026-04-22T10:11:12.123+04:00'),
            svg_with_text('2026-04-22T11:12:13.456+04:00'),
        ),
        (
            svg_with_text('⏳ Cyberspace'),
            svg_with_text('Cyberspace'),  # noqa: WPS226
        ),
        (
            svg_with_text('Cyberspace', x_coordinate='1'),  # noqa: WPS226
            svg_with_text('Cyberspace', x_coordinate='2'),  # noqa: WPS226
        ),
    ],
)
def test_stable_svg_lines_ignore_textual_noise(
    first_svg: str,
    second_svg: str,
):
    """Textual runtime noise must not change screenshot comparison."""
    assert stable_svg_lines(first_svg) == stable_svg_lines(second_svg)


def test_stable_svg_lines_keep_semantic_changes():
    """Actual rendered text changes must still fail screenshot comparison."""
    assert stable_svg_lines(svg_with_text('Cyberspace')) != stable_svg_lines(
        svg_with_text('Semantic Web'),
    )
