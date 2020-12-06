import re
from typing import List, Tuple

from .types import TokenType

re_s_single_apostrophe_no_prefix = r"[\'][^\'\\\n]*(?:\\([ntrbfav\/\\\'])[^\'\\\n]*)*[\']"
re_s_single_quotation_no_prefix = r"[\"][^\"\\\n]*(?:\\([ntrbfav\/\\\"])[^\"\\\n]*)*[\"]"
re_s_single_no_prefix = f"({re_s_single_apostrophe_no_prefix})|({re_s_single_quotation_no_prefix})"

re_s_triple_apostrophe_no_prefix = r"(\'\'\')[^\'\\]*(?:\\([ntrbfav\/\\\'])[^\'\\]*)*(\'\'\')"
re_s_triple_quotation_no_prefix = r"(\"\"\")[^\"\\]*(?:\\([ntrbfav\/\\\"])[^\"\\]*)*(\"\"\")"
re_s_triple_no_prefix = f"({re_s_triple_apostrophe_no_prefix})|({re_s_triple_quotation_no_prefix})"

re_s_single = r"[bru]?" + re_s_single_no_prefix
re_s_triple = r"[bru]?" + re_s_triple_no_prefix

re_s_single_f_prefix = "f" + re_s_single_no_prefix
re_s_triple_f_prefix = "f" + re_s_triple_no_prefix

re_comments = r"#.*\n"
re_whitespaces = r"\s+"
re_tokens = r"[a-zA-Z_][a-zA-Z_0-9]*"


def __split(parsed: List[Tuple[str, TokenType, int]], re_cur: str, match_type: TokenType) \
        -> List[Tuple[str, TokenType, int]]:
    """
    Extract via given regular expression tokens of a given type from a given list of not parsed tokens

    :param parsed: tokens, including not parsed
    :param re_cur: regular expression to use for token extraction
    :param match_type: type of extracted tokens
    :return: old and newly extracted tokens as a triple of token in string form, token type and token line
    """
    new_parsed = []
    for content, token_type, line_start in parsed:
        if token_type == TokenType.NOT_PARSED:
            prv_end = 0

            for match in re.finditer(re_cur, content):
                start, end = match.span()
                not_parsed = content[prv_end:start]

                if len(not_parsed) > 0:
                    new_parsed.append((not_parsed, TokenType.NOT_PARSED, line_start))

                line_start += not_parsed.count('\n')

                new_parsed.append((content[start:end], match_type, line_start))

                line_start += content[start:end].count('\n')

                prv_end = end

            not_parsed = content[prv_end:]
            if len(not_parsed) > 0:
                new_parsed.append((not_parsed, TokenType.NOT_PARSED, line_start))
        else:
            new_parsed.append((content, token_type, line_start))
    return new_parsed


def parse(contents: str) -> List[Tuple[str, TokenType, int]]:
    """
    Perform a lexical analysis on given file contents

    :param contents: file contents
    :return: parsed tokens as a triple of token in string form, token type and token line
    """
    parsed = [(contents, TokenType.NOT_PARSED, 1)]
    for re_cur, match_type in [(f"({re_s_triple})|({re_s_triple_f_prefix})", TokenType.TRIPLE_STRING),
                               (f"({re_s_single})|({re_s_single_f_prefix})", TokenType.SINGLE_STRING),
                               (re_comments, TokenType.COMMENT),
                               (re_whitespaces, TokenType.WHITESPACE),
                               (re_tokens, TokenType.OBJECT)]:
        parsed = __split(parsed, re_cur, match_type)
        # print([((c, tt) if tt != TokenType.NOT_PARSED else (len(c), tt)) for c, tt in parsed], '\n\n\n')

    # print([('WS' if tt == TokenType.WHITESPACE else (c, tt, line)) for c, tt, line in parsed])
    return parsed
