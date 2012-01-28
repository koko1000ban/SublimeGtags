# -*- coding: utf-8 -*-

import os
from os.path import join, normpath, dirname

import sublime
import sublime_plugin
from sublime import status_message

# Gtags
import gtags
from gtags import (TagFile, PP, find_tags_root)

setting = sublime.load_settings('GTags.sublime-settings').get # (key, None)
ON_LOAD       = sublime_plugin.all_callbacks['on_load']

class one_shot(object):
    def __init__(self):
        self.callbacks.append(self)
        self.remove = lambda: self.callbacks.remove(self)

def select(view, region):
    sel_set = view.sel()
    sel_set.clear()
    sel_set.add(region)
    view.show(region)

def on_load(f=None, window=None, encoded_row_col=True):
    window = window or sublime.active_window()
    def wrapper(cb):
        if not f: return cb(window.active_view())
        view = window.open_file( normpath(f), encoded_row_col )
        def wrapped():
            cb(view)

        if view.is_loading():
            class set_on_load(one_shot):
                callbacks = ON_LOAD
                def on_load(self, view):
                    try:wrapped()
                    finally: self.remove()

            set_on_load()
        else: wrapped()
    return wrapper


def run_on_cwd(dir=None):
    window = sublime.active_window()
    def wrapper(func):
        view = window.active_view()
        fname = view.file_name()
        
        if dir is None:
            tags_root = find_tags_root(dirname(fname))
            if tags_root is None:
                sublime.error_message("GTAGS not found. build tags by 'gtags'")
                return
        else:
            tags_root = dir[0]
        
        tags = TagFile(tags_root)
        func(view, tags, tags_root)

    return wrapper

class GtagsJumpBack(sublime_plugin.WindowCommand):
    def run(self, to=None):
        if not GtagsJumpBack.last: return status_message('JumpBack buffer empty')
        f, sel = GtagsJumpBack.last.pop()
        self.jump(f, eval(sel))
    
    def jump(self, fn, sel):
        @on_load(fn)
        def and_then(view):
            select(view, sublime.Region(*sel))
    
    last    =     []
    @classmethod
    def append(cls, view):
        fn = view.file_name()
        if fn:
            cls.last.append((fn, `view.sel()[0]`))

def gtags_jump_keyword(view, tags, keyword_or_items, jump_directly_if_one=False):
    if isinstance(keyword_or_items, list):
        items = keyword_or_items
        pass
    elif isinstance(keyword_or_items, str):
        items = tags.match(keyword_or_items)
    else:
        error_message("keyword_or_items's type(%s) is unsupported." % type(keyword_or_items))
        return
    
    def on_select(i):
        if i != -1:
            GtagsJumpBack.append(view)
            view.window().open_file("%s:%d:%d" % (normpath(items[i]['path']), int(items[i]['linenum']), 0), sublime.ENCODED_POSITION)
    
    if jump_directly_if_one or len(items) == 1:
        on_select(0)
    else:
        view.window().show_quick_panel(["%s\t%s" % (item['path'], item['fields']) for item in items], on_select)


class GtagsShowSymbols(sublime_plugin.TextCommand):
    def run(self, edit):
        @run_on_cwd()
        def and_then(view, tags, root):
            items = tags.start_with('')
            if not items:
                status_message("no items?")
                return

            def on_select(i):
                gtags_jump_keyword(view, tags, items[i])
            
            view.window().show_quick_panel(items, on_select)

class GtagsNavigateToDefinition(sublime_plugin.TextCommand):
    def run(self, edit):
        @run_on_cwd()
        def and_then(view, tags, root):
            symbol = view.substr(view.word(view.sel()[0]))
            matches = tags.match(symbol)
            if not matches:
                status_message("'%s' is not found on tag." % symbol)
                return

            gtags_jump_keyword(view, tags, matches)
        
class GtagsRebuildTags(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        @run_on_cwd(args.get('dirs'))
        def and_then(view, tags, root):
            sublime.status_message("rebuild tags on dir: %s" % root)
            tags.rebuild()
            sublime.status_message("build success on dir: %s" % root)
            