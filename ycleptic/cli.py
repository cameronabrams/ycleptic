# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Command-line interface for ycleptic
"""

from .yclept import Yclept, __version__
import argparse as ap
import textwrap
from .stringthings import oxford, banner_message

def makedoc(args):
    """
    Makes a sphinx/rtd-style doctree from the base config file provided including a root node.
    """
    config=args.config
    root=args.root
    footer_style=args.footer_style
    Y=Yclept(config)
    Y.make_doctree(root,footer_style=footer_style)

def config_help(args):
    """
    Provides help on a base config file, optionally traversing the directive tree.
    """
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
    command_parsers['make-doc'].add_argument('--root',type=str,default=None,help='root directory from which to begin the doctree build, relative to the current working directory')
    command_parsers['make-doc'].add_argument('--footer-style',type=str,default='paragraph',choices=['paragraph','comment','rubric','note','raw-html'],
                                             help='footer style for the generated documentation; one of "paragraph", "comment", "rubric", "note", or "raw-html"; default %(default)s')
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