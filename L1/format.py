import logging


def formatter(parsed, parsed_whitespace_prefixes, parsed_lines, file_path, config):
    augemented, augemented_whitespace_prefixes, augmented_lines = [], [], []
    for cur, nxt, prf, line in zip(parsed, parsed[1:] + [None], parsed_whitespace_prefixes, parsed_lines):
        augemented.append(cur)
        augemented_whitespace_prefixes.append(prf)
        augmented_lines.append(line)
        if (cur in {'{', '[', ','} and nxt != '\n') or \
                (cur in {']', '}'} and nxt not in {'\n', ','}) or \
                (nxt in {']', '}'} and cur != '\n'):
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
    level = 0
    prefix_cur, prefix_next = '', ''
    for token, prv_token, prv_token_true, nxt_token, nxt_token_true, whitespace_prefix, line in \
            zip(parsed, prv_tokens, prv_tokens_true, nxt_tokens, nxt_tokens_true,
                parsed_whitespace_prefixes, parsed_lines):
        if token in {'{', '['}:
            level += 1
        if token in {'}', ']'}:
            level -= 1

        error_reasoning = ''

        if token == '\n':
            spaces = level * config['indent']
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
            consequent_n += 1
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
            if consequent_n <= config['keep_maximum_blank_lines'] + 1:
                prefix_next = '\n' + prefix_next
            token = ''

        final_prefix = prefix_cur + prefix
        result += final_prefix + token
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
