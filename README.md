# XPLoaderPy3

The original XPLoader is a .xp file parser for use with libtcod, written by Sean 'RCIX' Hagar. XPLoaderPy3 is a port of XPLoader to TDL/Python3 (with some minor miscellaneous changes) by Erwan 'MalanTai' Castioni and Gawein 'Edern' Le Goff.

# Demo

Just demonstrates loading a simple .xp file with layers. Esc quits, a toggles display of the second layer, arrows move the picture.

# Use

Copy xpLoaderPy3.py into your project, import xpLoaderPy3, and call load\_xp\_string. Note: By default, .xp files are gzipped, and you'll need to use the gzip library to decompress them first. The code's fairly readable if you want to look at it.. load\_layer\_to\_console makes it easier to load the data into libtcod/TDL consoles (root or otherwise). Have fun!

# Requirements

- Python 3.x
- TDL

# Links

[Screenshot](http://i.imgur.com/6Ofm3If.png)

[REXPaint](http://www.gridsagegames.com/rexpaint/), without which this would have no reason to exist

[XPLoader](https://github.com/RCIX/XPLoader), the original program for Python 2, from where almost all of the code comes from.