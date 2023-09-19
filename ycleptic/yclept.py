# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""A class for handling specialized YAML-format input files"""
import yaml
from collections import UserDict
import textwrap
import logging
logger=logging.getLogger(__name__)
import importlib.metadata

__version__ = importlib.metadata.version("ycleptic")

class Yclept(UserDict):
    """A inherited UserDict class for handling controlled YAML input
    
    Keys
    ----
    basefile: str
        name of base config file
    userfile: str, optional
        name of user config file
    base: dict
        contents of base config file
    user: dict
        contents of user config file processed against the base config
    """
    def __init__(self,basefile,userfile=''):
        data={}
        with open(basefile,'r') as f:
            data["base"]=yaml.safe_load(f)
        super().__init__(data)
        self["user"]={}
        if userfile:
            with open(userfile,'r') as f:
                self["user"]=yaml.safe_load(f)
        _dwalk(self["base"],self["user"])
        self["basefile"]=basefile
        self["userfile"]=userfile

    def console_help(self,*args,end=''):
        """Interactive help with base config structure
        
        Usage
        -----
        If Y is an initialized instance of Yclept, then

        >>> Y.console_help()

        will show the name of the top-level directives and their
        respective help strings.  Each positional
        argument will drill down another level in the base-config
        structure.
        """
        _userhelp(self["base"]["directives"],print,*args,end=end)

    def dump_user(self,filename='complete-user.yaml'):
        """generates a full dump of the processed user config, including all implied default values
        
        Arguments
        ---------
        filename: str, optional
            name of file to write
        """
        with open(filename,'w') as f:
            f.write(f'# Ycleptic v {__version__} -- Cameron F. Abrams -- cfa22@drexel.edu\n')
            f.write('# Dump of complete user config file\n')
            yaml.dump(self['user'],f)

    def make_default_specs(self,*args):
        """generates a partial config based on NULL user input and specified
        hierachty
        
        Arguments
        ---------
        args: tuple
            directive hierachy to use as the root for the config
        """
        holder={}
        _make_def(self['base']['directives'],holder,*args)
        return holder

def _make_def(L,H,*args):
    """recursive generation of YAML-format default user-config hierarchy"""
    if len(args)==1:
        name=args[0]
        try:
            item_idx=[x["name"] for x in L].index(name)
        except:
            raise ValueError(f'{name} is not a recognized directive')
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
        _make_def(item["directives"],H,*args)

def _userhelp(L,logf,*args,end=''):
    """rescursive generation of help messages for directives and subdirectives"""
    if len(args)==0:
        logf(f'    Help available for {", ".join([dspec["name"] for dspec in L])}{end}')
    elif len(args)==1:
        name=args[0]
        try:
            item_idx=[x["name"] for x in L].index(name)
        except:
            raise ValueError(f'{name} is not a recognized directive')
        item=L[item_idx]
        logf(f'{item["name"]}:{end}')
        logf(f'    {textwrap.fill(item["text"],subsequent_indent="      ")}{end}')
        logf(f'    type: {item["type"]}{end}')
        if "default" in item:
            logf(f'    default: {item["default"]}{end}')
        if "choices" in item:
            logf(f'    allowed values: {", ".join(item["choices"])}{end}')
        if item.get("required",False):
            logf(f'    A value is required.{end}')
        if "directives" in item:
            _userhelp(item["directives"],logf,end=end)
    else:
        arglist=list(args)
        nextarg=arglist.pop(0)
        args=tuple(arglist)
        try:
            item_idx=[x["name"] for x in L].index(nextarg)
        except:
            raise ValueError(f'{nextarg} is not a recognized directive')
        item=L[item_idx]
        logf(f'{nextarg}->{end}')
        _userhelp(item['directives'],logf,*args,end=end)

def _dwalk(D,I):
    """Process the user's config-dict I by walking recursively through it 
       along with the default config-specification dict D
       
       I is the dict yaml-read from the user input
       D is thd config-specification dict yaml-read from the package resources
    """
    # get the name of each config directive at this level in this block
    assert 'directives' in D # D must contain one or more directives
    tld=[x['name'] for x in D['directives']]
    if I==None:
        raise ValueError(f'Null dictionary found; expected a dict with key(s) {tld} under \'{D["name"]}\'.')
    ud=list(I.keys())
    for u in ud:
        if not u in tld:
            raise ValueError(f'Directive \'{u}\' invalid; expecting one of {tld} under \'{D["name"]}\'.')
    # logger.debug(f'dwalk along {tld} for {I}')
    # for each directive name
    for d in tld:
        # get its index in the list of directive names
        tidx=tld.index(d)
        # get its dictionary
        dx=D['directives'][tidx]
        # logger.debug(f' d {d}')
        # get its type
        typ=dx['type']
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
                        raise Exception(f'Directive \'{d}\' of \'{D["name"]}\' requires a value.')
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
                    _dwalk(dx,I[d])
                else:
                    I[d]=dx.get('default',{})
            elif typ=='list':
                if 'required' in dx:
                    if not dx['required']:
                        continue
                I[d]=dx.get('default',[])
        # this directive does appear in I
        else:
            if typ=='str' and 'choices' in dx:
                # just check the choices that were provided by the user
                assert I[d] in dx['choices'],f'Directive \'{d}\' of \'{dx["name"]}\' must be one of {", ".join(dx["choices"])}'
            elif typ=='dict':
                # process descendants
                if 'directives' in dx:
                    _dwalk(dx,I[d])
                else:
                    special_update(dx.get('default',{}),I[d])
            elif typ=='list':
                # process list-item children
                if 'directives' in dx:
                    _lwalk(dx,I[d])
                else:
                    defaults=dx.get('default',[])
                    I[d]=defaults+I[d]

def _lwalk(D,L):
    assert 'directives' in D
    tld=[x['name'] for x in D['directives']]
    # logger.debug(f'lwalk on {tld}')
    for item in L:
        # check this item against its directive
        itemname=list(item.keys())[0]
        # logger.debug(f' - item {item}')
        if not itemname in tld:
            raise ValueError(f'Element \'{itemname}\' of list \'{D["name"]}\' is not valid; expected one of {tld}')
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
            _dwalk(dx,item[itemname])
        else:
            logger.debug(f'Warning: List-element-directive \'{itemname}\' in \'{dx["name"]}\' ignored.')

def special_update(dict1,dict2):
    """Update dict1 with values from dict2 in a "special" way so that
    any list values are appended rather than overwritten
    """
    print(f'special update {dict1} {dict2}')
    for k,v in dict2.items():
        ov=dict1.get(k,None)
        if not ov:
            dict1[k]=v
        else:
            if type(v)==list and type(ov)==list:
                for nv in v:
                    if not nv in ov:
                        ov.append(nv)
            elif type(v)==dict and type(ov)==dict:
                ov.update(v)
            else:
                dict1[k]=v # overwrite
    return dict1