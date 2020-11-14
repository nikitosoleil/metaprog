# PythonCCF

A simple tool for renaming and documenting Python code according to PEP

## Table of contents

* [Usage](#usage)
* [Requirements](#requirements)

# Usage

    python PythonCCF.py [args]
      
    optional arguments:  
      -h, --help            Show help message and exit  
      -p P                  Path to project to format .py files in  
      -d D                  Directory to format .py files in  
      -f F                  .py file(s) to format  
      -v, --verify          Verify object names and documentation  
      -o, --output          Output fixed files  
      --output-prefix       Output path prefix
      
### Usage example

    python PythonCCF.py -f examples/test*.py -o --output-prefix output

# Requirements

- python>=3.5