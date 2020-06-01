#!/usr/bin/env bash

import argparse
import hashlib
import os
import shutil
import sys
import tarfile


class HashObject:
    def __init__(self, impl):
        self.impl = impl()

    def write(self, data):
        self.impl.update(data)

    def hexdigest(self):
        return self.impl.hexdigest()

    @staticmethod
    def SHA1():
        return HashObject(hashlib.sha1)


def compare(a, b):
    sha1_a = HashObject.SHA1()
    shutil.copyfileobj(a, sha1_a)
    sha1_b = HashObject.SHA1()
    shutil.copyfileobj(b, sha1_b)
    return sha1_a.hexdigest() == sha1_b.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("a")
    parser.add_argument("b")

    args = parser.parse_args()

    tar_a = tarfile.open(args.a)
    tar_b = tarfile.open(args.b)

    members_a = tar_a.getmembers()
    members_b = tar_b.getmembers()
    paths_a = [x.name for x in members_a if x.isfile()]
    paths_b = [x.name for x in members_b if x.isfile()]

    # check archive structure
    test_a = set([x[:x.index("/")] for x in paths_a])
    test_b = set([x[:x.index("/")] for x in paths_b])
    assert len(test_a) == 1 and len(test_b) == 1
    root_a = test_a.pop()
    root_b = test_b.pop()

    # trim root dir
    names_a = set([x[len(root_a)+1:] for x in paths_a])
    names_b = set([x[len(root_b)+1:] for x in paths_b])

    added = names_b - names_a
    for name in sorted(list(added)):
        print("   Added:", name)

    deleted = names_a - names_b
    for name in sorted(list(deleted)):
        print(" Deleted:", name)

    intersection = names_a & names_b
    for name in sorted(list(intersection)):
        file_a = tar_a.extractfile(os.path.join(root_a, name))
        file_b = tar_b.extractfile(os.path.join(root_b, name))
        assert file_a, "not found {}/{}".format(root_a, name)
        assert file_b, "not found {}/{}".format(root_b, name)
        if not compare(file_a, file_b):
            print("Modified:", name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
