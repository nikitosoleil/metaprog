import logging


def formatter(parsed, parsed_whitespace_prefixes, parsed_lines, file_path, config):
    augemented, augemented_whitespace_prefixes, augmented_lines = [], [], []
    for cur, nxt, prf, line in zip(parsed, parsed[1:] + [None], parsed_whitespace_prefixes, parsed_lines):
        augemented.append(cur)
        augemented_whitespace_prefixes.append(prf)
        augmented_lines.append(line)
        if (cur in {'{', '[', ','} and nxt not in {'\n', '}', ']'}) or \
                (cur in {']', '}'} and nxt not in {'\n', ','}) or \
                (nxt in {']', '}'} and cur not in {'\n', '[', '{'}):
            augemented.append('\n')
            augemented_whitespace_prefixes.append(None)
            augmented_lines.append(None)
    parsed, parsed_whitespace_prefixes, parsed_lines = augemented, augemented_whitespace_prefixes, augmented_lines

    prv_tokens = [None] + parsed[:-1]
    prv_tokens_true = [None] + parsed[:-1]
    nxt_tokens = parsed[1:] + [None]
    nxt_tokens_true = parsed[1:] + [None]
    for i in range(1, len(parsed)):
        if prv_tokens[i].isspace():
            prv_tokens[i] = prv_tokens[i - 1]
        if nxt_tokens[-i - 1].isspace():
            nxt_tokens[-i - 1] = nxt_tokens[-i]

    result = ''
    consequent_n = 0
    indentation = ''
    prefix_cur, prefix_next = '', ''
    brackets = []
    for token, prv_token, prv_token_true, nxt_token, nxt_token_true, whitespace_prefix, line in \
            zip(parsed, prv_tokens, prv_tokens_true, nxt_tokens, nxt_tokens_true,
                parsed_whitespace_prefixes, parsed_lines):
        if token in {'{', '['}:
            brackets.append(token)
        if token in {'}', ']'}:
            brackets.pop(-1)

        last_bracket = brackets[-1] if len(brackets) != 0 else None
        next_bracket = None if last_bracket is None else ']' \
            if last_bracket == '[' else '}'
        wrapping_method = None if last_bracket is None else config['wrap_arrays'] \
            if last_bracket == '[' else config['wrap_objects']

        error_reasoning = ''

        if token == '\n':
            spaces = len(brackets) * config['indent']
            if nxt_token in {'}', ']'}:
                spaces -= config['indent']
            tabs = 0
            if config['use_tab_character']:
                tabs = spaces // config['tab_size']
                spaces = spaces % config['tab_size']
            indentation = '\t' * tabs + ' ' * spaces

            prefix = ''
            if prv_token != ':' and nxt_token not in {':', ','}:
                if config['keep_indents_on_empty_lines'] or nxt_token_true != '\n':
                    prefix_next += indentation
            else:
                token = ''
        else:
            consequent_n = 0
            if token == ',':
                prefix = ' ' if config['spaces_before_comma'] else ''
                error_reasoning = 'before , '
            elif token == ':':
                prefix = ' ' if config['spaces_before_:'] else ''
                error_reasoning = 'before : '
            elif prv_token == ':':
                prefix = ' ' if config['spaces_after_:'] else ''
                error_reasoning = 'after : '
            elif token == '}' and prv_token == '{':
                prefix = ' ' if config['spaces_within_braces'] else ''
                if '\n' not in whitespace_prefix:
                    error_reasoning = 'between { and } '
            elif token == ']' and prv_token == '[':
                prefix = ' ' if config['spaces_within_brackets'] else ''
                if '\n' not in whitespace_prefix:
                    error_reasoning = 'between [ and ] '
            else:
                prefix = ''

        if token == '\n':
            if wrapping_method in {'wrap_if_long'} and prv_token_true == ',' and nxt_token_true != '\n':
                prefix_next = ' '
            elif wrapping_method in {'do_not_wrap'} and prv_token_true == ',':
                prefix_next = ' '
            elif wrapping_method in {'do_not_wrap'} and (prv_token in {',', last_bracket} or nxt_token == next_bracket):
                prefix_next = ''
            elif consequent_n <= config['keep_maximum_blank_lines']:
                consequent_n += 1
                prefix_next = '\n' + prefix_next
            elif config['keep_indents_on_empty_lines']:
                prefix_next = ''
            token = ''

        final_prefix = prefix_cur + prefix
        final_append = final_prefix + token

        if wrapping_method == 'wrap_if_long':
            if not final_append.startswith('\n') and \
                    len((result + final_append).split('\n')[-1]) > config['hard_wrap_at']:
                final_append = '\n' + indentation + final_append.strip()

        result += final_append

        prefix_cur = prefix_next
        prefix_next = ''

        if whitespace_prefix is not None and final_prefix != whitespace_prefix:
            l, r = 0, 0
            for i in range(min(len(final_prefix), len(whitespace_prefix))):
                if final_prefix[i] == whitespace_prefix[i] and l == i:
                    l = i + 1
                if final_prefix[-i - 1] == whitespace_prefix[-i - 1] and r == -i:
                    r = -i - 1
            r = max(len(final_prefix), len(whitespace_prefix)) if r == 0 else -r
            final_prefix, whitespace_prefix = final_prefix[l:r], whitespace_prefix[l:r]
            if final_prefix != whitespace_prefix:
                logging.error(f'{file_path}: {line} - FORMAT ERROR: ' + error_reasoning +
                              f'must be {repr(final_prefix)}, found {repr(whitespace_prefix)}')

    return result
