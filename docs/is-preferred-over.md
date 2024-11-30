---
title: iolanta:is-preferred-over
hide: [navigation, toc]
---

# ≼ `iolanta:is-preferred-over`

<table>
    <tr>
        <th>Domain</th>
        <td><a href="/Facet">Facet</a></td>
    </tr>
    <tr>
        <th>Range</th>
        <td><a href="/Facet">Facet</a></td>
    </tr>
</table>

## By Example

```turtle
<python://iolanta.facets.textual_default.TextualDefaultFacet>
  iolanta:is-preferred-over
  <python://iolanta.facets.textual_default.InverseProperties> .
```

…means that `TextualDefaultFacet` is more preferable than `InverseProperties`.

When Iolanta is looking for a <a href="/Facet">Facet</a> to visualize a particular IRI it might find multiple suitable facets. Console based Iolanta user interface will present all of these as options. However, different facets might not be equally representative or useful.

This property helps define preferences among facets. Regardless of the IRI in question, or the output datatype, the property defines a partial ordering on available facets.
