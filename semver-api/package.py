#!/usr/bin/env python3

import sys


def pop(arg, required=True):
    if '--' + arg not in argv:
        if required:
            raise ValueError(f'--{arg} is required')
        return None

    index = argv.index('--' + arg)
    indexes = [index]
    values = []
    while True:
        index += 1
        if index >= len(argv) or argv[index].startswith('--'):
            break

        values.append(argv[index])
        indexes.insert(0, index)

    for index in indexes:
        argv.pop(index)

    return ' '.join(values)


def discover_version():
    # TODO: write a function to discover the version from the project. read the version from a file, or from the git tags/branches
    pass


argv = sys.argv[1:]

stack_name = pop('stack-name')
template_file = pop('template-file').removesuffix('api.yaml')
parameter_overrides = pop('parameter-overrides')

major, minor, patch = (pop('version') or discover_version()).split('.')
update_latest = pop('no-update-latest', False) is None

print('set -e;')

cmd = (
    'aws cloudformation deploy',
    '--stack-name', stack_name + '-api',
    '--template-file', template_file + 'api-shared.yaml',
    '--parameter-overrides', parameter_overrides,
    *argv
)
print('echo "Waiting for API shared stack to be created/updated...";', ' '.join(cmd), ';')

cmd = (
    'aws cloudformation deploy',
    '--stack-name', stack_name + f'-api-v{major}-{minor}',
    '--template-file', template_file + 'api-semver.yaml',
    '--parameter-overrides', parameter_overrides, f'Major={major}', f'Minor={minor}', f'Patch={patch}',
    *argv
)
print(f'echo "Waiting for API endpoint /v{major}.{minor} to be created/updated...";', ' '.join(cmd), ';')

cmd = (
    'aws cloudformation deploy',
    '--stack-name', stack_name + '-api-latest',
    '--template-file', template_file + 'api-latest.yaml',
    '--parameter-overrides', parameter_overrides, f'Major={major}', f'Minor={minor}', f'Patch={patch}',
    *argv
)

if update_latest:
    print(f'echo "Waiting for API endpoint /latest to be created/updated...";', ' '.join(cmd), ';')
