import difflib
import html
import re
import shutil
import tempfile
from pathlib import Path
from xml.etree import ElementTree

TRANSIENT_TIMESTAMP = re.compile(
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?',
)

LOADING_PREFIX = '⏳'


def stable_svg_lines(svg_text: str) -> list[str]:
    """Extract stable text rows from a Textual SVG screenshot."""
    svg = ElementTree.fromstring(svg_text)

    return [
        stable_svg_line(text_element)
        for text_element in svg.iter()
        if text_element.tag.endswith('text')
        and stable_svg_text(''.join(text_element.itertext()))
    ]


def stable_svg_line(text_element: ElementTree.Element) -> str:
    """Build a deterministic line for one SVG text element."""
    return stable_svg_text(''.join(text_element.itertext()))


def stable_svg_text(raw_text: str) -> str:
    """Normalize nondeterministic Textual screenshot text."""
    text = html.unescape(raw_text).replace('\xa0', ' ').strip()

    if text.startswith(LOADING_PREFIX):
        text = text.removeprefix(LOADING_PREFIX).strip()

    return TRANSIENT_TIMESTAMP.sub('TIMESTAMP', text)


def assert_stable_screenshot(
    expected_svg_path: Path,
    generated_svg_path: Path,
) -> None:
    """Compare screenshot semantics and keep raw failure output for review."""
    expected_lines = stable_svg_lines(expected_svg_path.read_text())
    generated_lines = stable_svg_lines(generated_svg_path.read_text())

    if expected_lines == generated_lines:
        return

    failure_path = screenshot_failure_path(generated_svg_path)
    failure_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(generated_svg_path, failure_path)

    diff = '\n'.join(
        difflib.unified_diff(
            expected_lines,
            generated_lines,
            fromfile=str(expected_svg_path),
            tofile=str(failure_path),
            lineterm='',
        ),
    )
    message = 'Screenshot changed: {expected}\nGenerated: {generated}\n{diff}'
    raise AssertionError(
        message.format(
            expected=expected_svg_path,
            generated=failure_path,
            diff=diff,
        ),
    )


def screenshot_failure_path(generated_svg_path: Path) -> Path:
    """Return a writable path for raw mismatch artifacts."""
    return (
        Path(tempfile.gettempdir())
        / 'iolanta-screenshot-failures'
        / generated_svg_path.name
    )
