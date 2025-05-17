---
hide: [toc]
---

# 📛 `when-no-facet-found`


<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Domain__

    ---

    [`rdfs:Datatype`](/reference/rdfs/datatype/)<br/>
    <small>Datatype of the value the facet returns</small>

-   :material-target-variant:{ .lg .middle } __Range__

    ---

    [`iolanta:Facet`](/Facet/)<br/>
    <small>Iolanta visualization</small>

</div>

No facet is found to visualize this `URI` in the form of this `datatype`. A pityful occasion. We could throw an ugly exception in this situation, or show a hard-coded error message; but instead let's specify a specially crafted facet which will provide a user friendly placeholder. That's what this property is for.
