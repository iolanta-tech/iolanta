/**
 * Raise Mermaid text limit for large generated diagrams (e.g. IBIS maps).
 * Default ~50k is exceeded by some blog pages; Material picks this up via window.mermaid.
 */
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

mermaid.initialize({
  maxTextSize: 200000,
  startOnLoad: false,
});

window.mermaid = mermaid;
