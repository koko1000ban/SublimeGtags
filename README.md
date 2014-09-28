# SublimeGtags

This is a plugin for the [Sublime Text 2](http://www.sublimetext.com/)/[3](http://www.sublimetext.com/3) text
editor that support [GNU GLOBAL (gtags)](http://www.gnu.org/software/global/)


## Installation
Clone this repo directly into your Packages directory.

##Set Up
To set-up C/C++ Source Navigation:
1. Install [CTAGS](http://ctags.sourceforge.net)
2. Get [GNU GLOBAL](http://www.gnu.org/software/global/)
3. In terminal cd to downloaded directory, and run command "./configure --with-exuberant-ctags" (This will use the Ctags as a parser for parsing files)
4. Type "make".
5. Type "make install".
6. Now run "gtags -v" in your project folder to create tag files.

## Settings
 You can point other locations for the GPATH, GRPATH etc files via the preferences.
 Main menu -> Preferences -> Package Settings -> SublimeGtags -> Settings - Users

 There's a GTags.sublime-settings:

    {
        // show relative paths in keyword jump selection panel
        "show_relative_paths": true,

        // a list of other locations to look up (GTAGSLIBPATH)
        "extra_tag_paths" : ["/usr/local/src/llvm-trunk/tools/clang"]
    }

## Compatibility
 * OS X (good)
 * Linux (fair)
 * Windows (fair)

## Support
If you find something wrong with the plugin, the documentation, or wish to request a feature, let me know on the project’s issue page.

Thanks :)

## Screenshot
![](http://dl.dropbox.com/u/32342/github/sublime-gtags1.png)
