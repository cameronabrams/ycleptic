# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
The ``make-doc`` subcommand implementation
"""

import os
import shutil
from . import __version__
from .stringthings import my_indent, dict_to_rst_yaml_block, generate_footer

def make_doc(L,topname,toptext,fp,docname='',doctext='',docexample={},rootdir='',footer_style='paragraph'):
    """
    Makes a sphinx/rtd-style doctree from the base config file provided including a root node.
    
    This is a recursive function that will create a directory structure based on the attributes and subattributes in the provided list `L`. It will create a main file with the name `topname` and write the documentation for the top-level attributes, as well as any subattributes or single-valued parameters.
    
    Parameters
    ----------
    L : list of dict
        List of attributes and subattributes to document.
    topname : str
        The name of the top-level documentation file (without extension).
    toptext : str
        The text to include at the top of the documentation file.
    fp : file-like object
        The file-like object to write the documentation to.
    docname : str, optional
        The name of the document (used in the title).
    doctext : str, optional
        The text to include in the document.
    docexample : dict, optional
        An example to include in the document, formatted as a dictionary.
    rootdir : str, optional
        The root directory for the documentation files.
    footer_style : str, optional
        The style of the footer to include in the documentation (default is "paragraph").
    
    """
    if docname=='':
        docname=f'``{topname}``'
    if doctext=='':
        doctext=toptext
    realpath=os.path.realpath(fp.name)
    thispath=realpath.replace(os.path.commonpath([rootdir,realpath]),'')
    if thispath[0]==os.sep:
        thispath=thispath[1:]
    thispath=os.path.splitext(thispath)[0]
    print(f'"{thispath}"')
    fp.write(f'.. _{" ".join(thispath.split(os.sep))}:\n\n')
    fp.write(f'{docname}\n{"="*(len(docname))}\n\n')
    if doctext:
        fp.write(f'{doctext}\n\n')
    if docexample:
        fp.write('Example:\n'+'+'*len('Example:')+'\n\n')
        # fp.write(f'Example:\n{"+"*len("Example:")}\n\n')
        fp.write(f'{dict_to_rst_yaml_block(docexample)}\n\n')
    svp=[d for d in L if 'attributes' not in d]
    svp_w_contdef=[d for d in svp if type(d.get('default',None)) in [dict,list]]
    svp_simple=[d for d in svp if not type(d.get('default',None)) in [dict,list]]
    sd= [d for d in L if 'attributes'     in d]
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
            docexample=sv.get('docs',{}).get('example',{})
            if docexample:
                fp.write(f'    Example:\n\n')
                fp.write(f'{my_indent(dict_to_rst_yaml_block(docexample),indent=4)}\n\n')
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
        fp.write(f'Subattribute{ess}:\n\n')
        fp.write('.. toctree::\n   :maxdepth: 1\n\n')
        for s in sd:
            fp.write(f'   {topname}/{s["name"]}\n')
        fp.write('\n\n')
    fp.write(generate_footer(app_name=__package__, version=__version__,style=footer_style))
    fp.close()
    if len(svp_w_contdef)>0:
        os.chdir(topname)
        for s in svp_w_contdef:
            name=s["name"]
            text=s.get('text','')
            default=s["default"] #must have
            doctext=s.get('docs',{}).get('text',text)
            docexample=s.get('docs',{}).get('example',{})
            with open(f'{name}.rst','w') as f:
                subpath=thispath+os.sep+name
                f.write(f'.. _{" ".join(subpath.split(os.sep))}:\n\n')
                f.write(f'``{name}``\n{"-"*(4+len(name))}\n\n')
                if type(default)==list:
                    for d in default:
                        f.write(f'  * {d}\n')
                elif type(default)==dict:
                    for k,v in default.items():
                        f.write(f'  * ``{k}``: {v}\n')
                f.write('\n\n')
                if doctext:
                    f.write(f'{doctext}\n\n')
                if docexample:
                    f.write('Example:\n'+'+'*len('Example:')+'\n\n')
                    f.write(f'{dict_to_rst_yaml_block(docexample)}\n\n')
                f.write(generate_footer(app_name=__package__, version=__version__,style=footer_style))
                f.close()
        os.chdir('..')
    if len(sd)>0:
        os.chdir(topname)
        for s in sd:
            name=s["name"]
            doc=s.get('docs',{})
            with open(f'{name}.rst','w') as f:
                make_doc(s['attributes'],name,s['text'],f,docname=doc.get('title',''),doctext=doc.get('text',''),docexample=doc.get('example',{}),rootdir=rootdir,footer_style=footer_style)
        os.chdir('..')

