import os
from enum import Enum

# Screen resolution defaults
DEFAULT_TEMPLATE_WIDTH = 1080
DEFAULT_TEMPLATE_HEIGHT = 2340
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GameMode(Enum):
    """Game mode enumeration"""
    NORMAL = "NORMAL"
    POTION = "POTION"


class UICoordinates:
    """UI element coordinates (based on 1080x2340 resolution, auto-scaled by ADB)"""
    
    # Buttons
    FINISH_BTN = {"x": 113, "y": 2200}
    RENOVATE_BTN = {"x": 550, "y": 1650}
    OPEN_BTN = {"x": 540, "y": 1400}
    UPGRADE_SHOP_BTN = {"x": 977, "y": 2200}
    ADS_BTN = {"x": 545, "y": 2200}
    OUTSIDE = {"x": 550, "y": 400}
    
    # Shop elements
    FIRST_ELEMENT = {"x": 850, "y": 950}
    CLOSE_SHOP = {"x": 920, "y": 800}


class SwipeConfig:
    """Swipe and detection configurations"""
    
    MAX_SWIPE_TURNS = 2
    SWIPE_DISTANCE_RATIO = 1/5
    CLICK_DELAY = 0.1
    SWIPE_DURATION = 0.5
    LOOP_DELAY = 0.5
    
    # Crop regions for swipe detection
    SWIPE_TOP_REGION = {"left": 10, "top": 270, "right": 90, "bottom": 300}
    SWIPE_BOTTOM_REGION = {"left": 10, "top": 2080, "right": 90, "bottom": 2110}


class TemplateConfig:
    """Template matching configurations"""
    
    TEMPLATES = {
        "upgrade_food": "templates/button_test.png",
        "button_coin": "templates/button_coin.png",
        "coin_potion_ingredients": "templates/coin_potion_ingredients.png",
        "upgrade_shop": "templates/upgrade_button.png",
        "coin_shop": "templates/coinshop.png",
        "coin_potion_shop": "templates/coin_potion_shop.png",
        "open_button": "templates/open_button.png",
        "finish_button": "templates/finished_button.png",
        "boxes_dir": "templates/boxes",
    }
    
    THRESHOLDS = {
        "default": 0.8,
        "coin_shop": 0.9,
    }
    
    CLICK_RETRY_COUNT = 10  # Times to click shop elements


class ValidZones:
    """Valid zones for clicking game elements"""
    
    # Center zone
    CENTER = {"x_min": 209, "x_max": 870, "y_min": 675, "y_max": 1875}
    
    # Left zone
    LEFT = {"x_min": 0, "x_max": 209, "y_min": 960, "y_max": 1860}
    
    # Right zone
    RIGHT = {"x_min": 870, "x_max": 999999, "y_min": 1240, "y_max": 2040}


# Legacy constants for backward compatibility
DEFAULT_FINISH_BTN_X = UICoordinates.FINISH_BTN["x"]
DEFAULT_FINISH_BTN_Y = UICoordinates.FINISH_BTN["y"]
DEFAULT_RENOVATE_X = UICoordinates.RENOVATE_BTN["x"]
DEFAULT_RENOVATE_Y = UICoordinates.RENOVATE_BTN["y"]
DEFAULT_OPEN_BTN_X = UICoordinates.OPEN_BTN["x"]
DEFAULT_OPEN_BTN_Y = UICoordinates.OPEN_BTN["y"]
DEFAULT_UPGRADE_SHOP_X = UICoordinates.UPGRADE_SHOP_BTN["x"]
DEFAULT_UPGRADE_SHOP_Y = UICoordinates.UPGRADE_SHOP_BTN["y"]
DEFAULT_ADS_X = UICoordinates.ADS_BTN["x"]
DEFAULT_ADS_Y = UICoordinates.ADS_BTN["y"]
DEFAULT_OUTSIDE_X = UICoordinates.OUTSIDE["x"]
DEFAULT_OUTSIDE_Y = UICoordinates.OUTSIDE["y"]
DEFAULT_FIRST_ELEMENT_X = UICoordinates.FIRST_ELEMENT["x"]
DEFAULT_FIRST_ELEMENT_Y = UICoordinates.FIRST_ELEMENT["y"]
DEFAULT_CLOSING_UPGRADE_X = UICoordinates.CLOSE_SHOP["x"]
DEFAULT_CLOSING_UPGRADE_Y = UICoordinates.CLOSE_SHOP["y"]
