---
title: Facet
hide: [toc]
---

# 🎨 `Facet`

<table>
    <tr>
        <th>∈ Is</th>
        <td><code>rdfs:Class</code></td>
    </tr>
</table>

## In RDF

In RDF, a `Facet` is represented as an IRI, like this:

```
python://iolanta.facets.textual_default.InverseProperties
```

You can use properties like [`iolanta:hasInstanceFacet`](/hasInstanceFacet/) to attach a facet, by its IRI, to various IRIs — and thus influence how Iolanta renders these IRIs.

## Python class facets

The Facet IRI above actually points to a Python class which should be importable to Iolanta as follows:

```python
from iolanta.facets.textual_default import InverseProperties
from iolanta.facets.facet import Facet

assert issubclass(InverseProperties, Facet)    # ⇒ True    # noqa: S101
```

Check out [:material-github: the source code](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_default/facets.py#L142) of this class: it defines `show()` method which Iolanta will call to render inverse properties for an IRI on screen.

### Where to get Python facets from?

* A number of facets are bundled with Iolanta;
* More facets can be installed with Iolanta plugins from [PyPI](https://pypi.org/);
* and, you can write your own — it is enough for Iolanta to be able to import them.

## More facet types

!!! "info" "TBD"
    WASM powered plugins are on the Iolanta roadmap. They will enable users to run visualizations downloading them dynamically from the Web, and do so safely.
