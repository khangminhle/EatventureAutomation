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

    def __check_valid_points(self, x: int, y: int):

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


    def find_upgrade_food(self):
        if not self.__adb:
            print("Not connected to ADB yet")
            return

        img = self.__adb.screenshot(mode="GRAY")
        template_path = os.path.join(BASE_DIR, 'templates', 'button_test.png')
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)
        points = find_points_match_template(img, template)
        #print('Ti le:', self.__adb.scale_x, self.__adb.scale_y)

        return [(x, y+20) for x, y in points if self.__check_valid_points(x, y+20)]

        # Loại bỏ các điểm vượt giới hạn Y
        #return [(x, y + 20) for x, y in points if y + 20 < self.__adb.upper_bound_y]


    def find_button_coin(self):
        if not self.__adb:
            print("Not connected to ADB yet")
            return

        img = self.__adb.screenshot(mode="GRAY")
        template_path = os.path.join(BASE_DIR, 'templates', 'button_coin.png')
        if self.__map == "POTION":
            template_path = os.path.join(BASE_DIR, 'templates', 'coin_potion_ingredients.png')
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)
        return find_points_match_template(img, template)

    def find_boxes(self):
        if not self.__adb:
            print("Not connected to ADB yet")
            return
        img = self.__adb.screenshot(mode="GRAY")
        template_path = os.path.join(BASE_DIR, 'templates', 'boxes' , '*.png')
        templates = glob.glob(template_path)

        for tp in templates:
            template = cv2.imread(tp, cv2.IMREAD_GRAYSCALE)
            template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)
            points = find_points_match_template(img, template)

            if len(points) > 0:
                return [(x, y) for x, y in points if self.__check_valid_points(x, y)]

    def find_upgrade_shop(self):

        if not self.__adb:
            print("Not connected to ADB yet")
            return

        img = self.__adb.screenshot(mode="BGR")
        template_path = os.path.join(BASE_DIR, 'templates', 'upgrade_button.png')
        template = cv2.imread(template_path)
        template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)

        return find_points_match_template(img, template)

    def find_upgade_shop_elements(self):

        if not self.__adb:
            print("Not connected to ADB yet")
            return

        img = self.__adb.screenshot(mode="BGR")
        template_path = os.path.join(BASE_DIR, 'templates', 'coinshop.png')
        if self.__map == "POTION":
            template_path = os.path.join(BASE_DIR, 'templates', 'coin_potion_shop.png')
        template = cv2.imread(template_path)
        template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)

        return find_points_match_template(img, template, threshold=0.9, check=True)


    def find_finish_button(self):

        if not self.__adb:
            print("Not connected to ADB yet")
            return

        img = self.__adb.screenshot(mode="BGR")
        template_path = os.path.join(BASE_DIR, 'templates', 'finished_button.png')
        template = cv2.imread(template_path)
        template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)

        return find_points_match_template(img, template)


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

        #screenshot = self.__adb.screenshot(default="CORE")

        cropped_img = self.__adb.crop_screen((left, top, right, bottom))#screenshot.crop((left, top, right, bottom))

        if cropped_img is not None:
            img2 = cv2.cvtColor(cropped_img, cv2.COLOR_RGBA2BGR)

            if check_same_images(img1, img2):
                return True
            else:
                return False
        else:
            print("Loi check max swipe")
            return None
