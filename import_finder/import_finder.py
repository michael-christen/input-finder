"""Find directly imported modules.

TODO:
    - Properly ignore builtin packages
    - Add extensive tests
    - Fix ignore relative regex
"""
import click
import re
import os
import distutils.sysconfig as sysconfig

from .constants import STD_MODULES


# TODO: are we missing any regexes?
GLOBAL_IMPORT_RE = re.compile('^\s*import\s((?:\w|[.])+)(?:\sas\s(?:\w|[.])+)*$')
FROM_IMPORT_RE = re.compile('^\s*from\s((?:\w|[.])+)\simport\s((?:\w|[.*])+)(?:\sas\s(?:(?:\w|[.])+))*$')

def get_import_module_from_line(line):
    global_import = GLOBAL_IMPORT_RE.match(line)
    if global_import:
        return global_import.group(1)
    else:
        from_import = FROM_IMPORT_RE.match(line)

    if from_import:
        return '{}.{}'.format(from_import.group(1), from_import.group(2))


def get_base_module(module):
    return module.split('.')[0]


# list of standard modules
def std_module_list():
    ret_list = []
    std_lib = sysconfig.get_python_lib(standard_lib=True)
    # Walks through standard lib folders/files etc then returns list of modules
    for top, dirs, files in os.walk(std_lib):
        for nm in files:
            if nm != '__init__.py' and nm[-3:] == '.py':
                ret_list.append(os.path.join(top, nm)[len(std_lib)+1:-3].replace('\\','.'))
    return ret_list


def is_builtin_module(module):
    return get_base_module(module) in std_module_list()


@click.command()
@click.option('--ignore-relative/--no-ignore-relative', default=True)
@click.option('--ignore-builtin/--no-ignore-builtin', default=True)
def find(ignore_relative, ignore_builtin):
    with click.get_text_stream('stdin') as stdin:
        for line in stdin.readlines():
            module = get_import_module_from_line(line)
            if module:
                if module.startswith('.'):
                    if not ignore_relative:
                        click.echo('relative: %s' % module)
                    continue
                if is_builtin_module(module):
                    if not ignore_builtin:
                        click.echo('builtin: %s' % module)
                    continue
                click.echo(module)


if __name__ == '__main__':
    find()
