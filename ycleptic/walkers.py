# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Recursive functions that traverse the directive tree for setting values
"""
import logging

logger=logging.getLogger(__name__)

from .dictthings import special_update
from .stringthings import raise_clean

def make_def(L,H,*args):
    """
    Recursively generates YAML-format default user-config hierarchy
    
    Parameters
    ----------
    L : list of dict
        The list of directives to traverse (the "base config")
    H : dict
        The dictionary to populate with default values (the "user config")
    args : tuple
        The current directive names to traverse in the hierarchy.
    """
    if len(args)==1:
        name=args[0]
        try:
            item_idx=[x["name"] for x in L].index(name)
        except:
            raise_clean(ValueError(f'{name} is not a recognized directive'))
        item=L[item_idx]
        for d in item.get("directives",[]):
            if "default" in d:
                H[d["name"]]=d["default"]
            else:
                H[d["name"]]=None
        if not "directives" in item:
            if "default" in item:
                H[item["name"]]=item["default"]
            else:
                H[item["name"]]=None
    elif len(args)>1:
        arglist=list(args)
        nextarg=arglist.pop(0)
        args=tuple(arglist)
        try:
            item_idx=[x["name"] for x in L].index(nextarg)
        except:
            raise ValueError(f'{nextarg} is not a recognized directive')
        item=L[item_idx]
        make_def(item["directives"],H,*args)

def mwalk(D1,D2):
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

    assert 'directives' in D1
    assert 'directives' in D2
    tld1=[x['name'] for x in D1['directives']]
    for d2 in D2['directives']:
        if d2['name'] in tld1:
            logger.debug(f'Config directive {d2["name"]} is in the dotfile')
            didx=tld1.index(d2['name'])
            d1=D1['directives'][didx]
            if 'directives' in d1 and 'directives' in d2:
                mwalk(d1,d2)
            else:
                d1.update(d2)
        else:
            D1['directives'].append(d2)

def dwalk(D,I):
    """
    Recursively process the user's config-dict I by walking recursively through it
    along with the default config-specification dict D
    
    Parameters
    ----------
    D : dict
        The directive specification dictionary to walk through.
    I : dict
        The user's config dictionary to be processed.
    """
    if not 'directives' in D:
        raise ValueError(f'Directive {D["name"]} has no directives; cannot walk through it.')
    # get the name of each config directive at this level in this block
    tld=[x['name'] for x in D['directives']]
    if I==None:
        raise ValueError(f'Null dictionary found; expected a dict with key(s) {tld} under \'{D["name"]}\'.')
    # The user's config file is a dictionary whose keys must match directive names in the config
    ud=list(I.keys())
    for u in ud:
        if not u in tld:
            raise_clean(ValueError(f'Directive \'{u}\' invalid; expecting one of {tld} under \'{D["name"]}\'.'))
    # logger.debug(f'dwalk along {tld} for {I}')
    # for each directive name
    for d in tld:
        # get its index in the list of directive names
        tidx=tld.index(d)
        # get its dictionary; D['directives'] is a list
        dx=D['directives'][tidx]
        # logger.debug(f' d {d}')
        # get its type
        typ=dx['type']
        if typ=='dict' and (d in I and not type(I[d])==dict):
            raise_clean(ValueError(f'Directive \'{d}\' of \'{D["name"]}\' must be a dict; found {type(I[d])}.'))
        # logger.debug(f' - {d} typ {typ} I {I[d]}
        # logger.debug(f'- {d} typ {typ} I {I}')
        # if this directive name does not already have a key in the result
        if not d in I:
            # logger.debug(f' -> not found {d}')
            # if it is a scalar
            if typ in ['str','int','float', 'bool']:
                # if it has a default, set it
                if 'default' in dx:
                    I[d]=dx['default']
                    # logger.debug(f' ->-> default {d} {I[d]}')
                # if it is flagged as required, die since it is not in the read-in
                elif 'required' in dx:
                    if dx['required']:
                        raise_clean(ValueError(f'Directive \'{d}\' of \'{D["name"]}\' requires a value.'))
            # if it is a dict
            elif typ=='dict':
                # if it is explicitly tagged as not required, do nothing
                if 'required' in dx:
                    if not dx['required']:
                        continue
                # whether required or not, set it as empty and continue the walk,
                # which will set defaults for all descendants
                if 'directives' in dx:
                    I[d]={}
                    dwalk(dx,I[d])
                else:
                    I[d]=dx.get('default',{})
            elif typ=='list':
                if 'required' in dx:
                    if not dx['required']:
                        continue
                I[d]=dx.get('default',[])
        # this directive does appear in I
        else:
            if typ=='str':
                case_sensitive=dx.get('case_sensitive',True)
                if not case_sensitive:
                    I[d]=I[d].casefold()
                # logger.debug(f'case_sensitive {case_sensitive}')
                if 'choices' in dx:
                    if not case_sensitive:
                        # just check the choices that were provided by the user
                        if not I[d].casefold() in [x.casefold() for x in dx['choices']]:
                            raise_clean(ValueError(f'Directive \'{d}\' of \'{dx["name"]}\' must be one of {", ".join(dx["choices"])} (case-insensitive); found \'{I[d]}\''))
                    else:
                        # check the choices that were provided by the user
                        if not I[d] in dx['choices']:
                            raise_clean(ValueError(f'Directive \'{d}\' of \'{dx["name"]}\' must be one of {", ".join(dx["choices"])}; found \'{I[d]}\''))
            elif typ=='dict':
                # process descendants
                if 'directives' in dx:
                    dwalk(dx,I[d])
                else:
                    I[d]=special_update(dx.get('default',{}),I[d])
            elif typ=='list':
                # process list-item children
                if 'directives' in dx:
                    lwalk(dx,I[d])
                else:
                    defaults=dx.get('default',[])
                    I[d]=defaults+I[d]

def lwalk(D,L):
    """
    Recursively processes a list of items L by walking recursively through it
    along with the default config-specification dict D
    
    Parameters
    ----------
    D : dict
        The directive specification dictionary to walk through.
    L : list of dict
        The list of items to be processed, where each item is a dictionary.
    """
    assert 'directives' in D
    tld=[x['name'] for x in D['directives']]
    # logger.debug(f'lwalk on {tld}')
    for item in L:
        # check this item against its directive
        itemname=list(item.keys())[0]
        # logger.debug(f' - item {item}')
        if not itemname in tld:
            raise_clean(ValueError(f'Element \'{itemname}\' of list \'{D["name"]}\' is not valid; expected one of {tld}'))
        tidx=tld.index(itemname)
        dx=D['directives'][tidx]
        typ=dx['type']
        if typ in ['str','int','float']:
            # because a list directive indicates an ordered sequence of tasks and we expect each
            # task to be a dictionary specifying the task and not a single scalar value,
            # we will ignore this one
            logger.debug(f'Warning: Scalar list-element-directive \'{dx}\' in \'{dx["name"]}\' ignored.')
        elif typ=='dict':
            if not item[itemname]:
                item[itemname]={}
            dwalk(dx,item[itemname])
        else:
            logger.debug(f'Warning: List-element-directive \'{itemname}\' in \'{dx["name"]}\' ignored.')