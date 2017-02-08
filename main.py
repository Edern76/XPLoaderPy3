import tdl
import xpLoaderPy3 as xpL
import gzip
import os

offX, offY = 0, 0
loadLayer2 = False
MOVEMENT_KEYS = {
                 #Standard arrows
                 'UP': [0, -1],
                 'DOWN': [0, 1],
                 'LEFT': [-1, 0],
                 'RIGHT': [1, 0],
                 }
###################
# Find the path to the file to display
curDir = os.path.dirname(__file__)
file = os.path.join(curDir, "xptest.xp")
###################

###################
# Initialize the main console
WIDTH, HEIGHT = 30, 30
root = tdl.init(WIDTH, HEIGHT, 'XpLoaderPy3 Example')
###################

###################
# Create a subconsole which will hold the image. It is definitely not mandatory to do so, but I did this just in order to show that it can be done.
SUB_WIDTH, SUB_HEIGHT = 20, 20
frame = tdl.Console(SUB_WIDTH, SUB_HEIGHT)
###################

###################
# Get data from the .xp file
unzippedFile = gzip.open(file).read() #Unzips the .xp file so we can call load_xp_string
fileAttributes = xpL.load_xp_string(unzippedFile)
fileWidth = fileAttributes["width"]
fileHeight = fileAttributes["height"]
layers = fileAttributes["layer_data"]
###################

###################
# Main loop with display and input handling
while not tdl.event.is_window_closed():
	frame.clear()
	root.clear()
	root.draw_str(0, 0, "Width : {} / Height : {}".format(fileWidth, fileHeight), fg = (255, 0, 0), bg = Ellipsis)
	if loadLayer2:
		for layer in layers:
			xpL.load_layer_to_console(frame, layer, offX, offY)
	else:
		xpL.load_layer_to_console(frame, layers[0], offX, offY)
	root.blit(frame, 10, 10, SUB_WIDTH, SUB_HEIGHT, srcX=0, srcY=0)
	tdl.flush()
	key = tdl.event.key_wait()
	if key.keychar.upper() in MOVEMENT_KEYS:
		(x, y) = MOVEMENT_KEYS[key.keychar.upper()]
		if offX + x in range(0, 10) and offY + y in range(0, 10):
			offX += x
			offY += y
	elif key.keychar.upper() == "ESCAPE":
		raise SystemExit("User pressed Escape")
	elif key.keychar.upper() == "A":
		loadLayer2 = not loadLayer2
####################
	
	
	 



