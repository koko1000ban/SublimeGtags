# -*- coding: utf-8 -*-

import os
import threading
from os.path import join, normpath, dirname

import sublime
import sublime_plugin
from sublime import status_message

# Gtags
import gtags
from gtags import (TagFile, PP, find_tags_root)

settings = sublime.load_settings('GTags.sublime-settings')


def run_on_cwd(dir=None):
    window = sublime.active_window()

    def wrapper(func):
        view = window.active_view()

        filename = view.file_name()
        if filename is None:
            sublime.error_message('Cannot use GNU GLOBAL for non-file')
            return

        if dir is None:
            tags_root = find_tags_root(dirname(filename))
            if tags_root is None:
                sublime.error_message("GTAGS not found. build tags by 'gtags'")
                return
        else:
            tags_root = dir[0]

        tags = TagFile(tags_root, settings.get('extra_tag_paths'))
        func(view, tags, tags_root)

    return wrapper


class ThreadProgress(object):
    def __init__(self, thread, message, success_message, error_message):
        self.thread = thread
        self.message = message
        self.success_message = success_message
        self.error_message = error_message
        self.addend = 1
        self.size = 8
        sublime.set_timeout(lambda: self.run(0), 100)

    def run(self, i):
        if not self.thread.is_alive():
            if hasattr(self.thread, 'success') and not self.thread.success:
                sublime.status_message(self.error_message)
            else:
                sublime.status_message(self.success_message)
            return

        before = i % self.size
        after = (self.size - 1) - before
        sublime.status_message('%s [%s=%s]' % \
            (self.message, ' ' * before, ' ' * after))
        if not before:
            self.addend = 1
        elif not after:
            self.addend = -1
        i += self.addend
        sublime.set_timeout(lambda: self.run(i), 100)


class JumpHistory(object):
    instance = None

    def __init__(self):
        self._storage = []

    def append(self, view):
        filename = view.file_name()
        row, col = view.rowcol(view.sel()[0].begin())
        self._storage.append('%s:%d:%d' % (filename, row + 1, col + 1))

    def jump_back(self):
        if self.empty():
            sublime.status_message('Jump history is empty')
        else:
            filename = self._storage.pop()
            sublime.active_window().open_file(filename, sublime.ENCODED_POSITION)

    def jump_forward(self):
        sublime.status_message('Not implemented')

    def empty(self):
        return len(self._storage) == 0


def jump_history():
    if JumpHistory.instance is None:
        JumpHistory.instance = JumpHistory()
    return JumpHistory.instance


class GtagsJumpBack(sublime_plugin.WindowCommand):
    def run(self):
        jump_history().jump_back()


def gtags_jump_keyword(view, keywords, root, showpanel=False):
    def jump(keyword):
        jump_history().append(view)
        position = '%s:%d:0' % (
            os.path.normpath(keyword['path']), int(keyword['linenum']))
        view.window().open_file(position, sublime.ENCODED_POSITION)

    def on_select(index):
        if index != -1:
            jump(keywords[index])

    if showpanel or len(keywords) > 1:
        if settings.get('show_relative_paths'):
            convert_path = lambda path: os.path.relpath(path, root)
        else:
            convert_path = os.path.normpath
        data = [
            [kw['signature'], '%s:%d' % (convert_path(kw['path']), int(kw['linenum']))]
             for kw in keywords
        ]
        view.window().show_quick_panel(data, on_select)
    else:
        jump(keywords[0])


class ShowSymbolsThread(threading.Thread):
    def __init__(self, view, tags, root):
        threading.Thread.__init__(self)
        self.view = view
        self.tags = tags
        self.root = root

    def run(self):
        symbols = self.tags.start_with('')
        self.success = len(symbols) > 0
        if not self.success:
            return

        def on_select(index):
            if index != -1:
                definitions = self.tags.match(symbols[index])
                gtags_jump_keyword(self.view, definitions, self.root)

        sublime.set_timeout(
            lambda: self.view.window().show_quick_panel(symbols, on_select), 0)


class GtagsShowSymbols(sublime_plugin.TextCommand):
    def run(self, edit):
        @run_on_cwd()
        def and_then(view, tags, root):
            thread = ShowSymbolsThread(view, tags, root)
            thread.start()
            ThreadProgress(thread,
                'Getting symbols on %s' % root,
                'Symbols have successfully obtained',
                'No symbols found')


class GtagsNavigateToDefinition(sublime_plugin.TextCommand):
    def run(self, edit):
        @run_on_cwd()
        def and_then(view, tags, root):
            symbol = view.substr(view.word(view.sel()[0]))
            matches = tags.match(symbol)
            if not matches:
                status_message("'%s' is not found on tag." % symbol)
                return

            gtags_jump_keyword(view, matches, root)

class GtagsFindReferences(sublime_plugin.TextCommand):
    def run(self, edit):
        @run_on_cwd()
        def and_then(view, tags, root):
            symbol = view.substr(view.word(view.sel()[0]))
            matches = tags.match(symbol, reference=True)
            if not matches:
                status_message("'%s' is not found on rtag." % symbol)
                return

            gtags_jump_keyword(view, matches, root)


class TagsRebuildThread(threading.Thread):
    def __init__(self, tags):
        threading.Thread.__init__(self)
        self.tags = tags

    def run(self):
        self.success = self.tags.rebuild()


class GtagsRebuildTags(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        # set root folder if run from sidebar context menu
        root = kwargs.get('dirs')

        @run_on_cwd(dir=root)
        def and_then(view, tags, root):
            thread = TagsRebuildThread(tags)
            thread.start()
            ThreadProgress(thread,
                'Rebuilding tags on %s' % root,
                'Tags rebuilt successfully on %s' % root,
                'Error while tags rebuilding, see console for details')
