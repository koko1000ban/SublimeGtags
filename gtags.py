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
    def _expand_path(self, path):
        return os.path.expandvars(os.path.expanduser(path))
    
    def __init__(self, root_dir=None, extra_paths=[]):
        self.__env = {'PATH' : ENV_PATH}
        self.__root = root_dir

        if root_dir is not None:
            self.__env['GTAGSROOT'] = self._expand_path(root_dir)
            
        if extra_paths:
            self.__env['GTAGSLIBPATH'] = ":".join(map(self._expand_path, extra_paths))

    def start_with(self, prefix):
        out = subprocess.Popen(['global', '-c', prefix], stdout=subprocess.PIPE, env=self.__env).communicate()[0]
        return out.rstrip().splitlines()

    def _match(self, pattern, opts):
        command = ['global', pattern]
        command[1:1] = opts
        
        out = subprocess.Popen(command, stdout=subprocess.PIPE, env=self.__env).communicate()[0]
        lines = out.rstrip().splitlines()
        matches = []
        for search_obj in (t for t in (TAGS_RE.search(l) for l in lines) if t):
            matches.append(search_obj.groupdict())
        return matches
        
    
    def match(self, pattern):
        return self._match(pattern, ['-a', '-x'])

    def rmatch(self, pattern):
        return self._match(pattern, ['-a', '-x', '-r'])
    
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

    def test_reference(self):
        f = TagFile('$HOME/repos/work/val/e4/proto1/')
        refs = f.rmatch("Exp_IsSkipProgress")
        assert len(refs) == 22
        assert refs[0]["path"] == "/Users/tabi/Dropbox/repos/work/val/e4/proto1/include/ExpPrivate.h"
        assert refs[0]["linenum"] == '1270'
    
    def test_extra_paths(self):
        f = TagFile("$HOME/tmp/sample", ["$HOME/repos/work/val/e4/proto1/", "~/pkg/llvm-trunk/tools/clang/"])
        matches = f.match("InitHeaderSearch")
        assert len(matches) == 1
        assert matches[0]["path"] == "/Users/tabi/pkg/llvm-trunk/tools/clang/lib/Frontend/InitHeaderSearch.cpp"
        assert matches[0]["linenum"] == '44'
        

if __name__ == '__main__':
    unittest.main()
