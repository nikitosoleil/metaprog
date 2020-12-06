from enum import Enum


class TokenType(Enum):
    NOT_PARSED = 0
    TRIPLE_STRING = 1
    SINGLE_STRING = 2
    COMMENT = 3
    WHITESPACE = 4
    OBJECT = 5
    DOCSTRING = 6


class ObjectType(Enum):
    CLASS = 0
    FUNCTION = 1
    VARIABLE = 2
