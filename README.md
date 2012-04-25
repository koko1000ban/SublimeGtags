# SublimeGtags

This is a plugin for the [Sublime Text 2](http://www.sublimetext.com/) text
editor that support [GNU GLOBAL(gtags)](http://www.gnu.org/software/global/)


## Installation
clone this repo directly into your Packages directory.

## Settings
 You can point other locations for the GPATH, GRPATH etc files via the preferences.
 Main menu -> Preferences -> Package Settings -> SublimeGtags -> Settings - Users
 
 There's a GTags.sublime-settings:
 
 	{
    	// switch debug mode 
    	"debug"           :  false,

    	// a list of other locations to look up (GTAGSLIBPATH)
    	"extra_tag_paths" : ["/usr/local/src/llvm-trunk/tools/clang"]
	}
 
## Compatibility
 * OSX(good
 * Linux(less good
 * Windows(worst
 
## See
 [CTags Plugin](https://github.com/SublimeText/CTags)

## Screenshot
![](http://dl.dropbox.com/u/32342/github/sublime-gtags1.png)
