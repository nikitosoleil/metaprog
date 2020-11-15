import re
from enum import Enum

re_s_single_no_prefix = r"[\'\"][^\"\\\n]*(?:\\([ntrbfav\/\\\"'])[^\"\\\n]*)*[\'\"]"
re_s_triple_no_prefix = r"(\"\"\"|\'\'\')[^\"\'\\]*(?:\\([ntrbfav\/\\\"\'])[^\"\'\\]*)*(\"\"\"|\'\'\')"
re_s_single = r"[bru]?" + re_s_single_no_prefix
re_s_triple = r"[bru]?" + re_s_triple_no_prefix
# TODO: separate quote and apostrophe

re_s_single_f_prefix = "f" + re_s_single_no_prefix
re_s_triple_f_prefix = "f" + re_s_triple_no_prefix
# TODO: make use of *_f_prefix

re_comments = r"#.*\n"
re_whitespaces = r"\s+"
re_tokens = r"[a-zA-Z_][a-zA-Z_0-9]*"


class TokenType(Enum):
    NOT_PARSED = 0
    TRIPLE_STRING = 1
    SINGLE_STRING = 2
    COMMENT = 3
    WHITESPACE = 4
    OBJECT = 5


class ObjectType(Enum):
    CLASS = 0
    FUNCTION = 1
    VARIABLE = 2


def __split(parsed, re_cur, match_type):
    new_parsed = []
    for content, token_type in parsed:
        if token_type == TokenType.NOT_PARSED:
            prv_end = 0

            for match in re.finditer(re_cur, content):
                start, end = match.span()
                not_parsed = content[prv_end:start]

                if len(not_parsed) > 0:
                    new_parsed.append((not_parsed, TokenType.NOT_PARSED))

                new_parsed.append((content[start:end], match_type))

                prv_end = end

            not_parsed = content[prv_end:]
            if len(not_parsed) > 0:
                new_parsed.append((not_parsed, TokenType.NOT_PARSED))
        else:
            new_parsed.append((content, token_type))
    return new_parsed


def parse(contents):
    parsed = [(contents, TokenType.NOT_PARSED)]
    for re_cur, match_type in [(f"({re_s_triple})|({re_s_triple_f_prefix})", TokenType.TRIPLE_STRING),
                               (f"({re_s_single})|({re_s_single_f_prefix})", TokenType.SINGLE_STRING),
                               (re_comments, TokenType.COMMENT),
                               (re_whitespaces, TokenType.WHITESPACE),
                               (re_tokens, TokenType.OBJECT)]:
        parsed = __split(parsed, re_cur, match_type)
    
    return parsed


def find_declared(parsed):
    prv_tokens = [None] + parsed[:-1]
    prv_tokens_white = [None] + parsed[:-1]
    nxt_tokens = parsed[1:] + [None]
    nxt_tokens_white = parsed[1:] + [None]
    for i in range(1, len(parsed)):
        if prv_tokens[i][1] == TokenType.WHITESPACE:
            prv_tokens[i] = prv_tokens[i - 1]
        if nxt_tokens[-i - 1][1] == TokenType.WHITESPACE:
            nxt_tokens[-i - 1] = nxt_tokens[-i]

    declared = []
    in_def, in_lambda, in_for, in_eq = False, False, False, False
    balance = 0
    for cur, prv, nxt, prv_white, cur_white in zip(parsed, prv_tokens, nxt_tokens, prv_tokens_white, nxt_tokens_white):
        if cur[1] == TokenType.WHITESPACE:
            if prv[0] != '\\' and '\n' in cur[0]:
                in_eq = False
            continue

        if cur[1] == TokenType.NOT_PARSED:
            for c in cur[0]:
                if c in '[{(':
                    balance += 1
                if c in ']})':
                    balance -= 1

                if c == '=':
                    in_eq = True

        if ':' in cur[0]:  # TODO: consider dicts as default argument values
            in_def = False
        if ':' in cur[0]:
            in_lambda = False
        if cur[0] == 'in':
            in_for = False

        if cur[1] == TokenType.OBJECT and balance == 0:
            if prv is not None and prv[0] == 'class':
                declared.append((cur[0], ObjectType.CLASS))
            elif prv is not None and prv[0] == 'def':
                declared.append((cur[0], ObjectType.FUNCTION))
            elif (prv is not None and prv[0] == 'as') or \
                    (nxt is not None and not in_eq and
                     ((nxt[0][0] == '=' and (len(nxt[0]) == 1 or nxt[0][1] not in '=<>'))
                      or nxt[0] == ',')) or \
                    (in_def or in_lambda or in_for):
                declared.append((cur[0], ObjectType.VARIABLE))

        if cur[0] == 'def':
            in_def = True
        if cur[0] == 'lambda':
            in_lambda = True
        if cur[0] == 'for':
            in_for = True

    print('\n'.join(f'{d[0]}, {d[1]}' for d in declared), '\n\n\n')

    return declared


def process(all_contents):
    all_parsed = [parse(contents) for contents in all_contents]
    all_declared = [find_declared(parsed) for parsed in all_parsed]
    return []
