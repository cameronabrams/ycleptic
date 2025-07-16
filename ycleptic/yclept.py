# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
A class for handling specialized YAML-format input files
"""

import logging
import os
import textwrap
import yaml
from collections import UserDict
from argparse import Namespace
from . import __version__
from .makedoc import make_doc
from .walkers import make_def, mwalk, dwalk

logger=logging.getLogger(__name__)

class Yclept(UserDict):
    """
    A class for handling specialized YAML-format input files, including a base config file and an optional user config file.  Inherits from :class:`collections.UserDict`.

    This class reads a base config file and an optional user config file to generate an overal instance configuration state. It allows for recursive processing of directives and subdirectives, and provides methods for generating documentation and interactive help.
    
    Parameters
    ----------
    basefile : str
        The path to the base config file.
    userfile : str, optional
        The path to the user config file. If not provided, an empty user config will be created.
    userdict : dict, optional
        A dictionary containing user-defined configurations. If provided, it will be used instead of reading from a user file.
    rcfile : str, optional
        The path to a resource config file that can be used to update the base config with additional settings. If not provided, no additional resource config will be applied.
    """

    def __init__(self,basefile,userfile='',userdict={},rcfile=''):
        data={}
        with open(basefile,'r') as f:
            data["base"]=yaml.safe_load(f)
        if rcfile:
            with open(rcfile,'r') as f:
                rc=yaml.safe_load(f)
                mwalk(data["base"],rc)
        super().__init__(data)
        self["user"]={}
        if userfile:
            with open(userfile,'r') as f:
                self["user"]=yaml.safe_load(f)
        elif userdict:
            self["user"]=userdict
        dwalk(self["base"],self["user"])
        self["basefile"]=basefile
        self["userfile"]=userfile
        self["rcfile"]=rcfile

    def console_help(self,arglist,end='',**kwargs):
        """
        Interactive help with base config structure
        
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

    def make_doctree(self,topname='config_ref',footer_style='paragraph'):
        """
        Generates a Sphinx-style documentation tree from the base config file, including a root node.
        """
        with open(f'{topname}.rst','w') as f:
            doc=self['base'].get('docs',{})
            rootdir=os.getcwd()
            make_doc(self['base']['directives'],topname,'Top-level directives',f,docname=doc.get('title',''),
                      doctext=doc.get('text',''),docexample=doc.get('example',{}), rootdir=rootdir,footer_style=footer_style)

    def dump_user(self,filename='complete-user.yaml'):
        """
        Generates a full dump of the processed user config, including all implied default values

        """
        with open(filename,'w') as f:
            f.write(f'# Ycleptic v {__version__}\n')
            f.write('# Dump of complete user config file\n')
            yaml.dump(self['user'],f)

    def make_default_specs(self,*args):
        """
        Generates a partial config based on NULL user input and specified
        hierarchy

        Parameters
        ----------
        args : str
            The names of the directives to include in the partial config.
        """
        holder={}
        make_def(self['base']['directives'],holder,*args)
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
                H.write_func(f'    allowed values: {", ".join([str(_) for _ in item["choices"]])}{end}')
            if item.get("required",False):
                H.write_func(f'    A value is required.{end}')
        else:
            if "default" in item:
                H.write_func(f'    default:{end}')
                for k,v in item["default"].items():
                    H.write_func(f'        {k}: {v}{end}')

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
    

