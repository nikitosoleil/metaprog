import argparse
import glob
import os
import json
import logging

from parse import parser
from format import formatter

if __name__ == '__main__':
    file_handler = logging.FileHandler('errors.log', 'w')
    file_handler.setLevel(logging.ERROR)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    ap = argparse.ArgumentParser(description="A simple tool for formatting .json files")
    ap.add_argument('-p', type=str, default=None, help="Path to project to format JSON files in")
    ap.add_argument('-d', type=str, default=None, help="Directory to format JSON files in")
    ap.add_argument('-f', type=str, default=None, help="JSON file(s) to format")
    ap.add_argument('-v', '--verify', action='store_true', help="Verify file syntax")
    ap.add_argument('-c', '--config', type=str, default=None, help="Format file using specified config")
    ap.add_argument('-o', '--output', type=str, default=None, help="Output path prefix")
    args = ap.parse_args()

    # print(args)

    not_nones = [arg for arg in ['p', 'd', 'f'] if getattr(args, arg) is not None]

    if len(not_nones) != 1:
        raise ValueError('One and only one argument in (p, d, f) must be specified')

    arg = not_nones[0]

    if arg == 'p':
        files = [os.path.join(path, file)
                 for path, folders, files in os.walk(args.p)
                 for file in files
                 if file.endswith('.json')]
    if arg == 'd':
        files = [os.path.join(args.d, file)
                 for file in os.listdir(args.d)
                 if file.endswith('.json')]
    if arg == 'f':
        files = glob.glob(args.f)

    logging.info(f'Found {len(files)} files')

    not_nones = [arg for arg in ['verify', 'config'] if getattr(args, arg) not in {None, False}]

    if len(not_nones) != 1:
        raise ValueError('One and only one argument in (v/verify, c/config) must be specified')

    arg = not_nones[0]

    if arg == 'verify':
        mode = 'verify'
        config = None
    else:
        mode = 'format'
        with open(args.config, 'r') as file:
            config = json.load(file)
        logger.info(f'Configuration is {config}')

    logging.info(f'Selected mode is "{mode}"')

    for file_path in files:
        with open(file_path, 'r') as file:
            contents = file.read()
        parsed = parser(contents, file_path)
        if mode == 'format':
            formatted = formatter(*parsed, file_path, config)
            output_file_path = file_path if args.output is None else os.path.join(args.output, file_path)
            output_file_folder = os.sep.join(output_file_path.split(os.sep)[:-1])
            os.makedirs(output_file_folder, exist_ok=True)
            with open(output_file_path, 'w') as file:
                file.write(formatted)
