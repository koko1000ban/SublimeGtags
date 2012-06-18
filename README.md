# SublimeGtags

This is a plugin for the [Sublime Text 2](http://www.sublimetext.com/) text
editor that support [GNU GLOBAL (gtags)](http://www.gnu.org/software/global/)


## Installation
Clone this repo directly into your Packages directory.

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

## See
 [CTags Plugin](https://github.com/SublimeText/CTags)

## Support
If you find something wrong with the plugin, the documentation, or wish to request a feature, let me know on the project’s issue page.

Thanks :)

## Screenshot
![](http://dl.dropbox.com/u/32342/github/sublime-gtags1.png)
