import argparse
import glob
import os
import logging

from .process import process, rename, ObjectType


def main():
    ap = argparse.ArgumentParser(description="A simple tool for renaming and documenting Python code according to PEP")
    ap.add_argument('-p', type=str, default=None, help="Path to project to format .py files in")
    ap.add_argument('-d', type=str, default=None, help="Directory to format .py files in")
    ap.add_argument('-f', type=str, default=None, help=".py file(s) to format")
    ap.add_argument('-v', '--verify', action='store_true', help="Verify object names and documentation")
    ap.add_argument('-o', '--output', action='store_true', help="Output fixed files")
    ap.add_argument('--output-prefix', type=str, default='.', help="Output path prefix")
    args = ap.parse_args()

    os.makedirs(args.output_prefix, exist_ok=True)
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

    output_files = []
    for file_path in files:
        if arg == 'p':
            splits = os.path.split(file_path)
            output_splits = []
            for i, s in enumerate(splits):
                out_s = rename(s, ObjectType.FUNCTION)
                if out_s != s:
                    if i == len(splits) - 1:
                        msgs.append({'type': 'rename_file',
                                     'old_file': s,
                                     'new_file': out_s})
                    else:
                        msgs.append({'type': 'rename_directory',
                                     'old_dir': s,
                                     'new_dir': out_s})
                output_splits.append(out_s)

            output_file_path = os.path.join(args.output_prefix, *output_splits)
        else:
            output_file_path = os.path.join(args.output_prefix, file_path)

        output_files.append(output_file_path)

    msgs = [m for i, m in enumerate(msgs) if m not in msgs[:i]]

    for msg in msgs:
        if msg['type'] == 'rename':
            logging.error('{file_path}: {line} - {object_type} NAMING ERROR: {old_token} should be {new_token}'
                          .format(**msg))
        if msg['type'] == 'fix_docstring':
            logging.error('{file_path}: {line} - NAMING IN DOCSTRING ERROR'.format(**msg))
        if msg['type'] == 'add_docstring':
            logging.error('{file_path}: {line} - MISSING DOCSTRING ERROR'.format(**msg))
        if msg['type'] == 'rename_file':
            logging.error('{old_file} - FILENAME ERROR: should be {new_file}'.format(**msg))
        if msg['type'] == 'rename_directory':
            logging.error('{old_dir} - DIRECTORY NAME ERROR: should be {new_dir}'.format(**msg))

    if mode == 'output':
        for output_file_path, file_path, fixed in zip(output_files, files, results):
            output_file_folder = os.sep.join(output_file_path.split(os.sep)[:-1])
            os.makedirs(output_file_folder, exist_ok=True)
            with open(output_file_path, 'w') as file:
                file.write(fixed)
        with open(os.path.join(args.output_prefix, 'fixing.log'), 'w') as file:
            lines = []
            for msg in msgs:
                if msg['type'] == 'rename':
                    lines.append('{file_path}: {line} - changed {old_token} to {new_token}\n'.format(**msg))
                if msg['type'] == 'fix_docstring':
                    lines.append('{file_path}: {line} - fixed naming in docstring\n'.format(**msg))
                if msg['type'] == 'add_docstring':
                    lines.append('{file_path}: {line} - added docstring\n'.format(**msg))
                if msg['type'] == 'rename_file':
                    lines.append('{old_file} - FILENAME ERROR: renamed to {new_file}'.format(**msg))
                if msg['type'] == 'rename_directory':
                    lines.append('{old_dir} - DIRECTORY NAME ERROR: renamed to {new_dir}'.format(**msg))
            file.writelines(lines)
