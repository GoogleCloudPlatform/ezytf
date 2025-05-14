### Implementation Order:
{% for item in stack_list -%}
{{ loop.index }}. {{ item }}
{% endfor %}