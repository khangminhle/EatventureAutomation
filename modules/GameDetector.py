import os
from string import templatelib
import cv2
import glob
import numpy as np
#import adbutils

from .ImageProcess import *
from .ADB import ADBController

from .Constants import *
from .Constants import GameMode
from .Constants import ImageColor
from .Constants import SwipeConfig
from .Constants import TemplateConfig

class GameDetector:

    def __init__(self, adb: ADBController, map_game=GameMode.NORMAL):
        self.__adb = adb
        self.__map = map_game

    def check_nothing_upgrade(self):

        actions = [self.find_upgrade_food]#, self.find_upgrade_shop, self.find_boxes]

        for action in actions:
            if action():
                return True
        
        return False

    def _check_valid_points(self, x: int, y: int):

        #print("max min", self.__adb.max_screen_x, self.__adb.max_screen_y)

        if x < 0 or y < 0:
            return False

        if x > self.__adb.max_screen_x or y > self.__adb.max_screen_y:
            return False

        # LEFT VALID ZONE
        if x  < 209:
            return y >= 960 and y <= 1860

        # MID VALID ZONE
        if x >= 209 and x <= 870:
            return y >= 675 and y <= 1875

        # RIGHT VALID ZONE:
        if x > 870:
            return y >= 1240 and y <= 2040


    def _match_template_helper(self, template_name, mode=ImageColor.GRAYSCALE, **kwargs):

        if not self.__adb:
            print("Not connected to ADB yet")
            return None

        try:
            # SCREENSHOT
            img = self.__adb.screenshot(mode=mode)

            # TEMPLATE
            template = TemplateConfig.LOADED_TEMPLATES[template_name]

            if mode == ImageColor.GRAYSCALE:
                template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            else:
                if mode != ImageColor.BGR:
                    print("Input mode image khong hop le")
                    return None

            return find_points_match_template(img, template, **kwargs)

        except Exception as e:
            print("Error GameDetector - _match_template_helper:", e)
            return None

    def find_upgrade_food(self):
        points = self._match_template_helper('upgrade_food')#['templates', 'button_test.png'])

        if points is None:
            return []

        if isinstance(points, bool):
            return []

        return [(x, y+20) for x, y in points if self._check_valid_points(x, y+20)]

    def find_button_coin(self):

        if self.__map == GameMode.POTION:
            points = self._match_template_helper('coin_potion_ingredients')#['templates', 'coin_potion_ingredients.png'])
        else:
            if self.__map == GameMode.NORMAL:
                points = self._match_template_helper('button_coin')#['templates', 'button_coin.png'])
            else:
                return []

        if points is None:
            return []

        if isinstance(points, bool):
            return []

        return points

    def find_boxes(self):

        #templates = TemplateConfig.LOADED_TEMPLATES['boxes_dir']

        template_path = os.path.join(BASE_DIR, 'templates', 'boxes' , '*.png')
        template_names = [ os.path.basename(path) for path in glob.glob(template_path)]

        for template_name in template_names:
        
            points = self._match_template_helper(template_name)

            print("boxes:", points)

            if points is None:
                return []

            if isinstance(points, bool):
                return []
            
            if len(points) > 0:
                return [(x, y+20) for x, y in points if self._check_valid_points(x, y+20)]

        return []

    def find_upgrade_shop(self):

        flag = self._match_template_helper('upgrade_shop', mode=ImageColor.BGR, check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False

    def find_upgrade_shop_elements(self):

        if self.__map == GameMode.POTION:
            template_name = 'coin_potion_shop'
        else:
            if self.__map == GameMode.NORMAL:
                template_name = 'coinshop'
            else:
                return False

        flag = self._match_template_helper(template_name, mode=ImageColor.BGR, threshold=0.9, check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False


    def find_open_button(self):
        
        flag = self._match_template_helper('open_button', check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False
        

    def find_finish_button(self):

        flag = self._match_template_helper('finish_button', mode=ImageColor.BGR, check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False

    def check_max_swipe(self, mode="top"):
        # Top region
        left = SwipeConfig.SWIPE_TOP_REGION['left'] * self.__adb.scale_x
        top = SwipeConfig.SWIPE_TOP_REGION['top'] * self.__adb.scale_y
        right = SwipeConfig.SWIPE_TOP_REGION['right'] * self.__adb.scale_x
        bottom = SwipeConfig.SWIPE_TOP_REGION['bottom'] * self.__adb.scale_y

        if mode == "top":
            img1_path = os.path.join(BASE_DIR, 'check_swipe.png')
            img1 = cv2.imread(img1_path)
        else:
            # Bottom region
            top = SwipeConfig.SWIPE_BOTTOM_REGION['top'] * self.__adb.scale_y
            bottom = SwipeConfig.SWIPE_BOTTOM_REGION['bottom'] * self.__adb.scale_y
            img1_path = os.path.join(BASE_DIR, 'check_swipe_bottom.png')
            img1 = cv2.imread(img1_path)


        if img1 is None:
            print("Khong tim thay check swipe png")
            return None

        cropped_img = self.__adb.crop_screen((left, top, right, bottom))

        if cropped_img is not None:
            img2 = cv2.cvtColor(cropped_img, cv2.COLOR_RGBA2BGR)

            if check_same_images(img1, img2):
                return True
            else:
                return False
        else:
            print("Loi check max swipe")
            return None
