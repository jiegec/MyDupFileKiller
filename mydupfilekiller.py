# !/usr/bin/env python3
from hashlib import md5
import sys
import os


def find(paths, output=False):
    """
    A simple method to find all duplicate files.
    :param paths:  A list of paths.
    :param output: If True, it outputs the result to the console.
    :return: A tuple of (num,dict). The num is the number of files. The dict is like {hash : [files]}
    """
    hashes = dict()
    num = 0
    for path in paths:
        path = os.path.normpath(path)
        for root, dirs, files in os.walk(path):
            for name in files:
                filename = os.path.join(root, name)
                m = md5()
                f = open(filename, 'rb')
                buffer = 8192
                while 1:
                    chunk = f.read(buffer)
                    if not chunk:
                        break
                    m.update(chunk)
                f.close()
                digest = m.hexdigest()
                _list = list()
                if digest in hashes:
                    _list = hashes[digest]
                _list.append(filename)
                hashes[digest] = _list
                num += 1
                if output:
                    print("Processed %d files." % num)
    if output:
        print("Done.")
        for key in hashes:
            _list = hashes[key]
            if len(_list) > 1:
                print(key)
                for file in _list:
                    print(file)
                print('')
    return num, hashes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You need to specify at least one path.")
        sys.exit()
    find(sys.argv[1:], True)