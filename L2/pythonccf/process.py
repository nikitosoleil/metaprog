import re
from typing import List

from .find_declared import find_declared
from .parse import parse
from .types import TokenType, ObjectType


def rename(s: str, ot: ObjectType) -> str:
    """
    Find a proper name for an object

    :param s: object name
    :param ot: object type
    :return: proper name
    """
    new_s = s

    if ot == ObjectType.VARIABLE:
        if re.search('[a-z]', s) is None:
            return new_s  # exception: all caps variable is a constant

    pieces = []
    cur_piece = ''
    for c, prv_c in zip(s, '_' + s[:-1]):
        if c == '_' or (c.isupper() and prv_c.islower()):
            pieces.append(cur_piece)
            cur_piece = ''
        if c != '_':
            cur_piece += c
    pieces.append(cur_piece)

    if ot == ObjectType.CLASS:
        new_s = ''.join([p.lower().capitalize() for p in pieces])

    if ot == ObjectType.FUNCTION or ot == ObjectType.VARIABLE:
        new_s = '_'.join([p.lower() for p in pieces])

    return new_s


def process(all_contents: List[str], files: List[str]) -> (List[str], List):
    """
    Verify and fix given contents of files

    :param all_contents: all file contents
    :param files: paths to files
    :return: fixed files and error messages
    """
    all_parsed = [parse(contents) for contents in all_contents]

    all_declared = {}
    all_new_parsed = []
    for parsed, file in zip(all_parsed, files):
        # print('\n', file, '\n')
        declared, new_parsed = find_declared(parsed)
        all_new_parsed.append(new_parsed)
        for s, ot in declared:
            all_declared[s] = ot

    all_parsed = all_new_parsed

    old_new = {}
    for s, ot in all_declared.items():
        new_s = rename(s, ot)
        if s != new_s:
            old_new[s] = new_s

    prv_line = 0
    all_renamed, msgs = [], []
    for parsed, file_path in zip(all_parsed, files):
        renamed = []
        for p in parsed:
            s, tt, line = p
            if tt == TokenType.OBJECT and s in old_new:
                msgs.append({'type': 'rename',
                             'file_path': file_path,
                             'line': line,
                             'object_type': all_declared[s].name,
                             'old_token': s,
                             'new_token': old_new[s]})
                s = old_new[s]
            if tt == TokenType.DOCSTRING:
                old_s = s
                for old, new in old_new.items():
                    s = s.replace(old, new)
                if line is not None:
                    if old_s != s:
                        msgs.append({'type': 'fix_docstring',
                                     'file_path': file_path,
                                     'line': line})
                else:
                    msgs.append({'type': 'add_docstring',
                                 'file_path': file_path,
                                 'line': prv_line})
            prv_line = line
            renamed.append((s, tt))
        all_renamed.append(renamed)

    results = [''.join([r[0] for r in renamed]) for renamed in all_renamed]
    return results, msgs
