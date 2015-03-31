#! /usr/bin/env python

import argparse
import sys

from ldif import LDIFParser, LDIFWriter


class LDIF(LDIFParser):
    def __init__(self, input, output):
        LDIFParser.__init__(self, input)
        self.writer = LDIFWriter(output)
        self.lookup = set()

    def handle(self, dn, entry):
        if dn in self.lookup.keys():
            print 'Filtered dn: {}'.format(dn)
        else:
            self.lookup.add(dn)
            self.writer.unparse(dn, entry)


def arguments():
    '''
    Setup arugment parser.
    '''
    parser = argparse.ArgumentParser(
        description='''
            Utility to remove duplicate entries from a LDIF file. Will read
            in from a LDIF file, then write the filtered results to a
            specified output LDIF file.
        '''
    )
    parser.add_argument(
        '-i',
        '--input',
        dest='input',
        action='store',
        default=None,
        help='The input LDIF file.'
    )
    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        action='store',
        default=None,
        help='The output LDIF file.'
    )

    args = parser.parse_args()

    if None in [args.input, args.output]:
        parser.print_help()
        sys.exit(1)

    return args


def main():
    args = arguments()
    with open(args.output, 'w') as f:
        parser = LDIF(open(args.input, 'r'), f)
        parser.parse()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Ctrl-c caught. Exiting.'
        sys.exit(1)
