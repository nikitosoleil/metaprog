def formatter(parsed, config):
    result = ""
    prv_token = None
    consequent_n = 0
    for token, level in parsed:
        suffix = token
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
            indentation = '\t' * tabs + ' ' * spaces

            if token != '\n':
                prefix = '\n' + indentation
            else:
                suffix = ''
                if prv_token in {'{', '[', ','}:
                    prefix = '\n' + (indentation if config['keep_indents_on_empty_lines'] else '')
                else:
                    prefix = ''

        if token != '\n':
            prv_token = token
            consequent_n = 0
        else:
            consequent_n += 1

        if consequent_n <= config['keep_maximum_blank_lines']:
            result += prefix + suffix

    return result
