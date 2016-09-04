#! /usr/bin/env python

import math


class UnitConverter(object):
    def __init__(self):
        self._unit_map = {
            'B': {'unit': None, 'scale': 1},
            'KB': {'unit': 'B', 'scale': 1000},
            'MB': {'unit': 'KB', 'scale': 1000},
            'GB': {'unit': 'MB', 'scale': 1000},
            'TB': {'unit': 'GB', 'scale': 1000},
            'KiB': {'unit': 'B', 'scale': 1024},
            'MiB': {'unit': 'KiB', 'scale': 1024},
            'GiB': {'unit': 'MiB', 'scale': 1024},
            'TiB': {'unit': 'GiB', 'scale': 1024}
        }

    def convert_to_bytes(self, target):
        '''
        Convert the human readable size to just byte in int form.
        Input expected format: `10.683 GB`, note the space.

        '''
        size_parts = target.split(' ')

        size = float(size_parts[0])
        unit = size_parts[1]

        while unit is not None:
            conversion = self._unit_map[unit]
            unit = conversion['unit']
            size = size * conversion['scale']
        return int(math.ceil(size))

    def convert_to_human_readable_size(self, size, numeration='decimal'):
        '''
        Get the bit length of the size value and divide by 10
        (equates to original by computed base log(2**10))
        '''
        if numeration == 'binary':
            scale = 1024
        elif numeration == 'decimal':
            scale = 1000
        else:
            raise ValueError('Unupported numeration type, use binary or decimal.')
        units = {
            'binary': ['B', 'KiB', 'MiB', 'GiB', 'TiB'],
            'decimal': ['B', 'kB', 'MB', 'GB', 'TB']
        }
        unit_offset = int(math.floor(math.log(size) / math.log(scale)))
        unit = units[numeration][unit_offset]
        return '{0} {1}'.format(round(float(size) / scale**unit_offset, 2), unit)
