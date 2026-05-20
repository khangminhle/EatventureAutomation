import os
from enum import Enum, auto
import glob
import cv2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GameMode(Enum):
    """Game mode enumeration"""
    NORMAL = auto()
    POTION = auto()

class ImageColor(Enum):
    GRAYSCALE = auto()
    BGR = auto()

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

    # Screen resolution defaults
    DEFAULT_TEMPLATE_WIDTH = 1080
    DEFAULT_TEMPLATE_HEIGHT = 2340

    LOADED_TEMPLATES = {}
    
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
    
    CLICK_RETRY_COUNT = 10  # Times to click shop elements

    @classmethod
    def load_templates(cls):
        print("--Loading templates")
        for name, path in cls.TEMPLATES.items():
            template_path = os.path.join(BASE_DIR, path)
            
            if not os.path.exists(template_path):
                print(f'Khong tim thay path:', template_path)
                continue

            if os.path.isdir(template_path):

                search_pattern = os.path.join(template_path, "*.png")

                file_list = glob.glob(search_pattern)

                for file_path in file_list:
                    img = cv2.imread(file_path)

                    file_name = os.path.basename(file_path)

                    if img is not None:
                        cls.LOADED_TEMPLATES[file_name] = img
                        print("filename", file_name)
                        print("Da load template:", file_path)
            else:
                img = cv2.imread(template_path)

                if img is not None:
                    cls.LOADED_TEMPLATES[name] = img
                    print("Da load template:", template_path)




class ValidZones:
    """Valid zones for clicking game elements"""
    
    # Center zone
    CENTER = {"x_min": 209, "x_max": 870, "y_min": 675, "y_max": 1875}
    
    # Left zone
    LEFT = {"y_min": 960, "y_max": 1860}
    
    # Right zone
    RIGHT = {"y_min": 1240, "y_max": 2040}

