def formatter(parsed, config):
    result = ""
    prv_token = None
    for token, level in parsed:
        if token == ',':
            prefix = ' ' if config['spaces_before_comma'] else ''
        elif token == ':':
            prefix = ' ' if config['spaces_before_:'] else ''
        elif prv_token == ':':
            prefix = ' ' if config['spaces_after_:'] else ''
        elif token in {'{', '['}:
            prefix = ''
        elif token == '}' and prv_token == '{' and config['spaces_within_braces']:
            prefix = ' '
        elif token == ']' and prv_token == '[' and config['spaces_within_brackets']:
            prefix = ' '
        else:
            spaces = level * config['indent']
            tabs = 0
            if config['use_tab_character']:
                tabs = spaces // config['tab_size']
                spaces = spaces % config['tab_size']
            prefix = '\n' + '\t' * tabs + ' ' * spaces
        result += prefix + token
        prv_token = token
    return result
