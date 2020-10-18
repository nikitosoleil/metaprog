# JSONFormatter

A simple tool for verifying & formatting JSON files

## Table of contents

* [Usage](#usage)
* [Config](#config)
* [Requirements](#requirements)

# Usage

    python JSONFormatter.py [args]
    
    positional arguments:  
      config                Path to formatting config  
      
    optional arguments:  
      -h, --help            Show help message and exit  
      -p P                  Path to project to format JSON files in  
      -d D                  Directory to format JSON files in  
      -f F                  JSON file(s) to format  
      -v, --verify          Verify file syntax & formatting  
      -o, --output          Output fixed & formatted files  
      --output-prefix       Output path prefix
      
### Usage example

    python JSONFormatter.py config.json -f examples/test*.json -o --output-prefix output
    
# Config

Formatting config is a JSON file with following parameters:

- use_tab_character - boolean, whether to use tab character instead of spaces
- tab_size - integer, number of spaces to replace with a tab character
- indent - integer, number of spaces to use for a single level indentation
- keep_indents_on_empty_lines - boolean, whether to fill empty lines with indenting tabs or spaces
- spaces_within_braces - boolean, whether to separate two empty braces {} with a space
- spaces_within_brackets - boolean, whether to separate two empty brackets [] with a space
- spaces_before_comma - boolean, whether to put a space before comma ,
- spaces_before_: - boolean, whether to put a space before colon :
- spaces_after_: - boolean, whether to put a space after colon :
- keep_maximum_blank_lines - integer, how many of consequent empty lines are allowed
- hard_wrap_at - minimum length of line to apply wrapping to
- wrap_arrays - wrapping method to apply to arrays
- wrap_objects - wrapping method to apply to objects

### Config example

    {
      "use_tab_character": true,
      "tab_size": 4,
      "indent": 2,
      "keep_indents_on_empty_lines": false,
      "spaces_within_braces": false,
      "spaces_within_brackets": false,
      "spaces_before_comma": false,
      "spaces_before_:": false,
      "spaces_after_:": true,
      "keep_maximum_blank_lines": 2,
      "hard_wrap_at": 40,
      "wrap_arrays": "wrap_if_long",
      "wrap_objects": "wrap_always"
    }

# Requirements

- python>=3.5