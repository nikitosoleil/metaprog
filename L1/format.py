def formatter(parsed, config):
    augemented = []
    for cur, nxt in zip(parsed, parsed[1:] + [None]):
        augemented.append(cur)
        if (cur in {'{', '[', ','} and nxt != '\n') or \
                (cur in {']', '}'} and nxt not in {'\n', ','}) or \
                (nxt in {']', '}'} and cur != '\n'):
            augemented.append('\n')
    parsed = augemented

    prv_tokens = [None] + parsed[:-1]
    prv_tokens_true = [None] + parsed[:-1]
    nxt_tokens = parsed[1:] + [None]
    nxt_tokens_true = parsed[1:] + [None]
    for i in range(1, len(parsed)):
        if prv_tokens[i] == '\n':
            prv_tokens[i] = prv_tokens[i - 1]
        if nxt_tokens[-i - 1] == '\n':
            nxt_tokens[-i - 1] = nxt_tokens[-i]

    result = ""
    consequent_n = 0
    level = 0
    for token, prv_token, prv_token_true, nxt_token, nxt_token_true in \
            zip(parsed, prv_tokens, prv_tokens_true, nxt_tokens, nxt_tokens_true):
        if token in {'{', '['}:
            level += 1
        if token in {'}', ']'}:
            level -= 1

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
                    token += indentation
            else:
                token = ''
            consequent_n += 1
        else:
            consequent_n = 0
            if token == ',':
                prefix = ' ' if config['spaces_before_comma'] else ''
            elif token == ':':
                prefix = ' ' if config['spaces_before_:'] else ''
            elif prv_token == ':':
                prefix = ' ' if config['spaces_after_:'] else ''
            elif token == '}' and prv_token == '{':
                prefix = ' ' if config['spaces_within_braces'] else ''
            elif token == ']' and prv_token == '[':
                prefix = ' ' if config['spaces_within_brackets'] else ''
            else:
                prefix = ''

        if consequent_n > config['keep_maximum_blank_lines'] + 1 and token.startswith('\n'):
            token = token[1:]

        result += prefix + token

    return result
