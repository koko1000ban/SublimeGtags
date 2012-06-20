#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import pprint
import re
import shlex
import subprocess
import unittest

PP = pprint.PrettyPrinter(indent=4)

TAGS_RE = re.compile(
    '(?P<symbol>[^\s]+)\s+'
    '(?P<linenum>[^\s]+)\s+'
    '(?P<path>[^\s]+)\s+'
    '(?P<signature>.*)'
)

ENV_PATH = os.environ['PATH']
IS_WINDOWS = platform.system() == 'Windows'


def find_tags_root(current, previous=None):
    current = os.path.normpath(current)
    if not os.path.isdir(current):
        return None

    parent = os.path.dirname(current)
    if parent == previous:
        return None

    if 'GTAGS' in os.listdir(current):
        return current

    return find_tags_root(parent, current)


class TagSubprocess(object):
    def __init__(self, **kwargs):
        self.default_kwargs = kwargs
        if IS_WINDOWS:
            self.default_kwargs['shell'] = True

    def create(self, command, **kwargs):
        final_kwargs = self.default_kwargs
        final_kwargs.update(kwargs)

        if isinstance(command, basestring):
            command = shlex.split(command.encode('utf-8'))

        return subprocess.Popen(command, **final_kwargs)

    def stdout(self, command, **kwargs):
        process = self.create(command, stdout=subprocess.PIPE, **kwargs)
        return process.communicate()[0]

    def call(self, command, **kwargs):
        process = self.create(command, stderr=subprocess.PIPE, **kwargs)
        _, stderr = process.communicate()
        return process.returncode, stderr


class TagFile(object):
    def _expand_path(self, path):
        path = os.path.expandvars(os.path.expanduser(path))
        if IS_WINDOWS:
            path = path.encode('utf-8')
        return path

    def __init__(self, root_dir=None, extra_paths=[]):
        self.__env = {'PATH': ENV_PATH}
        self.__root = root_dir

        if root_dir is not None:
            self.__env['GTAGSROOT'] = self._expand_path(root_dir)

        if extra_paths:
            self.__env['GTAGSLIBPATH'] = os.pathsep.join(
                map(self._expand_path, extra_paths))

        self.subprocess = TagSubprocess(env=self.__env)

    def start_with(self, prefix):
        return self.subprocess.stdout('global -c %s' % prefix).splitlines()

    def _match(self, pattern, options):
        lines = self.subprocess.stdout(
            'global %s %s' % (options, pattern)).splitlines()
        matches = []
        for search_obj in (t for t in (TAGS_RE.search(l) for l in lines) if t):
            matches.append(search_obj.groupdict())
        return matches

    def match(self, pattern, reference=False):
        return self._match(pattern, '-ax' + ('r' if reference else ''))

    def rebuild(self):
        retcode, stderr = self.subprocess.call('gtags -v', cwd=self.__root)
        success = retcode == 0
        if not success:
            print stderr
        return success


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
        refs = f.match("Exp_IsSkipProgress", reference=True)
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
