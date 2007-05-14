# -*- coding: utf-8 -*-
"""
    werkzeug.debug.render
    ~~~~~~~~~~~~~~~~~~~~~

    Render the traceback debugging page.

    :copyright: 2007 by Georg Brandl, Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import pprint
from os.path import dirname, join

from werkzeug.utils import escape
from werkzeug.minitmpl import Template
from werkzeug.debug.util import Namespace


def get_template(name):
    return Template(load_resource(name).decode('utf-8'))


def load_resource(res):
    try:
        f = file(join(dirname(__file__), 'shared', res))
    except IOError:
        return ''
    try:
        return f.read()
    finally:
        f.close()


t_body = get_template('body.tmpl')
t_codetable = get_template('codetable.tmpl')
t_vartable = get_template('vartable.tmpl')


def code_table(frame):
    lines = []
    lineno = frame['context_lineno']
    if lineno is not None:
        lineno += 1
        for l in frame['pre_context']:
            lines.append(Namespace(mode='pre', lineno=lineno, code=l))
            lineno += 1
        lines.append(Namespace(mode='cur', lineno=lineno,
                               code=frame['context_line']))
        lineno += 1
        for l in frame['post_context']:
            lines.append(Namespace(mode='post', lineno=lineno, code=l))
            lineno += 1
    else:
        lines.append(Namespace(mode='cur', lineno=1,
                               code='Sourcecode not available'))

    return t_codetable.render(lines=lines)


def var_table(var):
    def safe_pformat(x):
        try:
            lines = pprint.pformat(x).splitlines()
        except:
            return '?'
        tmp = []
        for line in lines:
            if len(line) > 79:
                line = line[:79] + '...'
            tmp.append(line)
        return escape('\n'.join(tmp))

    # dicts
    if isinstance(var, dict) or hasattr(var, 'items'):
        value = var.items()
        if not value:
            typ = 'empty'
        else:
            typ = 'dict'
            value.sort()
            value = [(escape(repr(key)), safe_pformat(val))
                     for key, val in value]

    # lists
    elif isinstance(var, list):
        if not var:
            typ = 'empty'
        else:
            typ = 'list'
            value = [safe_pformat(item) for item in var]

    # others
    else:
        typ = 'simple'
        value = escape(repr(var))

    return t_vartable.render(type=typ, value=value)


def debug_page(context):
    tc = context.to_dict()
    tc['var_table'] = var_table
    tc['code_table'] = code_table
    return t_body.render(tc)
