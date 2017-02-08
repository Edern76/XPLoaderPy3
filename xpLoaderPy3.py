import base64
from tdl import *

##################################
# XpLoaderPy3

# This is a version of Sean 'RCIX' Hagar's XPLoader modificated by Erwan 'MalanTai' Castioni and Gawein 'Edern' Le Goff in order to run on Python 3 with TDL (though it should work with libtcodpy too if you modify the "from tdl import *" statement and the console.draw_char one), along with a few minor changes that we needed for our personal project (the ability to ignore transparent characters and to print from a certain point on the target console, rather than from (0,0))
# XPLoader allows you to process images made with REXPaint and to display them in a libtcod/TDL console. These images must be in the .xp format.
# This version of XPLoader is licensed under the same license as the original : the MIT license. See the LICENSE file for more information.

# Also, thanks a lot to RCIX for making this very useful tool (which saved us a lot of time), and to Kyzrati (GridSageGames) for making REXPaint !"
##################################


##################################
# In-memory XP format is as follows:
# Returned structure is a dictionary with the keys version, layers, width, height, and layer_data
## Version is stored in case it's useful for someone, but as mentioned in the format description it probably won't be unless format changes happen
## Layers is a full 32 bit int, though right now REXPaint only exports or manages up to 4 layers
## Width and height are extracted from the layer with largest width and height - this value will hold true for all layers for now as per the format description
## layer_data is a list of individual layers, which are stored in the following format
### Each layer is a dictionary with keys width, height (see above), and cells. 
### Cells is a row major 2d array of, again, dictionaries with the values 'keycode' (ascii keycode), 'fore_r/g/b', and 'back_r/g/b' (technically ints but in value 0-255)
##################################


##################################
# Used primarily internally to parse the data, feel free to reference them externally if it's useful. 
# Changing these programattically will, of course, screw up the parsing (unless the format changes and you're using an old copy of this file)
##################################

version_bytes = 4
layer_count_bytes = 4

layer_width_bytes = 4
layer_height_bytes = 4
layer_keycode_bytes = 4
layer_fore_rgb_bytes = 3
layer_back_rgb_bytes = 3
layer_cell_bytes = layer_keycode_bytes + layer_fore_rgb_bytes + layer_back_rgb_bytes



##################################
# REXPaint color key for transparent background colors.
##################################

transparent_cell_back_r = 255
transparent_cell_back_g = 0
transparent_cell_back_b = 255

####################################################################
# START LIBTCOD/TDL SPECIFIC CODE

##################################
# Used primarily internally to parse the data, feel free to reference them externally if it's useful. 
# Changing these programattically will, of course, screw up the parsing (unless the format changes and you're using an old copy of this file)
##################################

#the solid square character
poskey_tile_character = 219

#some or all of the below may appear in libtcod's color definitions; and in fact, you can use libtcod colors as you please for position keys. 
#These are merely the colors provided in the accompanying palette.

poskey_color_red = (255, 0, 0)
poskey_color_lightpurple = (254, 0, 255) # specifically 254 as 255, 0, 255 is considered a transparent key color in REXPaint
poskey_color_orange = (255, 128, 0)
poskey_color_pink = (255, 0, 128)
poskey_color_green = (0, 255, 0)
poskey_color_teal = (0, 255, 255)
poskey_color_yellow = (255, 255, 0)
poskey_color_blue = (0, 0, 255)
poskey_color_lightblue = (0, 128, 255)
poskey_color_purple = (128, 0, 255)
poskey_color_white = (255, 255, 255)



def load_layer_to_console(console, xp_file_layer, offsetX = 0, offsetY = 0, drawTransparent = False):
    # Displays a single layer on the console, therefore xp_file_layer mustn't be your .xp file's path, but instead a dictionnary corresponding to a layer's data.
    # In order to extract the layer from a .xp file, just call load_xp_string on your unzipped (use gzip) .xp file. All of this file's layers' data will be in the returned dictionnary, under the 'layer_data' key.
    # If you want to display mutliple layers, just call this function for each layer in 'layer_data'.
    
    if not xp_file_layer['width'] or not xp_file_layer['height']:
        raise AttributeError('Attempted to call load_layer_to_console on data that didn\'t have a width or height key, check your data')

    for x in range(xp_file_layer['width']):
        for y in range(xp_file_layer['height']):
            cell_data = xp_file_layer['cells'][x][y]
            fore_color = (cell_data['fore_r'], cell_data['fore_g'], cell_data['fore_b'])
            back_color = (cell_data['back_r'], cell_data['back_g'], cell_data['back_b'])
            if back_color != (transparent_cell_back_r, transparent_cell_back_g, transparent_cell_back_b) or drawTransparent: #If we don't perform that check we get a fully pink rectangle, that we cannot fix otherwise since TDL doesn't support set_key_color
                console.draw_char(offsetX + x, offsetY + y, cell_data['keycode'], fore_color, back_color) #Replace with 'console_put_char_ex(console, offsetX + x, offsetY + y, cell_data['keycode'], fore_color, back_color)' without quotation marks if using libtcod.

def get_position_key_xy(xp_file_layer, poskey_color):
    for x in range(xp_file_layer['width']):
        for y in range(xp_file_layer['height']):
            cell_data = xp_file_layer['cells'][x][y]
            if cell_data['keycode'] == poskey_tile_character:
                fore_color_matches = cell_data['fore_r'] == poskey_color.r and cell_data['fore_g'] == poskey_color.g and cell_data['fore_b'] == poskey_color.b
                back_color_matches = cell_data['back_r'] == poskey_color.r and cell_data['back_g'] == poskey_color.g and cell_data['back_b'] == poskey_color.b
                if fore_color_matches or back_color_matches:
                    return (x, y)
    raise LookupError('No position key was specified for color ' + str(poskey_color) + ', check your .xp file and/or the input color')


# END LIBTCOD SPECIFIC CODE
####################################################################




##################################
# loads in an xp file from an unzipped string (gained from opening a .xp file with gzip and calling .read())
# reverse_endian controls whether the slices containing data for things like layer width, height, number of layers, etc. is reversed 
# so far as I can tell Python is doing int conversions in big-endian, while the .xp format stores them in little-endian
# I may just not be aware of it being unneeded, but have it there in case
##################################

def load_xp_string(file_string, reverse_endian=True):

    offset = 0

    version = file_string[offset : offset + version_bytes]
    offset += version_bytes
    layer_count = file_string[offset : offset + layer_count_bytes]
    offset += layer_count_bytes

    if reverse_endian:
        version = version[::-1]
        layer_count = layer_count[::-1]

    #hex-encodes the numbers then converts them to an int
    #version = int(version.encode('hex'), 16)
    #layer_count = int(layer_count.encode('hex'), 16)
    
    version = int(base64.b16encode(version), 16)
    layer_count = int(base64.b16encode(layer_count), 16)

    layers = []

    current_largest_width = 0
    current_largest_height = 0

    for layer in range(layer_count):
        #slight lookahead to figure out how much data to feed load_layer

        this_layer_width = file_string[offset:offset + layer_width_bytes]
        this_layer_height = file_string[offset + layer_width_bytes:offset + layer_width_bytes + layer_height_bytes]

        if reverse_endian:
            this_layer_width = this_layer_width[::-1]
            this_layer_height = this_layer_height[::-1]

        #this_layer_width = int(this_layer_width.encode('hex'), 16)
        #this_layer_height = int(this_layer_height.encode('hex'), 16)
        
        this_layer_width = int(base64.b16encode(this_layer_width), 16)
        this_layer_height = int(base64.b16encode(this_layer_height), 16)

        current_largest_width = max(current_largest_width, this_layer_width)
        current_largest_height = max(current_largest_height, this_layer_height)

        layer_data_size = layer_width_bytes + layer_height_bytes + (layer_cell_bytes *  this_layer_width * this_layer_height)

        layer_data_raw = file_string[offset:offset + layer_data_size]
        layer_data = parse_layer(file_string[offset:offset + layer_data_size], reverse_endian)
        layers.append(layer_data)

        offset += layer_data_size

    return {
        'version':version,
        'layer_count':layer_count,
        'width':current_largest_width,
        'height':current_largest_height,
        'layer_data':layers
    }

##################################
# Takes a single layer's data and returns the format listed at the top of the file for a single layer.
##################################

def parse_layer(layer_string, reverse_endian=True):
    offset = 0

    width = layer_string[offset:offset + layer_width_bytes]
    offset += layer_width_bytes
    height = layer_string[offset:offset + layer_height_bytes]
    offset += layer_height_bytes

    if reverse_endian:
        width = width[::-1]
        height = height[::-1]
    
    width = int(base64.b16encode(width), 16)
    height = int(base64.b16encode(height), 16)

    cells = []
    for x in range(width):
        row = []

        for y in range(height):
            cell_data_raw = layer_string[offset:offset + layer_cell_bytes]
            cell_data = parse_individual_cell(cell_data_raw, reverse_endian)
            row.append(cell_data)
            offset += layer_cell_bytes

        cells.append(row)

    return {
        'width':width,
        'height':height,
        'cells':cells
    }

##################################
# Pulls out the keycode and the foreground/background RGB values from a single cell's data, returning them in the format listed at the top of this file for a single cell.
##################################

def parse_individual_cell(cell_string, reverse_endian=True):
    offset = 0

    keycode = cell_string[offset:offset + layer_keycode_bytes]
    if reverse_endian:
        keycode = keycode[::-1]
    keycode = int(base64.b16encode(keycode), 16)
    offset += layer_keycode_bytes

    fore_r = int(base64.b16encode(cell_string[offset:offset+1]), 16)
    offset += 1
    fore_g = int(base64.b16encode(cell_string[offset:offset+1]), 16)
    offset += 1
    fore_b = int(base64.b16encode(cell_string[offset:offset+1]), 16)
    offset += 1

    back_r = int(base64.b16encode(cell_string[offset:offset+1]), 16)
    offset += 1
    back_g = int(base64.b16encode(cell_string[offset:offset+1]), 16)
    offset += 1
    back_b = int(base64.b16encode(cell_string[offset:offset+1]), 16)
    offset += 1

    return {
        'keycode':keycode,
        'fore_r':fore_r,
        'fore_g':fore_g,
        'fore_b':fore_b,
        'back_r':back_r,
        'back_g':back_g,
        'back_b':back_b,
    }