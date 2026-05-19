import os

DEFAULT_TEMPLATE_WIDTH = 1080
DEFAULT_TEMPLATE_HEIGHT = 2340
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


'''
	BELOW POSITIONS:
	1. BASED ON 1080 X 2340 RESOLUTION
	2. BUT THEY ARE SCALED IN ADB CONTROLLER
	SO, WE DON'T NEED TO UPDATE WHEN USING
	OTHER DEVICES WITH DIFFERENT RESOLUTIONS
'''

# Default position of finish button
DEFAULT_FINISH_BTN_X = 113
DEFAULT_FINISH_BTN_Y = 2200

# Default position of renovate button
DEFAULT_RENOVATE_X = 550
DEFAULT_RENOVATE_Y = 1650

# Default position of finish button
DEFAULT_OPEN_BTN_X = 540
DEFAULT_OPEN_BTN_Y = 1400

# Default position of upgrade shop
DEFAULT_UPGRADE_SHOP_X = 977
DEFAULT_UPGRADE_SHOP_Y = 2200

# Default positon of Ads
DEFAULT_ADS_X = 545
DEFAULT_ADS_Y = 2200

# Default outside position to close upgrade shop
DEFAULT_OUTSIDE_X = 550
DEFAULT_OUTSIDE_Y = 400

# Default position of first element in upgrade shop

DEFAULT_FIRST_ELEMENT_X = 850
DEFAULT_FIRST_ELEMENT_Y = 950

# Default position for closing upgrade shop

DEFAULT_CLOSING_UPGRADE_X = 920
DEFAULT_CLOSING_UPGRADE_Y = 800

'''
	VALID ZONE FOR CLICK BOXES, UPGRADE, OPEN, FINSH

	ZONE 1:

	209 <= X <= 870
	675 <= Y <= 1875

	ZONE 2 - LEFT ZONE:

	X < 209
	960 <= Y <= 1860
	
	ZONE 3 - RIGHT ZONE:
	X > 870
	1240 <= Y <= 2040
'''

