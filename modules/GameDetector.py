import os
import cv2
import glob
import numpy as np
#import adbutils

from .ImageProcess import *
from .Constants import *



class GameDetector:

    def __init__(self, adb: ADBController, map_game="NORMAL"):
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


    def _match_template_helper(self, template_paths, mode="GRAY", **kwargs):

        if not self.__adb:
            print("Not connected to ADB yet")
            return None

        try:
            # SCREENSHOT
            img = self.__adb.screenshot(mode=mode)

            # TEMPLATE
            template_path = os.path.join(BASE_DIR, *template_paths)

            if mode == "GRAY":
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            else:
                if mode == "BGR":
                    template = cv2.imread(template_path)

            return find_points_match_template(img, template, **kwargs)

        except Exception as e:
            print("Error GameDetector - _match_template_helper:", e)
            return None

    def find_upgrade_food(self):

        points = self._match_template_helper(['templates', 'button_test.png'])

        if points is None:
            return []

        if isinstance(points, bool):
            return []

        return [(x, y+20) for x, y in points if self._check_valid_points(x, y+20)]

    def find_button_coin(self):

        if self.__map == "POTION":
            points = self._match_template_helper(['templates', 'coin_potion_ingredients.png'])
        else:
            if self.__map == "NORMAL":
                points = self._match_template_helper(['templates', 'button_coin.png'])

        if points is None:
            return []

        if isinstance(points, bool):
            return []

        return points

    def find_boxes(self):

        template_path = os.path.join(BASE_DIR, 'templates', 'boxes' , '*.png')
        templates = glob.glob(template_path)

        for tp in templates:
            print(tp)
            points = self._match_template_helper([tp])

            print("boxes:", points)

            if points is None:
                return []

            if isinstance(points, bool):
                return []
            
            if len(points) > 0:
                return points#return [(x, y) for x, y in points if self._check_valid_points(x, y)]

        return []

    def find_upgrade_shop(self):

        flag = self._match_template_helper(['templates', 'upgrade_button.png'], mode="BGR", check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False

    def find_upgrade_shop_elements(self):

        if self.__map == "POTION":
            template_path = ['templates', 'coin_potion_shop.png']
        else:
            if self.__map == "NORMAL":
                template_path = ['templates', 'coinshop.png']

        flag = self._match_template_helper(template_path, mode="BGR", threshold=0.9, check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False


    def find_open_button(self):
        
        flag = self._match_template_helper(['templates', 'open_button.png'], check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False
        

    def find_finish_button(self):

        flag = self._match_template_helper(['templates', 'finished_button.png'], mode="BGR", check=True)

        if flag is None:
            return False

        if isinstance(flag, bool):
            return flag

        return False

    def check_max_swipe(self, mode="top"):
        # Top region
        left = 10 * self.__adb.scale_x
        top = 270 * self.__adb.scale_y
        right = 90 * self.__adb.scale_x
        bottom = 300 * self.__adb.scale_y

        if mode == "top":
            img1_path = os.path.join(BASE_DIR, 'check_swipe.png')
            img1 = cv2.imread(img1_path)
        else:
            # Bottom region
            top = 2080 * self.__adb.scale_y
            bottom = 2110 * self.__adb.scale_y
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
