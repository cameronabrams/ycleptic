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
        'docs',
    }
)

#: Keys ycleptic reads from an attribute's ``docs`` block.
KNOWN_DOCS_KEYS = frozenset({'title', 'text', 'example'})

#: Keys ycleptic reads from the top level of a base config.
KNOWN_TOP_KEYS = frozenset({'attributes', 'docs'})

#: Type names ycleptic recognizes.
KNOWN_TYPES = frozenset({'str', 'int', 'float', 'bool', 'tuple', 'list', 'dict'})

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
