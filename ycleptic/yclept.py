# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""A class for handling specialized YAML-format input files"""
import argparse as ap
import importlib.metadata
import logging
import os
import shutil
import textwrap
import yaml
from collections import UserDict
from argparse import Namespace

logger=logging.getLogger(__name__)

__version__=importlib.metadata.version("ycleptic")

banner_message="""
    {} v. {}
    https://ycleptic.readthedocs.io/en/latest/

    Cameron F. Abrams <cfa22@drexel.edu>

    """.format(__package__.title(),__version__)

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
    def __init__(self,basefile,userfile='',rcfile=''):
        data={}
        with open(basefile,'r') as f:
            data["base"]=yaml.safe_load(f)
        if rcfile:
            with open(rcfile,'r') as f:
                rc=yaml.safe_load(f)
                _mwalk(data["base"],rc)
        super().__init__(data)
        self["user"]={}
        if userfile:
            with open(userfile,'r') as f:
                self["user"]=yaml.safe_load(f)
        _dwalk(self["base"],self["user"])
        self["basefile"]=basefile
        self["userfile"]=userfile
        self["rcfile"]=rcfile

    def console_help(self,arglist,end='',**kwargs):
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
        f=kwargs.get('write_func',print)
        interactive_prompt=kwargs.get('interactive_prompt','')
        exit_at_end=kwargs.get('exit_at_end',False)
        self.H=Namespace(base=self['base']['directives'],write_func=f,arglist=arglist,end=end,interactive_prompt=interactive_prompt,exit=exit_at_end)
        self._help()

    def make_doctree(self,topname='config_ref'):
        with open(f'{topname}.rst','w') as f:
            doc=self['base'].get('docs',{})
            _make_doc(self['base']['directives'],topname,'Top-level directives',f,docname=doc.get('title',''),doctext=doc.get('text',''))

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

    def _show_item(self,idx):
        H=self.H
        item=H.base[idx]
        end=H.end
        H.write_func(f'\n{item["name"]}:{end}')
        H.write_func(f'    {textwrap.fill(item["text"],subsequent_indent="      ")}{end}')
        if item["type"]!="dict":
            if "default" in item:
                H.write_func(f'    default: {item["default"]}{end}')
            if "choices" in item:
                H.write_func(f'    allowed values: {", ".join(item["choices"])}{end}')
            if item.get("required",False):
                H.write_func(f'    A value is required.{end}')

    def _endhelp(self):
        self.H.write_func('Thank you for using ycleptic\'s interactive help!')
        exit(0)

    def _show_path(self):
        self.H.write_func('\nbase|'+'->'.join(self.path))

    def _show_branch(self,idx,interactive=False):
        self._show_path()
        self._show_item(idx)
        self._show_subdirectives(interactive=interactive)

    def _show_leaf(self,idx):
        self._show_path()
        self._show_item(idx)

    def _show_subdirectives(self,interactive=False):
        H=self.H
        subds=[x["name"] for x in H.base]
        hassubs=['directives' in x for x in H.base]
        att=['']*len(subds)
        if interactive:
            subds+=['..','!']
            att+=[' up',' quit']
            hassubs+=[False,False]
        for m,h,a in zip(subds,hassubs,att):
            if h:
                c=' ->'
            else:
                c=''
            H.write_func(f'    {m}{c}{a}')

    def _get_help_choice(self,init_list):
        H=self.H
        if len(init_list)>0:
            choice=init_list.pop()
        else:
            choice='!'
            if H.interactive_prompt!='':
                choice=input(H.interactive_prompt)
        while choice=='' or not choice in [x["name"] for x in H.base]+['..','!']:
            if choice!='':
                H.write_func(f'{choice} not recognized.')
            if len(init_list)>0:
                choice=init_list.pop()
            else:
                choice='!'
                if H.interactive_prompt!='':
                    choice=input(H.interactive_prompt)
        return choice

    def _help(self):
        H=self.H
        self.basestack=[]
        self.path=[]
        init_keylist=H.arglist[::-1]
        if len(init_keylist)==0:
            self._show_subdirectives(H.interactive_prompt!='')
        choice=self._get_help_choice(init_keylist)
        while choice!='!':
            if choice=='..':
                if len(self.basestack)==0:
                    if H.exit:
                        self._endhelp()
                    return
                H.base=self.basestack.pop()
                if len(self.path)>0:
                    self.path.pop()
            else:
                downs=[x["name"] for x in H.base]
                idx=downs.index(choice)
                if len(init_keylist)==0:
                    self._show_item(idx)
                if 'directives' in H.base[idx]:
                    # this is not a leaf, but we just showed it
                    # so we history the base and reassign it
                    self.basestack.append(H.base)
                    self.path.append(choice)
                    H.base=H.base[idx]['directives']
                else:
                    # this is a leaf, and we just showed it,
                    # so we can dehistory it but keep the base
                    # since it might have more leaves to select
                    H.write_func(f'\nAll subdirectives at the same level as \'{choice}\':')
            if len(init_keylist)==0:
                self._show_path()
                self._show_subdirectives(H.interactive_prompt!='')
                if H.interactive_prompt=='':
                    return
            choice=self._get_help_choice(init_keylist)
        if H.exit:
            self._endhelp()
        return
    
def _make_doc(L,topname,toptext,fp,docname='',doctext=''):
    if docname=='':
        docname=f'``{topname}``'
    if doctext=='':
        doctext=toptext
    fp.write(f'{docname}\n{"="*(len(docname))}\n\n')
    fp.write(f'{doctext}\n\n')
    svp=[d for d in L if 'directives' not in d]
    svp_w_contdef=[d for d in svp if type(d.get('default',None)) in [dict,list]]
    svp_simple=[d for d in svp if not type(d.get('default',None)) in [dict,list]]
    sd= [d for d in L if 'directives'     in d]
    if any([type(sv.get('default',None)) in [dict,list] for sv in svp]) or len(sd)>0:
        if os.path.exists(topname):
            shutil.rmtree(topname)
        os.mkdir(topname)
    if len(svp_simple)>0:
        ess='s' if len(svp_simple)>1 else ''
        fp.write(f'Single-valued parameter{ess}:\n\n')
        for sv in svp_simple:
            default=sv.get('default',None)
            default_text=''
            parname=f'``{sv["name"]}``'
            if default!=None:
                default_text=f' (default: {default})'
            fp.write(f'  * {parname}: {sv["text"]}{default_text}\n\n')
        fp.write('\n\n')
    if len(svp_w_contdef)>0:
        ess='s' if len(svp_w_contdef)>1 else ''
        fp.write(f'Container-like parameter{ess}:\n\n')
        fp.write('.. toctree::\n   :maxdepth: 1\n\n')
        for s in svp_w_contdef:
            fp.write(f'   {topname}/{s["name"]}\n')
        fp.write('\n\n')

    if len(sd)>0:
        ess='s' if len(sd)>1 else ''
        fp.write(f'Subdirective{ess}:\n\n')
        fp.write('.. toctree::\n   :maxdepth: 1\n\n')
        for s in sd:
            fp.write(f'   {topname}/{s["name"]}\n')
        fp.write('\n\n')
    fp.close()
    if len(svp_w_contdef)>0:
        os.chdir(topname)
        for s in svp_w_contdef:
            name=s["name"]
            default=s["default"] #must have
            with open(f'{name}.rst','w') as f:
                f.write(f'``{name}``\n{"-"*(4+len(name))}\n\n')
                if type(default)==list:
                    for d in default:
                        f.write(f'  * {d}\n')
                elif type(default)==dict:
                    for k,v in default.items():
                        f.write(f'  * ``{k}``: {v}\n')
                f.write('\n\n')
                f.close()
        os.chdir('..')
    if len(sd)>0:
        os.chdir(topname)
        for s in sd:
            name=s["name"]
            doc=s.get('docs',{})
            with open(f'{name}.rst','w') as f:
                _make_doc(s['directives'],name,s['text'],f,docname=doc.get('title',''),doctext=doc.get('text',''))
        os.chdir('..')

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

def _mwalk(D1,D2):
    """With custom config from D2, update D1"""
    assert 'directives' in D1
    assert 'directives' in D2
    tld1=[x['name'] for x in D1['directives']]
    for d2 in D2['directives']:
        if d2['name'] in tld1:
            logger.debug(f'Config directive {d2["name"]} is in the dotfile')
            didx=tld1.index(d2['name'])
            d1=D1['directives'][didx]
            if 'directives' in d1 and 'directives' in d2:
                _mwalk(d1,d2)
            else:
                d1.update(d2)
        else:
            D1['directives'].append(d2)

def _dwalk(D,I):
    """Process the user's config-dict I by walking recursively through it 
       along with the default config-specification dict D
       
       I is the dict yaml-read from the user input
       D is thd config-specification dict yaml-read from the package resources
    """
    assert 'directives' in D # D must contain one or more directives
    # get the name of each config directive at this level in this block
    tld=[x['name'] for x in D['directives']]
    if I==None:
        raise ValueError(f'Null dictionary found; expected a dict with key(s) {tld} under \'{D["name"]}\'.')
    # The user's config file is a dictionary whose keys must match directive names in the config
    ud=list(I.keys())
    for u in ud:
        if not u in tld:
            raise ValueError(f'Directive \'{u}\' invalid; expecting one of {tld} under \'{D["name"]}\'.')
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
    # print(f'special update {dict1} {dict2}')
    for k,v in dict2.items():
        ov=dict1.get(k,None)
        if not ov:
            dict1[k]=v
        else:
            if type(v)==list and type(ov)==list:
                logger.debug(f'merging {v} into {ov}')
                for nv in v:
                    if not nv in ov:
                        logger.debug(f'appending {nv}')
                        ov.append(nv)
            elif type(v)==dict and type(ov)==dict:
                ov.update(v)
            else:
                dict1[k]=v # overwrite
    return dict1

def oxford(a_list,conjunction='or'):
    """insist on the use of the Oxford comma"""
    if not a_list: return ''
    if len(a_list)==1:
        return a_list[0]
    elif len(a_list)==2:
        return f'{a_list[0]} {conjunction} {a_list[1]}'
    else:
        return ", ".join(a_list[:-1])+f', {conjunction} {a_list[-1]}'

def makedoc(args):
    config=args.config
    root=args.root
    Y=Yclept(config)
    Y.make_doctree(root)

def config_help(args):
    config=args.config
    arglist=args.arglist
    exit_at_end=args.exit_at_end
    interactive=args.i
    interactive_prompt='help: ' if interactive else ''
    Y=Yclept(config)
    if args.write_func=='print':
        write_func=print
    Y.console_help(arglist,write_func=write_func,interactive_prompt=interactive_prompt,exit=exit_at_end)

def cli():
    commands={
        'make-doc':makedoc,
        'config-help':config_help,
    }
    helps={
        'make-doc':'Makes a sphinx/rtd-style doctree from the base config file provided and, optionally, a root node',
        'config-help':'Help on a base config file',
    }
    descs={
        'make-doc':'If you provide the name of a base configuration file for your app, and optionally, a root directive, this command will generate a sphinx/rtd-style doctree',
        'config-help':'If you provide the name of a base configuration file for your app, you can use this command to explore it the way a user would in your app'
    }
    parser=ap.ArgumentParser(description=textwrap.dedent(banner_message),formatter_class=ap.RawDescriptionHelpFormatter)
    subparsers=parser.add_subparsers()
    subparsers.required=False
    command_parsers={}
    for k in commands:
        command_parsers[k]=subparsers.add_parser(k,description=descs[k],help=helps[k],formatter_class=ap.RawDescriptionHelpFormatter)
        command_parsers[k].set_defaults(func=commands[k])
    command_parsers['make-doc'].add_argument('config',type=str,default=None,help='input base configuration file in YAML format')
    command_parsers['make-doc'].add_argument('--root',type=str,default=None,help='root directive to begin the doctree build from')
    command_parsers['config-help'].add_argument('config',type=str,default=None,help='input base configuration file in YAML format')
    command_parsers['config-help'].add_argument('arglist',type=str,nargs='*',default=[],help='space-separated directive tree traversal')
    command_parsers['config-help'].add_argument('--write-func',type=str,default='print',help='space-separated directive tree traversal')
    command_parsers['config-help'].add_argument('--i',type=bool,default=True,action=ap.BooleanOptionalAction,help='use help interactively')
    command_parsers['config-help'].add_argument('--exit-at-end',type=bool,default=True,action=ap.BooleanOptionalAction,help='exit after help')

    args=parser.parse_args()
    if hasattr(args,'func'):
        args.func(args)
    else:
        my_list=oxford(list(commands.keys()))
        print(f'No subcommand found. Expected one of {my_list}')