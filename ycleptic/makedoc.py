# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
The ``make-doc`` subcommand implementation
"""

from __future__ import annotations
import io
import logging
import shutil
from pathlib import Path
from . import __version__
from .stringthings import my_indent, dict_to_rst_yaml_block, generate_footer
from .walkers import subattributes

logger = logging.getLogger(__name__)


def make_doc(
    L: list[dict],
    topname: str,
    toptext: str,
    fp: io.TextIOWrapper,
    docname: str = '',
    doctext: str = '',
    docexample: dict | None = None,
    rootdir: str = '',
    footer_style: str = 'paragraph',
):
    """
    Makes a sphinx/rtd-style doctree from the base config file provided including a root node.

    This is a recursive function that will create a directory structure based on the attributes
    and subattributes in the provided list `L`. It will create a main file with the name `topname`
    and write the documentation for the top-level attributes, as well as any subattributes or
    single-valued attributes.

    Parameters
    ----------
    L : list of dict
        List of attributes and subattributes to document.
    topname : str
        The bare stem name of the current RST file (e.g. ``config_ref`` or ``attribute_1``).
        Used only for toctree entry generation; the actual output path is derived from ``fp``.
    toptext : str
        The text to include at the top of the documentation file.
    fp : io.TextIOWrapper
        Open file handle to write the documentation into.
    docname : str
        Title string for the document.  Optional; defaults to the topname in double backticks.
    doctext : str
        Introductory text for the document.  Optional; defaults to ``toptext``.
    docexample : dict
        Example to render as a YAML code block.  Optional.
    rootdir : str
        Absolute path to the Sphinx source directory.  Used to compute RST
        cross-reference labels relative to the source root.  Optional.
    footer_style : str
        Style of the auto-generated footer.  Optional; defaults to ``"paragraph"``.
    """
    if docexample is None:
        docexample = {}
    # Derive absolute paths from the open file handle so this function works
    # regardless of the process working directory.
    fp_path = Path(fp.name).resolve()
    rootpath = Path(rootdir).resolve() if rootdir else fp_path.parent
    rel = fp_path.with_suffix('').relative_to(rootpath)  # e.g. PosixPath('config_ref/attribute_1')
    outdir = fp_path.parent / fp_path.stem  # where sub-RST files are written

    if docname == '':
        docname = f'``{topname}``'
    if doctext == '':
        doctext = toptext

    logger.debug(f'"{rel}"')
    fp.write(f'.. _{" ".join(rel.parts)}:\n\n')
    fp.write(f'{docname}\n{"=" * (len(docname))}\n\n')
    if doctext:
        fp.write(f'{doctext}\n\n')
    if docexample:
        fp.write('Example:\n' + '+' * len('Example:') + '\n\n')
        fp.write(f'{dict_to_rst_yaml_block(docexample)}\n\n')

    # A free-key node carries its child schema in 'value_attributes' rather than
    # 'attributes'; it is a branch and must be documented as one, or the values
    # users actually write would go undocumented.
    svp = [d for d in L if subattributes(d) is None]
    svp_w_contdef = [d for d in svp if isinstance(d.get('default', None), (dict, list))]
    svp_simple = [d for d in svp if not isinstance(d.get('default', None), (dict, list))]
    sd = [d for d in L if subattributes(d) is not None]

    if any(isinstance(sv.get('default', None), (dict, list)) for sv in svp) or len(sd) > 0:
        if outdir.exists():
            shutil.rmtree(outdir)
        outdir.mkdir()

    if len(svp_simple) > 0:
        ess = 's' if len(svp_simple) > 1 else ''
        fp.write(f'Single-valued attribute{ess}:\n\n')
        for sv in svp_simple:
            default = sv.get('default', None)
            default_text = f' (default: {default})' if default is not None else ''
            fp.write(f'  * ``{sv["name"]}``: {sv["text"]}{default_text}\n\n')
            if 'choices' in sv:
                allowed = ', '.join(f'``{c}``' for c in sv['choices'])
                fp.write(f'    Allowed values: {allowed}\n\n')
            if 'value_type' in sv:
                if sv.get('type') == 'list':
                    fp.write(f'    Every item is a ``{sv["value_type"]}``.\n\n')
                else:
                    fp.write(
                        '    Keyed by names you choose; every value is a '
                        f'``{sv["value_type"]}``.\n\n'
                    )
                    if 'key_text' in sv:
                        fp.write(f'    Key: {sv["key_text"]}\n\n')
            sv_example = sv.get('docs', {}).get('example', {})
            if sv_example:
                fp.write('    Example:\n\n')
                fp.write(f'{my_indent(dict_to_rst_yaml_block(sv_example), indent=4)}\n\n')
        fp.write('\n\n')

    if len(svp_w_contdef) > 0:
        ess = 's' if len(svp_w_contdef) > 1 else ''
        fp.write(f'Container-like attribute{ess}:\n\n')
        fp.write('.. toctree::\n   :maxdepth: 1\n\n')
        for s in svp_w_contdef:
            fp.write(f'   {topname}/{s["name"]}\n')
        fp.write('\n\n')

    if len(sd) > 0:
        ess = 's' if len(sd) > 1 else ''
        fp.write(f'Subattribute{ess}:\n\n')
        fp.write('.. toctree::\n   :maxdepth: 1\n\n')
        for s in sd:
            fp.write(f'   {topname}/{s["name"]}\n')
        fp.write('\n\n')

    fp.write(
        generate_footer(app_name=__package__.split('.')[0], version=__version__, style=footer_style)
    )
    fp.close()

    if len(svp_w_contdef) > 0:
        for s in svp_w_contdef:
            name = s['name']
            default = s['default']
            text = s.get('text', '')
            sub_doctext = s.get('docs', {}).get('text', text)
            sub_example = s.get('docs', {}).get('example', {})
            sub_rel = rel / name
            with open(outdir / f'{name}.rst', 'w') as f:
                f.write(f'.. _{" ".join(sub_rel.parts)}:\n\n')
                f.write(f'``{name}``\n{"-" * (4 + len(name))}\n\n')
                if isinstance(default, list):
                    for d in default:
                        f.write(f'  * {d}\n')
                elif isinstance(default, dict):
                    for k, v in default.items():
                        f.write(f'  * ``{k}``: {v}\n')
                f.write('\n\n')
                if isinstance(default, list) and default:
                    if s.get('list_defaults', 'append') == 'replace':
                        f.write('A list you supply **replaces** these defaults entirely.\n\n')
                    else:
                        f.write(
                            'These defaults are **kept**, and a list you supply is added '
                            'after them.\n\n'
                        )
                if sub_doctext:
                    f.write(f'{sub_doctext}\n\n')
                if sub_example:
                    f.write('Example:\n' + '+' * len('Example:') + '\n\n')
                    f.write(f'{dict_to_rst_yaml_block(sub_example)}\n\n')
                f.write(
                    generate_footer(
                        app_name=__package__.split('.')[0], version=__version__, style=footer_style
                    )
                )

    if len(sd) > 0:
        for s in sd:
            name = s['name']
            doc = s.get('docs', {})
            subtext = s['text']
            if 'value_attributes' in s:
                # The elements here are the user's own, so the only way a reader
                # learns what to write is this sentence; say it before the schema.
                if s.get('type') == 'list':
                    subtext = (
                        f'{subtext}\n\nThis section is a list, and every item takes '
                        'the attributes below.'
                    )
                else:
                    key_text = s.get('key_text', '')
                    # key_text is the schema author's prose; a label avoids assuming
                    # anything about its capitalization or grammar
                    keydoc = f'\n\nKey: {key_text}' if key_text else ''
                    subtext = (
                        f'{subtext}\n\nThis section is keyed by names you choose; '
                        f'every value takes the attributes below.{keydoc}'
                    )
            with open(outdir / f'{name}.rst', 'w') as f:
                make_doc(
                    # sd holds only nodes that declare children, so this is never None
                    subattributes(s) or [],
                    name,
                    subtext,
                    f,
                    docname=doc.get('title', ''),
                    doctext=doc.get('text', '') if 'value_attributes' not in s else subtext,
                    docexample=doc.get('example', {}),
                    rootdir=str(rootpath),
                    footer_style=footer_style,
                )
