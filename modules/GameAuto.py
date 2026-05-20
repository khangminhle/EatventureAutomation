import time
from typing import Optional

from .ADB import ADBController
from .GameDetector import GameDetector
from .Constants import GameMode
from .Constants import UICoordinates
from .Constants import SwipeConfig
from .Constants import TemplateConfig

class GameStateNormal:
	
class GameAuto:

	def __init__(self):
		try:
			self.__adb = None
			self.__detector = None
			self.__map = GameMode.NORMAL
			self.__swipe_turn = 0

		except Exception as e:
			print("Error GameAuto():", e)

	def config(self):
		try:
			self.__adb = ADBController()
			if not self.__adb.is_ready():
				if not self.__adb.connect():
					return False

				self.__adb.config()

			self.__detector = GameDetector(self.__adb, self.__map)

			# Load templates
			TemplateConfig.load_templates()

			return True

		except Exception as e:
			print("Erorr GameAuto - config():", e)
			return False

	def click_upgrade_shop(self):
		try:
			if not self.__detector or not self.__adb:
				return False

			while self.__detector.find_upgrade_shop_elements():
				for _ in range(TemplateConfig.CLICK_RETRY_COUNT):
					# Default x, y for first element position
					self.__adb.click(UICoordinates.FIRST_ELEMENT['x'], UICoordinates.FIRST_ELEMENT['y'])
				time.sleep(1)
			# Default x, y for closing upgrade shop
			self.__adb.click(UICoordinates.CLOSE_SHOP['x'], UICoordinates.CLOSE_SHOP['y'])

		except Exception as e:
			print("Error GameAuto - click_upgrade_shop:", e)

	def handle_upgrade_shop(self):
		try:
			if not self.__detector or not self.__adb:
				return False

			flag = self.__detector.find_upgrade_shop()

			if not flag:
				print("Khong tim thay nut upgrade shop")
				return False

			self.__adb.click(UICoordinates.UPGRADE_SHOP_BTN['x'], UICoordinates.UPGRADE_SHOP_BTN['y'])
			print("Da tim thay mui ten upgrade shop")

			self.click_upgrade_shop()

		except Exception as e:
			print("Error GameAuto - handle_upgrade_shop:", e)

	def click_boxes(self):
		try:
			if not self.__detector or not self.__adb:
				return False

			points = self.__detector.find_boxes()

			if not points:
				print("Khong tim thay boxes nao!")
				return False

			for x, y in points:
				self.__adb.click(x, y)
				time.sleep(SwipeConfig.CLICK_DELAY)

			return True
		except Exception as e:
			print("Error GameAuto - click_boxes:", e)

	def swipe_button_coin(self):

		try:
			if not self.__detector or not self.__adb:
				return False

			while True:
				points = self.__detector.find_button_coin()

				if not points:
					print("Khong tim thay button coin")
					# Click outside point to stop swiping
					self.__adb.click(UICoordinates.OUTSIDE['x'], UICoordinates.OUTSIDE['y'])
					return False

				for x, y in points:
					self.__adb.click(x, y)
					self.__adb.swipe(x, y, x, y)
					break

		except Exception as e:
			print("Error GameAuto - swipe_button_coin:", e)
		#return True

	def handle_upgrade_food(self):

		try:
			if not self.__detector or not self.__adb:
				return False

			points = self.__detector.find_upgrade_food()

			if not points:
				print("Khong tim thay mui ten upgrade food")
				return False

			#print("food")
			#print(points)
			for x, y in points:
				self.__adb.click(x, y)
				print(f'Da click vao vi tri {x} {y}')
				self.swipe_button_coin()

		except Exception as e:
			print("Error GameAuto - handle_upgrade_food:", e)

	def click_open_new_map(self):

		try:
			if not self.__detector or not self.__adb:
				return False

			flag = self.__detector.find_open_button()

			if not flag:
				print("Khong tim thay nut open")
				return False

			self.__adb.click(UICoordinates.OPEN_BTN['x'], UICoordinates.OPEN_BTN['y'])

		except Exception as e:
			print("Error GameAuto - click_open_new_map:", e)

	def handle_nothing_upgrade(self):

		if not self.__detector or not self.__adb:
			return False

		try:
			flag = self.__detector.check_nothing_upgrade()

			while not flag:

				print("Phat hien khong con gi de upgrade")

				#self.click_boxes()
				self.__adb.click(UICoordinates.OUTSIDE['x'], UICoordinates.OUTSIDE['y'])

				x = self.__adb.screen_center_x
				y = self.__adb.screen_center_y

				# SWIPE UP OR DOWN (initially swipe DOWN for the first time)
				self.__adb.swipe(x, y, x, y + self.__adb.distanceToSwipe, SwipeConfig.SWIPE_DURATION)

				flag = self.__detector.check_nothing_upgrade()

				if flag:
					return

				self.click_finish_button()
				self.click_open_new_map()
				self.click_boxes()

				checked = False
				if self.__adb.distanceToSwipe < 0:
					print("SWIPE DOWN")
					# check bottom region crop
					checked = self.__detector.check_max_swipe("bottom")
				else:
					print("SWIPE UP")
					# check top region crop
					checked = self.__detector.check_max_swipe("top")

				if checked:
					self.__swipe_turn += 1
					# Reverse swipe UP to DOWN and vice versa
					self.__adb.distanceToSwipe = self.__adb.distanceToSwipe * -1

					# Check if we finish 1 round for swipping DOWN and UP
					if self.__swipe_turn == SwipeConfig.MAX_SWIPE_TURNS:
						print("DA XONG 1 TURN SWIPE")
				else:
					if checked is None:
						raise Exception("Khong the check max swipe")

					self.crop_swipe()

		except Exception as e:
			print("Error GameAuto - handle_nothing_upgrade:", e)


	def click_finish_button(self):
		try:
			if not self.__detector or not self.__adb:
				return False

			flag = self.__detector.find_finish_button()

			if not flag:
				print("Khong tim thay nut finish")
				return False

			self.__adb.click(UICoordinates.FINISH_BTN['x'], UICoordinates.FINISH_BTN['y'])
			time.sleep(1)
			self.__adb.click(UICoordinates.RENOVATE_BTN['x'], UICoordinates.RENOVATE_BTN['y'])

		except Exception as e:
			print("Error GameAuto - click_finish_button:", e)
			return False

	def crop_swipe(self):

		if not self.__detector or not self.__adb:
			return False

		try:
			# Top region
			left = SwipeConfig.SWIPE_TOP_REGION['left']
			top = SwipeConfig.SWIPE_TOP_REGION['top']
			right = SwipeConfig.SWIPE_TOP_REGION['right']
			bottom = SwipeConfig.SWIPE_TOP_REGION['bottom']

			# Bottom region
			new_top = SwipeConfig.SWIPE_BOTTOM_REGION['top']
			new_bottom = SwipeConfig.SWIPE_BOTTOM_REGION['bottom']

			cropped_img = self.__adb.crop_screen((left, top, right, bottom))#screenshot.crop((left, top, right, bottom))

			if cropped_img is not None:
				self.__adb.save_image(cropped_img, name="check_swipe")
			else:
				print("Loi crop swipe top")
				return None

			cropped_img = self.__adb.crop_screen((left, new_top, right, new_bottom))#screenshot.crop((left, new_top, right, new_bottom))

			if cropped_img is not None:
				self.__adb.save_image(cropped_img, name="check_swipe_bottom")
			else:
				print("Loi crop swipe bottom")
				return None

		except Exception as e:
			print("Error GameAuto - crop_swipe:", e)

	def start(self):

		try:
			# SET UP CONFIG
			if not self.config():
				print("Khong the start auto")
				return False

			self.crop_swipe()
			print("Auto started!")
			while(True):
				print("New loop")
				self.handle_upgrade_food()
				self.click_boxes()
				self.swipe_button_coin()
				self.handle_upgrade_shop()
				self.handle_nothing_upgrade()

				time.sleep(SwipeConfig.LOOP_DELAY)

		except KeyboardInterrupt:
			print("Auto stopped!")


if __name__ == '__main__':
	print("Run GameAuto.py")
else:
	print("Imported GameAuto.py")