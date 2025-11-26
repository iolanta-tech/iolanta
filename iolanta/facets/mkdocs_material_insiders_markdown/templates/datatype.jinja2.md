# {{ label }}

<table>
<thead>
</thead>
<tbody>
{% if types %}
<tr>
<td>∈ Instance Of</td>
<td>{% for type in types %}<code><a href="{{ type.uri }}">{{ type.title }}</a></code>{% if not loop.last %}, {% endif %}{% endfor %}</td>
</tr>
{% endif %}
{% if superclasses %}
<tr>
<td>⊊ Subclass Of</td>
<td>{% for superclass in superclasses %}<code><a href="{{ superclass.uri }}">{{ superclass.title }}</a></code>{% if not loop.last %}, {% endif %}{% endfor %}</td>
</tr>
{% endif %}
</tbody>
</table>

{% if comment %}
{{ comment | safe }}
{% endif %}
