import logging
import re
from enum import Enum
from functools import partial

string_re = r'"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"'
number_re = r'-?([1-9][0-9]*|0)(\.[0-9]+)?([eE][+-][0-9]+)?'
other_re = r'true|false|null'
all_re = '|'.join([string_re, number_re, other_re])


class States(Enum):
    START = 1

    DICT_START = 2
    DICT_STRING = 3
    DICT_COLON = 4
    DICT_VALUE = 5
    DICT_COMMA = 6

    ARRAY_START = 7
    ARRAY_VALUE = 8
    ARRAY_COMMA = 9

    END = 100


def is_value(token, what_re=all_re):
    return re.match(what_re, token) is not None


def parser(contents, file_path):
    tokens = []
    prv_r = 0
    n_line, prv_line_pos = 1, 0
    contents += 'null'
    while True:
        match = re.search(all_re, contents[prv_r:])
        if match is None:
            break
        l, r = match.span()
        value = contents[prv_r + l:prv_r + r]
        for i in range(l):
            char_pos = prv_r + i
            substr = contents[char_pos]
            if not substr.isspace() or substr == '\n':
                tokens.append((substr, n_line, char_pos - prv_line_pos))
            if substr == '\n':
                n_line += 1
                prv_line_pos = char_pos
        tokens.append((value, n_line, prv_r + l - prv_line_pos))
        prv_r += r
    tokens.pop(-1)

    brackets = []
    output_tokens = []
    total_errors = 0
    state = States.START
    prv_line = 0
    for token, line, char in tokens:
        if token == '\n':
            if line != prv_line:
                output_tokens.append((token, len(brackets)))
                prv_line = line
            continue

        was_error = [False]

        def __error(was_error, message):
            logging.error(f'{file_path}: {line} - {message}')
            was_error[0] = True

        error = partial(__error, was_error)

        # print(token, brackets, state)
        if state == States.START:
            if token == '{':
                state = States.DICT_START
                brackets.append('{')
            else:
                error('JSON must begin with {')
        elif state == States.DICT_START:
            if token == '}':
                brackets.pop(-1)
                if len(brackets) == 0:
                    state = States.END
                else:
                    if brackets[-1] == '{':
                        state = States.DICT_VALUE
                    else:
                        state = States.ARRAY_VALUE
            elif is_value(token, string_re):
                state = States.DICT_STRING
            else:
                error('String or } must be after {')
        elif state == States.DICT_STRING:
            if token == ':':
                state = States.DICT_COLON
            else:
                error('Colon must be after string')
        elif state == States.DICT_COLON:
            if token == '{':
                state = States.DICT_START
                brackets.append('{')
            elif token == '[':
                state = States.ARRAY_START
                brackets.append('[')
            elif is_value(token):
                state = States.DICT_VALUE
            else:
                error('Value must be after colon')
        elif state == States.DICT_VALUE:
            if token == ',':
                state = States.DICT_COMMA
            elif token == '}':
                brackets.pop(-1)
                if len(brackets) == 0:
                    state = States.END
                else:
                    if brackets[-1] == '{':
                        state = States.DICT_VALUE
                    else:
                        state = States.ARRAY_VALUE
            else:
                error(', or } must be after value')
        elif state == States.DICT_COMMA:
            if is_value(token, string_re):
                state = States.DICT_STRING
            else:
                error('String must be after ,')
        elif state == States.ARRAY_START:
            if token == ']':
                brackets.pop(-1)
                if brackets[-1] == '{':
                    state = States.DICT_VALUE
                else:
                    state = States.ARRAY_VALUE
            elif token == '{':
                state = States.DICT_START
                brackets.append('{')
            elif token == '[':
                state = States.ARRAY_START
                brackets.append('[')
            elif is_value(token):
                state = States.ARRAY_VALUE
            else:
                error('Value or ] must be after [')
        elif state == States.ARRAY_VALUE:
            if token == ',':
                state = States.ARRAY_COMMA
            elif token == ']':
                brackets.pop(-1)
                if brackets[-1] == '{':
                    state = States.DICT_VALUE
                else:
                    state = States.ARRAY_VALUE
            else:
                error(', or ] must be after value')
        elif state == States.ARRAY_COMMA:
            if token == '{':
                state = States.DICT_START
                brackets.append('{')
            elif token == '[':
                state = States.ARRAY_START
                brackets.append('[')
            elif is_value(token):
                state = States.ARRAY_VALUE
            else:
                error('Value must be after ,')
        elif state == States.END:
            error('JSON ended')

        if was_error[0]:
            total_errors += 1
        else:
            output_tokens.append((token, len(brackets)))
            prv_line = line

    if total_errors > 0:
        logging.error(f'File {file_path}: found {total_errors} error(s)')

    return output_tokens
