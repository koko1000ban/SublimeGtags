#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import re
import pprint
import unittest
from os.path import normpath, dirname

PP = pprint.PrettyPrinter(indent=4)

TAGS_RE = re.compile (
    '(?P<symbol>[^\s]+)\s+'
    '(?P<linenum>[^\s]+)\s+'
    '(?P<path>[^\s]+)\s+'
    '(?P<fields>.*)'
)

ENV_PATH = os.environ['PATH']

def find_tags_root(dir, pre=None):
    dir = normpath(dir)
    par = os.path.dirname(dir)
    if not os.path.exists(dir) or not os.path.isdir(dir):
        return None
    elif par == pre:
        return None

    for f in os.listdir(dir):
        if f == 'GTAGS':
            return dir
    return find_tags_root(par, dir)


class TagFile(object):
    def __init__(self, root_dir=None):
        self.__env = {'PATH' : ENV_PATH}
        self.__root = root_dir

        if root_dir is not None:
            self.__env['GTAGSROOT'] = os.path.expandvars(os.path.expanduser(root_dir))

    def start_with(self, prefix):
        out = subprocess.Popen(['global', '-c', prefix], stdout=subprocess.PIPE, env=self.__env).communicate()[0]
        return out.rstrip().splitlines()

    def match(self, pattern):
        out = subprocess.Popen(['global', '-a', '-x', pattern], stdout=subprocess.PIPE, env=self.__env).communicate()[0]
        lines = out.rstrip().splitlines()
        matches = []
        for search_obj in (t for t in (TAGS_RE.search(l) for l in lines) if t):
            matches.append(search_obj.groupdict())
        return matches

    def rebuild(self):
        out = subprocess.Popen(['gtags', '-vv'], cwd=self.__root, shell=1, env=self.__env).communicate()[0]

class GTagsTest(unittest.TestCase):
    def test_start_with(self):
        f = TagFile('$HOME/repos/work/val/e4/proto1/')
        assert len(f.start_with("Exp_Set")) == 4
    
    def test_match(pattern):
        f = TagFile('$HOME/repos/work/val/e4/proto1/')
        matches = f.match("ExpAddData")
        assert len(matches) == 4
        assert matches[0]["path"] == "/Users/tabi/Dropbox/repos/work/val/e4/proto1/include/ExpData.h"
        assert matches[0]["linenum"] == '1463'
    
    def test_start_with2(self):
        f = TagFile()
        assert len(f.start_with("Exp_Set")) == 0

if __name__ == '__main__':
    unittest.main()