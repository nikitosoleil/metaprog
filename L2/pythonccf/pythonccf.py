import argparse
import glob
import os
import logging

from .process import process


def main():
    ap = argparse.ArgumentParser(description="A simple tool for renaming and documenting Python code according to PEP")
    ap.add_argument('-p', type=str, default=None, help="Path to project to format .py files in")
    ap.add_argument('-d', type=str, default=None, help="Directory to format .py files in")
    ap.add_argument('-f', type=str, default=None, help=".py file(s) to format")
    ap.add_argument('-v', '--verify', action='store_true', help="Verify object names and documentation")
    ap.add_argument('-o', '--output', action='store_true', help="Output fixed files")
    ap.add_argument('--output-prefix', type=str, default='.', help="Output path prefix")
    args = ap.parse_args()

    file_handler = logging.FileHandler(os.path.join(args.output_prefix, 'verification.log'), 'w')
    file_handler.setLevel(logging.ERROR)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    not_nones = [arg for arg in ['p', 'd', 'f'] if getattr(args, arg) is not None]

    if len(not_nones) != 1:
        raise ValueError('One and only one argument in (p, d, f) must be specified')

    arg = not_nones[0]

    if arg == 'p':
        files = [os.path.join(path, file)
                 for path, folders, files in os.walk(args.p)
                 for file in files
                 if file.endswith('.py')]
    if arg == 'd':
        files = [os.path.join(args.d, file)
                 for file in os.listdir(args.d)
                 if file.endswith('.py')]
    if arg == 'f':
        files = glob.glob(args.f)

    logging.info(f'Found {len(files)} files')

    not_nones = [arg for arg in ['verify', 'output'] if getattr(args, arg) not in {None, False}]

    if len(not_nones) != 1:
        raise ValueError('One and only one argument in (v/verify, o/output) must be specified')

    mode = not_nones[0]
    logging.info(f'Selected mode is "{mode}"')

    all_contents = []
    for file_path in files:
        with open(file_path, 'r') as file:
            contents = file.read()
        all_contents.append(contents)

    results, msgs = process(all_contents, files)
    for file_path, line, ot, old, new in msgs:
        logging.error(f'{file_path}: {line} - {ot} NAMING ERROR: {old} should be {new}')

    if mode == 'output':
        for file_path, fixed in zip(files, results):
            output_file_path = os.path.join(args.output_prefix, file_path)
            output_file_folder = os.sep.join(output_file_path.split(os.sep)[:-1])
            os.makedirs(output_file_folder, exist_ok=True)
            with open(output_file_path, 'w') as file:
                file.write(fixed)
        with open(os.path.join(args.output_prefix, 'fixing.log'), 'w') as file:
            file.writelines([f'{file_path}: {line} - changed {old} to {new}\n'
                             for file_path, line, ot, old, new in msgs])
