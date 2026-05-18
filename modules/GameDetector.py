import os
import cv2
import glob
import numpy as np
from .ImageProcess import *
from .Constants import *


class GameDetector:

	def __init__(self, adb: ADBController):
		self.__adb = adb

	def check_nothing_upgrade(self):

		actions = [self.find_upgrade_food, self.find_upgrade_shop, self.find_boxes]

		for action in actions:
			if action():
				return True
		
		return False


	def find_upgrade_food(self):
		if not self.__adb:
			print("Not connected to ADB yet")
			return

		img = self.__adb.screenshot(mode="GRAY")
		template_path = os.path.join(BASE_DIR, 'templates', 'button_test.png')
		template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
		template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)
		points = find_points_match_template(img, template)

		# Loại bỏ các điểm vượt giới hạn Y
		return [(x, y + 20) for x, y in points if y + 20 < self.__adb.upper_bound_y]


	def find_button_coin(self):
		if not self.__adb:
			print("Not connected to ADB yet")
			return

		img = self.__adb.screenshot(mode="GRAY")
		template_path = os.path.join(BASE_DIR, 'templates', 'button_coin.png')
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
				return points

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
		template = cv2.imread(template_path)
		template = resize_template(template, self.__adb.scale_x, self.__adb.scale_y)

		return find_points_match_template(img, template, threshold=0.9, check=True)


	