{% for group in groups %}
{% if group.title %}
## {{ group.title }}
{% endif %}

<div class="grid cards" markdown>

{% for term in group.terms %}
-   __[{{ term.title }}]({{ term.uri }})__
{% if term.comment %}

    ---

    {{ term.comment | trim }}
{% endif %}

{% endfor %}
</div>

{% endfor %}
