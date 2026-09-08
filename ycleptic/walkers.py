# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Recursive functions that traverse the attribute tree for setting values
"""

from __future__ import annotations
import logging

from .dictthings import special_update
from .stringthings import raise_clean

logger = logging.getLogger(__name__)


def make_def(L: list[dict], H: dict, *args):
    """
    Recursively generates YAML-format default user-config hierarchy with default
    attribute values

    Parameters
    ----------
    L : list of dict
        The list of attributes to traverse (the "base config")
    H : dict
        The dictionary to populate with default values (the "user config")
    args : tuple
        The current attribute names to traverse in the hierarchy.
    """
    if len(args) == 1:
        name = args[0]
        try:
            item_idx = [x['name'] for x in L].index(name)
        except ValueError:
            raise_clean(ValueError(f'{name} is not a recognized attribute'))
        item = L[item_idx]
        for d in item.get('attributes', []):
            if 'default' in d:
                H[d['name']] = d['default']
            else:
                H[d['name']] = None
        if 'attributes' not in item:
            if 'default' in item:
                H[item['name']] = item['default']
            else:
                H[item['name']] = None
    elif len(args) > 1:
        arglist = list(args)
        nextarg = arglist.pop(0)
        args = tuple(arglist)
        try:
            item_idx = [x['name'] for x in L].index(nextarg)
        except ValueError:
            raise_clean(ValueError(f'{nextarg} is not a recognized attribute'))
        item = L[item_idx]
        make_def(item['attributes'], H, *args)


def mwalk(D1: dict, D2: dict):
    """
    Recursively updates the base config D1 with base config D2.  This is used when reading a user dotfile that defines a partial base config in addition to whatever the user app base config defines.

    Parameters
    ----------
    D1 : dict
        The base config dictionary to be updated.
    D2 : dict
        The base config dictionary that contains the new values to merge into D1.
        This is typically the user dotfile that defines a partial base config.
    """

    assert 'attributes' in D1
    assert 'attributes' in D2
    tld1 = [x['name'] for x in D1['attributes']]
    for d2 in D2['attributes']:
        if d2['name'] in tld1:
            logger.debug(f'Config attribute {d2["name"]} is in the dotfile')
            didx = tld1.index(d2['name'])
            d1 = D1['attributes'][didx]
            if 'attributes' in d1 and 'attributes' in d2:
                mwalk(d1, d2)
            else:
                d1.update(d2)
        else:
            D1['attributes'].append(d2)


def _scalar_type_ok(typ: str, value) -> bool:
    """
    Return True if ``value`` is acceptable for the declared scalar type ``typ``.

    ``bool`` is treated as distinct from ``int``/``float`` (a YAML boolean is its
    own kind and must not silently satisfy a numeric attribute), while an ``int``
    is accepted where a ``float`` is declared (widening). A YAML sequence (list)
    satisfies ``tuple``, since YAML has no native tuple type. ``str`` is not
    covered here; string attributes are validated through their ``choices``.
    """
    if typ == 'bool':
        return isinstance(value, bool)
    if typ == 'int':
        return isinstance(value, int) and not isinstance(value, bool)
    if typ == 'float':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if typ == 'tuple':
        return isinstance(value, (list, tuple))
    return True


def subattributes(node: dict) -> list[dict] | None:
    """
    Return the attribute specs describing what lives *under* ``node``.

    A node declares its children in one of two mutually exclusive ways:
    ``attributes`` names the legal keys, while ``value_attributes`` says the
    keys are the user's to choose and gives the schema every value must
    satisfy.  Returns ``None`` for a leaf, which has neither.

    Callers that only need to know "is this a branch?" should use this rather
    than testing for ``attributes`` directly, so free-key nodes are not
    mistaken for leaves.
    """
    if 'attributes' in node:
        return node['attributes']
    if 'value_attributes' in node:
        return node['value_attributes']
    return None


def _declared_type(dx: dict, dname: str) -> str:
    """
    Return the declared type of attribute spec ``dx``, or report its absence.

    Every attribute must declare a type; without one there is nothing to
    validate the user's value against.
    """
    typ = dx.get('type')
    if typ is None:
        raise_clean(ValueError(f"Attribute '{dx.get('name', '?')}' of '{dname}' declares no type."))
    return typ


LIST_DEFAULTS_MODES = ('append', 'replace')
"""Legal values of a list attribute's ``list_defaults`` key."""


def _list_defaults_mode(dx: dict, dname: str) -> str:
    """
    Return the ``list_defaults`` mode of list attribute spec ``dx``.

    Defaults to ``'append'``, which is ycleptic's historical behavior: a
    declared default list is prepended to whatever the user supplies.  A schema
    whose list defaults are meant to be *superseded* by the user rather than
    added to declares ``list_defaults: replace``.
    """
    mode = dx.get('list_defaults', 'append')
    if mode not in LIST_DEFAULTS_MODES:
        raise_clean(
            ValueError(
                f"Attribute '{dx.get('name', '?')}' of '{dname}' declares "
                f'list_defaults: {mode!r}; expected one of {", ".join(LIST_DEFAULTS_MODES)}.'
            )
        )
    return mode


def _fwalk(dx: dict, M: dict, dname: str):
    """
    Validate every value of a free-key mapping ``M`` against ``dx``'s
    ``value_attributes``.

    The keys of ``M`` are the user's own --- molecule names, reaction labels
    and the like --- so they are not checked against anything.  Each value is
    walked as if it were an ordinary attribute block, which fills in per-value
    defaults and rejects unknown keys *within* a value.

    Parameters
    ----------
    dx : dict
        The free-key attribute spec; must carry ``value_attributes``.
    M : dict
        The user's mapping.
    dname : str
        Name of the enclosing block, used in error messages.
    """
    name = dx.get('name', '?')
    if not isinstance(M, dict):
        raise_clean(
            ValueError(f"Attribute '{name}' of '{dname}' must be a mapping; found {type(M)}.")
        )
    spec = {'name': name, 'attributes': dx['value_attributes']}
    for key in list(M.keys()):
        if M[key] is None:
            M[key] = {}
        if not isinstance(M[key], dict):
            raise_clean(
                ValueError(
                    f"Entry '{key}' of '{name}' must be a mapping of its attributes; "
                    f'found value {M[key]!r} of type {type(M[key]).__name__}.'
                )
            )
        dwalk({**spec, 'name': f'{name}[{key}]'}, M[key])


def dwalk(D: dict, I: dict):
    """
    Recursively process the user's config-dict I by walking recursively through it
    along with the default config-specification dict D

    Parameters
    ----------
    D : dict
        The attribute specification dictionary to walk through.
    I : dict
        The user's config dictionary to be processed.
    """
    dname = D.get('name', 'root')
    if 'attributes' not in D:
        raise ValueError(f'Attribute {dname} has no attributes; cannot walk through it.')
    # get the name of each config attribute at this level in this block
    tld = [x['name'] for x in D['attributes']]
    if I is None:
        raise ValueError(
            f"Null dictionary found; expected a dict with key(s) {tld} under '{dname}'."
        )
    # The user's config file is a dictionary whose keys must match attribute names in the config
    ud = list(I.keys())
    for u in ud:
        if u not in tld:
            raise_clean(
                ValueError(f"Attribute '{u}' invalid; expecting one of {tld} under '{dname}'.")
            )
    # logger.debug(f'dwalk along {tld} for {I}')
    # for each attribute name
    for d in tld:
        # get its index in the list of attribute names
        tidx = tld.index(d)
        # get its dictionary; D['attributes'] is a list
        dx = D['attributes'][tidx]
        # logger.debug(f' d {d}')
        # get its type
        typ = _declared_type(dx, dname)
        if 'attributes' in dx and 'value_attributes' in dx:
            raise_clean(
                ValueError(
                    f"Attribute '{d}' of '{dname}' declares both 'attributes' and "
                    "'value_attributes'; a node either names its keys or accepts any key, "
                    'not both.'
                )
            )
        if typ == 'dict' and (d in I and not isinstance(I[d], dict)):
            raise_clean(
                ValueError(f"Attribute '{d}' of '{dname}' must be a dict; found {type(I[d])}.")
            )
        # logger.debug(f' - {d} typ {typ} I {I[d]}
        # logger.debug(f'- {d} typ {typ} I {I}')
        # if this attribute name does not already have a key in the result
        if d not in I:
            # logger.debug(f' -> not found {d}')
            # if it is a scalar
            if typ in ['str', 'int', 'float', 'bool', 'tuple']:
                # if it has a default, set it
                if 'default' in dx:
                    I[d] = dx['default']
                    # logger.debug(f' ->-> default {d} {I[d]}')
                # if it is flagged as required, die since it is not in the read-in
                elif 'required' in dx:
                    if dx['required']:
                        raise_clean(ValueError(f"Attribute '{d}' of '{dname}' requires a value."))
            # if it is a dict
            elif typ == 'dict':
                # if it is explicitly tagged as not required, do nothing
                if 'required' in dx:
                    if not dx['required']:
                        continue
                # whether required or not, set it as empty and continue the walk,
                # which will set defaults for all descendants
                if 'attributes' in dx:
                    I[d] = {}
                    dwalk(dx, I[d])
                elif 'value_attributes' in dx:
                    # keys are the user's to invent, so none are conjured here;
                    # any default mapping still gets its per-value defaults filled
                    I[d] = dx.get('default', {})
                    _fwalk(dx, I[d], dname)
                else:
                    I[d] = dx.get('default', {})
            elif typ == 'list':
                if 'required' in dx:
                    if not dx['required']:
                        continue
                I[d] = dx.get('default', [])
        # this attribute does appear in I
        else:
            if typ in ('int', 'float', 'bool', 'tuple') and not _scalar_type_ok(typ, I[d]):
                raise_clean(
                    ValueError(
                        f"Attribute '{d}' of '{dname}' must be of type {typ}; "
                        f'found value {I[d]!r} of type {type(I[d]).__name__}.'
                    )
                )
            if typ == 'str':
                case_sensitive = dx.get('case_sensitive', True)
                if not case_sensitive:
                    I[d] = I[d].casefold()
                # logger.debug(f'case_sensitive {case_sensitive}')
                if 'choices' in dx:
                    if not case_sensitive:
                        # just check the choices that were provided by the user
                        if I[d].casefold() not in [x.casefold() for x in dx['choices']]:
                            raise_clean(
                                ValueError(
                                    f"Attribute '{d}' of '{dx['name']}' must be one of {', '.join(dx['choices'])} (case-insensitive); found '{I[d]}'"
                                )
                            )
                    else:
                        # check the choices that were provided by the user
                        if I[d] not in dx['choices']:
                            raise_clean(
                                ValueError(
                                    f"Attribute '{d}' of '{dx['name']}' must be one of {', '.join(dx['choices'])}; found '{I[d]}'"
                                )
                            )
            elif typ == 'dict':
                # process descendants
                if 'attributes' in dx:
                    dwalk(dx, I[d])
                elif 'value_attributes' in dx:
                    I[d] = special_update(dx.get('default', {}), I[d])
                    _fwalk(dx, I[d], dname)
                else:
                    I[d] = special_update(dx.get('default', {}), I[d])
            elif typ == 'list':
                # process list-item children
                if 'attributes' in dx:
                    lwalk(dx, I[d])
                else:
                    # 'append' (the default) prepends the schema's default list to
                    # the user's; 'replace' honors the user's list verbatim, the
                    # default then applying only when the key is absent altogether
                    if _list_defaults_mode(dx, dname) == 'append':
                        defaults = dx.get('default', [])
                        I[d] = defaults + I[d]
            elif typ == 'tuple':
                if 'attributes' in dx:
                    raise_clean(
                        TypeError(f"Attribute '{d}' of '{dname}' cannot have subattributes.")
                    )
                # honor the user-provided sequence, storing it as a tuple
                I[d] = tuple(I[d])


def lwalk(D: dict, L: list[dict]):
    """
    Recursively processes a list of items L by walking recursively through it
    along with the default config-specification dict D

    Parameters
    ----------
    D : dict
        The attribute specification dictionary.
    L : list of dict
        The list of dictionary items to be processed against D.
    """
    assert 'attributes' in D
    tld = [x['name'] for x in D['attributes']]
    # logger.debug(f'lwalk on {tld}')
    for item in L:
        # check this item against its attribute
        itemname = list(item.keys())[0]
        # logger.debug(f' - item {item}')
        if itemname not in tld:
            raise_clean(
                ValueError(
                    f"Element '{itemname}' of list '{D['name']}' is not valid; expected one of {tld}"
                )
            )
        tidx = tld.index(itemname)
        dx = D['attributes'][tidx]
        typ = _declared_type(dx, D['name'])
        if typ in ['str', 'int', 'float']:
            # because a list attribute indicates an ordered sequence of tasks and we expect each
            # task to be a dictionary specifying the task and not a single scalar value,
            # we will ignore this one
            logger.debug(f"Scalar list-element-attribute '{dx}' in '{dx['name']}' ignored.")
        elif typ == 'dict':
            if not item[itemname]:
                item[itemname] = {}
            dwalk(dx, item[itemname])
        else:
            logger.debug(f"List-element-attribute '{itemname}' in '{dx['name']}' ignored.")
