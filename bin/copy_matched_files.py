#! /usr/bin/env python

import argparse
import fnmatch
import os
import shutil
import sys


def arguments():
    '''
    Arg parser.
    '''
    parser = argparse.ArgumentParser(description='''
        Utility to find files matching a pattern within subdirectories of the
        source location.  It then copies the found files to the destination
        location.
        ''')
    parser.add_argument(
        '-d',
        '--destination',
        help='Location to copy the matched files to.',
        action='store',
        default=None
    )
    parser.add_argument(
        '-f',
        '--file_pattern',
        help='The pattern to match in the target file names.',
        action='store',
        default=None
    )
    parser.add_argument(
        '-s',
        '--source',
        help='Location to start the find search from.',
        action='store',
        default=None
    )
    args = parser.parse_args()

    if None in [args.destination, args.file_pattern, args.source]:
        print 'You must specify all arguments.'
        parser.print_help()
        sys.exit(1)
    return args


def gen_find(file_pattern, top):
    '''
    Will walk from the specified location down.

    Returns generator object of strings that are the files that match the
    specified pattern.
    '''
    for path, dir_list, file_list in os.walk(top):
        for name in fnmatch.filter(file_list, file_pattern):
            yield os.path.join(path, name)


def main():
    args = arguments()

    for target in gen_find(args.file_pattern, args.source):
        print 'Copying {0} to {1}.'.format(target, args.destination)
        shutil.copy(target, args.destination)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Caught Ctrl-c. Exiting.'
        sys.exit(1)
