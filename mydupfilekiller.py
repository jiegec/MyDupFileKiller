# !/usr/bin/env python3
from hashlib import md5
import sys
import os

if len(sys.argv) < 2:
    print("You need to specify at least one path.")
    sys.exit()

fileHashes = dict()
fileNum = 0
for i in range(1, len(sys.argv)):
    path = sys.argv[i]
    for root, dirs, files in os.walk(path):
        for name in files:
            fileName = os.path.join(root, name)
            m = md5()
            f = open(fileName, 'rb')
            buffer = 8192
            while 1:
                chunk = f.read(buffer)
                if not chunk:
                    break
                m.update(chunk)
            f.close()
            digest = m.hexdigest()
            if digest in fileHashes:
                fileList = fileHashes[digest]
            else:
                fileList = []
            fileList.append(fileName)
            fileHashes[digest] = fileList
            fileNum = fileNum + 1
            print("Processed %r files." % fileNum)
for key in fileHashes:
    fileList = fileHashes[key]
    if len(fileList) > 1:
        print(key)
        for file in fileList:
            print(file)
        print('\n')