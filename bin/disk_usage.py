#! /usr/bin/env python

import datetime
import math
import operator
import os
import sys


'''
Python utility that takes a starting location in the file system as its only
argument. Will walk down from the start point.  Will not follow to other
mounts.  Will return the usage data for the current mount.  The largest 10
directories and largest 20 files located under the start point.
'''


def arguments():
    '''
    Proccess arguments passed to script.
    '''
    args = sys.argv

    # Test the number of arguments to verify one target
    if len(args) != 2:
        print 'You must one enter one directory to start from as an argument.'
        sys.exit(1)
    else:
        return args[1]


def assemble_results(
    usage,
    target,
    total_dirs,
    sorted_dirs,
    total_files,
    sorted_files
):
    '''
    Construct the results in a list ready for printing
    '''
    results = []

    results.append(
        '{0}% available disk space on {1}'.format(
            (round(float(usage[2]) / float(usage[0]), 4) * 100),
            target
        )
    )
    results.append(
        'Total: {0}\tUsed: {1}\tFree: {2}\n'.format(
            human_readable_size(usage[0]),
            human_readable_size(usage[1]),
            human_readable_size(usage[2])
        )
    )
    results.append(
        '{0}% of Total Inodes are free.'.format(
            (round(float(usage[5]) / float(usage[3]), 4) * 100)
        )
    )
    results.append(
        'Total Inodes: {0}\tUsed: {1}\tFree: {2}\n'.format(
            usage[3],
            usage[4],
            usage[5]
        )
    )
    results.append('Total directory count of {0}'.format(total_dirs))
    results.append(
        'The {0} largest directories are:\n'.format(
            len(sorted_dirs)
        )
    )
    results.append('{0}Directory'.format('Size'.ljust(9)))
    for directory, size in sorted_dirs:
        results.append(
            '{0}{1}'.format(
                human_readable_size(size).ljust(9),
                directory
            )
        )
    results.append('\n')
    results.append('Total file count of {0}'.format(total_files))
    results.append(
        'The {0} largest files are:\n'.format(
            len(sorted_files)
        )
    )
    results.append(
        '{0}{1}File'.format(
            'Size'.ljust(9),
            'Modified'.ljust(20)
        )
    )
    for filename, size, mtime in sorted_files:
        results.append(
            '{0}{1} {2}'.format(
                human_readable_size(size).ljust(9),
                datetime.datetime.fromtimestamp(mtime),
                filename
            )
        )
    return results


def disk_space(target):
    '''
    Get total, used, and free space at the target location's partition/mount
    '''
    st = os.statvfs(target)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    inodesfree = st.f_favail
    inodestotal = st.f_files
    inodesused = st.f_files - st.f_favail
    return (total, used, free, inodestotal, inodesused, inodesfree)


def get_files(target):
    '''
    Get file size and modified time for all files from the target directory and
    down.
    '''
    filelist = []
    total_files = 0
    dirdict = {}
    exclude_root_dirs = ['dev', 'proc', 'selinux']
    spin = spinning_cursor()
    # Walk the directory structure
    for root, dirs, files in os.walk(target):
        # Ignore mounts
        dirs[:] = filter(
            lambda dir: not os.path.ismount(os.path.join(root, dir)),
            dirs
        )
        # Filter system directories that do not contain pertinent files
        if root is '/':
            dirs[:] = filter(lambda dir: dir not in exclude_root_dirs, dirs)
        for name in files:
            # Construct absolute path for files
            filename = os.path.join(root, name)
            # Test for broken symlinks
            try:
                # Gather file information
                file_data = os.stat(filename)
            except OSError, e:
                if 'Errorno 2' in e:
                    continue
            # Create a tuple of filename, size, and modified time
            construct = filename, float(file_data.st_size), file_data.st_mtime
            # Get total file count
            total_files += 1
            if total_files % 5000 == 0:
                sys.stdout.write(spin.next())
                sys.stdout.write('\r')
                sys.stdout.flush()
            filelist = process_filelist(filelist, construct)
            # Now compute total size of files in each directory
            if root in dirdict:
                # Add size of file to its directory
                dirdict[root] += construct[1]
            else:
                # Create directory entry with base size
                dirdict[root] = construct[1]
    return (filelist, dirdict, total_files)


def human_readable_size(size):
    '''
    Get the bit length of the size value and divide by 10
    (equates to original by computed base log(2**10))
    '''
    unit_offset = int(math.floor(math.log(size) / math.log(1024)))
    unit = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'][unit_offset]
    return '{0}{1}'.format(round(float(size) / 1024**unit_offset, 2), unit)


def process_filelist(filelist, construct):
    '''
    Processes and sorts the filelist to keep the data set at the largest 20
    files.  This is for performance reasons.  By keeping a pruned data set, we
    do not face the penalties of extremely large ordered data sets in memory.
    '''
    if len(filelist) < 19:
        filelist.append(construct)
    elif len(filelist) == 19:
        filelist.append(construct)
        filelist = sorted(
            filelist,
            key=lambda files_list: files_list[1],
            reverse=True
        )
    elif construct[1] > filelist[-1][1]:
        filelist.append(construct)
        filelist = sorted(
            filelist,
            key=lambda files_list: files_list[1],
            reverse=True
        )
        filelist.pop()
    return filelist


def spinning_cursor():
    cursor = '/-\|'
    i = 0
    while 1:
        yield cursor[i]
        i = (i + 1) % len(cursor)


def main():
    target = arguments()

    usage = disk_space(target)
    sorted_files, raw_directories, total_files = get_files(target)

    sorted_dirs = sorted(
        raw_directories.iteritems(),
        key=operator.itemgetter(1),
        reverse=True
    )
    total_dirs = len(sorted_dirs)

    # Trim sorted dir list down to top 10 entries
    sorted_dirs = sorted_dirs[0:10]

    results = assemble_results(
        usage,
        target,
        total_dirs,
        sorted_dirs,
        total_files,
        sorted_files
    )

    print '\n'.join(results)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nCtrl-c caught. Exiting.'
        sys.exit(1)
