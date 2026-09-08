# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Validation of the base config specification itself

A base config is data, and ycleptic reads only the keys it recognizes.  A
misspelled key or type name is therefore discarded without comment, leaving the
schema author with a declaration that silently does nothing --- a
``choices:`` list that never constrains anything, for instance.  The checks
here look over a base spec as it is loaded and report those declarations.
"""

from __future__ import annotations

import difflib

#: Keys ycleptic reads from an attribute node of a base config.
KNOWN_ATTRIBUTE_KEYS = frozenset(
    {
        'name',
        'type',
        'text',
        'default',
        'required',
        'choices',
        'case_sensitive',
        'attributes',
        'value_attributes',
        'value_type',
        'key_text',
        'list_defaults',
        'docs',
    }
)

#: Keys ycleptic reads from an attribute's ``docs`` block.
KNOWN_DOCS_KEYS = frozenset({'title', 'text', 'example'})

#: Keys ycleptic reads from the top level of a base config.
KNOWN_TOP_KEYS = frozenset({'attributes', 'docs'})

#: Type names ycleptic recognizes.
KNOWN_TYPES = frozenset({'str', 'int', 'float', 'bool', 'tuple', 'list', 'dict'})

#: Legal values of a list attribute's ``list_defaults`` key.
KNOWN_LIST_DEFAULTS = frozenset({'append', 'replace'})

#: Scalar types an element schema may declare via ``value_type``.
KNOWN_VALUE_TYPES = frozenset({'str', 'int', 'float', 'bool'})

#: Keys by which a node declares what lives under it.  At most one may appear.
ELEMENT_DECLARATIONS = ('attributes', 'value_attributes', 'value_type')

# Misspellings common enough to name outright rather than leave to difflib.
_KEY_ALIASES = {
    'option': 'choices',
    'options': 'choices',
    'allowed': 'choices',
    'allowed_values': 'choices',
    'attribute': 'attributes',
    'description': 'text',
    'help': 'text',
    'subattributes': 'attributes',
    'value': 'value_attributes',
    'values': 'value_attributes',
    'value_attribute': 'value_attributes',
    'additionalproperties': 'value_attributes',
    'key_help': 'key_text',
    'key_description': 'key_text',
    'item_type': 'value_type',
    'items': 'value_attributes',
    'element_type': 'value_type',
}

_LIST_DEFAULTS_ALIASES = {
    'add': 'append',
    'concat': 'append',
    'concatenate': 'append',
    'extend': 'append',
    'overwrite': 'replace',
    'override': 'replace',
    'supersede': 'replace',
}

_TYPE_ALIASES = {
    'array': 'list',
    'boolean': 'bool',
    'double': 'float',
    'integer': 'int',
    'map': 'dict',
    'mapping': 'dict',
    'number': 'float',
    'object': 'dict',
    'real': 'float',
    'sequence': 'list',
    'string': 'str',
    'text': 'str',
}


def _suggest(word, known, aliases):
    """
    Return a ``did you mean`` clause for ``word``, or an empty string.
    """
    if not isinstance(word, str):
        return ''
    alias = aliases.get(word.lower())
    if alias is None:
        close = difflib.get_close_matches(word.lower(), sorted(known), n=1, cutoff=0.7)
        alias = close[0] if close else None
    return f" (did you mean '{alias}'?)" if alias else ''


def _path_str(path: list[str]) -> str:
    return '->'.join(path) if path else 'the top level'


def _check_node(node: dict, path: list[str], problems: list[str]):
    where = f"attribute '{_path_str(path)}'"

    for key in node:
        if key not in KNOWN_ATTRIBUTE_KEYS:
            problems.append(
                f'{where}: unrecognized key '
                f"'{key}'{_suggest(key, KNOWN_ATTRIBUTE_KEYS, _KEY_ALIASES)}; it is ignored"
            )

    typ = node.get('type')
    if typ is None:
        problems.append(f"{where}: no 'type' declared")
    elif typ not in KNOWN_TYPES:
        problems.append(
            f"{where}: unrecognized type '{typ}'"
            f'{_suggest(typ, KNOWN_TYPES, _TYPE_ALIASES)}; the attribute is left unvalidated'
        )
    elif 'choices' in node and typ != 'str':
        problems.append(
            f"{where}: 'choices' is only enforced on 'str' attributes, "
            f"and this one is '{typ}'; the allowed values are not applied"
        )

    declared = [k for k in ELEMENT_DECLARATIONS if k in node]
    if len(declared) > 1:
        problems.append(
            f'{where}: declares {" and ".join(repr(k) for k in declared)}; a node describes '
            'what is under it exactly one way, so all but one are ignored'
        )

    for key in ('value_attributes', 'value_type'):
        if key in node and typ not in (None, 'dict', 'list'):
            problems.append(
                f"{where}: '{key}' describes the elements of a mapping or a list, "
                f"and this attribute is '{typ}'; it is not applied"
            )

    if 'value_type' in node and node['value_type'] not in KNOWN_VALUE_TYPES:
        problems.append(
            f"{where}: unrecognized value_type '{node['value_type']}'"
            f'{_suggest(node["value_type"], KNOWN_VALUE_TYPES, _TYPE_ALIASES)}; '
            'the elements are left unvalidated'
        )

    if 'key_text' in node:
        if not any(k in node for k in ('value_attributes', 'value_type')):
            problems.append(
                f"{where}: 'key_text' documents the free-form keys of a mapping declared with "
                "'value_attributes' or 'value_type', neither of which this attribute "
                'declares; it is ignored'
            )
        elif typ == 'list':
            problems.append(
                f"{where}: 'key_text' documents free-form keys, but a list's elements are "
                'positional and have no keys; it is ignored'
            )

    if 'list_defaults' in node:
        mode = node['list_defaults']
        if typ != 'list':
            problems.append(
                f"{where}: 'list_defaults' applies only to 'list' attributes, "
                f"and this one is '{typ}'; it is ignored"
            )
        elif 'attributes' in node:
            problems.append(
                f"{where}: 'list_defaults' governs how a plain list's 'default' merges with "
                "the user's, but this list declares 'attributes', so its items are walked as "
                'an ordered sequence of tasks and no default list is ever merged; it is ignored'
            )
        elif mode not in KNOWN_LIST_DEFAULTS:
            problems.append(
                f"{where}: unrecognized list_defaults '{mode}'"
                f'{_suggest(mode, KNOWN_LIST_DEFAULTS, _LIST_DEFAULTS_ALIASES)}; '
                'the default is added to the user list, not replaced by it'
            )

    docs = node.get('docs')
    if isinstance(docs, dict):
        for key in docs:
            if key not in KNOWN_DOCS_KEYS:
                problems.append(
                    f"{where}: unrecognized key '{key}' in its 'docs' block"
                    f'{_suggest(key, KNOWN_DOCS_KEYS, {})}; it is ignored'
                )

    for sub in node.get('attributes', []) or []:
        if isinstance(sub, dict):
            _check_node(sub, path + [str(sub.get('name', '?'))], problems)

    # A free-key node's value schema is ordinary attribute specs, so it gets the
    # same scrutiny; '[*]' in the path marks the step through an arbitrary key.
    for sub in node.get('value_attributes', []) or []:
        if isinstance(sub, dict):
            _check_node(sub, path + ['[*]', str(sub.get('name', '?'))], problems)


def check_base_spec(base: dict) -> list[str]:
    """
    Look over a base config specification and report declarations ycleptic ignores.

    Parameters
    ----------
    base : dict
        A base config specification, as loaded from a base config file.

    Returns
    -------
    list of str
        One message per problem found, in the order encountered.  Empty if the
        specification uses only keys and type names ycleptic recognizes.
    """
    problems: list[str] = []
    if not isinstance(base, dict):
        return problems
    for key in base:
        if key not in KNOWN_TOP_KEYS:
            problems.append(
                f'the top level: unrecognized key '
                f"'{key}'{_suggest(key, KNOWN_TOP_KEYS, _KEY_ALIASES)}; it is ignored"
            )
    for node in base.get('attributes', []) or []:
        if isinstance(node, dict):
            _check_node(node, [str(node.get('name', '?'))], problems)
    return problems


def format_problems(problems: list[str], basefile: str = '') -> str:
    """
    Render ``problems`` as a single multi-line report.
    """
    src = f' {basefile}' if basefile else ''
    ess = 's' if len(problems) > 1 else ''
    head = f'base config{src} has {len(problems)} declaration{ess} ycleptic does not act on:'
    return '\n'.join([head] + [f'  - {p}' for p in problems])
