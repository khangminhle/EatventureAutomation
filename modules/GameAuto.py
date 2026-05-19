import time

from .ADB import ADBController
from .GameDetector import GameDetector
from .Constants import *

class GameAuto:

	def __init__(self):
		try:
			self.__adb = None
			self.__detector = None
			self.__map = "NORMAL"

			self.__max_swipe_turn = 2
			self.__swipe_turn = 0

		except Exception as e:
			print("Error GameAuto():", e)

	def config(self):
		try:
			self.__adb = ADBController()
			if not self.__adb.isReady():
				if not self.__adb.connect():
					return False

				self.__adb.config()

			self.__detector = GameDetector(self.__adb, self.__map)

			return True

		except Exception as e:
			print("Erorr GameAuto - config():", e)
			return False

	def click_upgrade_shop(self):
		try:
			if not self.__detector:
				return False

			'''
			while True:

				flag = self.__detector.find_upgrade_shop_elements()

				if not flag:
					print("Khong tim thay cac elements trong shop")
					break

				for _ in range(10):
					# Default x, y for first element position
					self.__adb.click(DEFAULT_FIRST_ELEMENT_X, DEFAULT_FIRST_ELEMENT_Y)

			# Default x, y for closing upgrade shop
			self.__adb.click(DEFAULT_CLOSING_UPGRADE_X, DEFAULT_CLOSING_UPGRADE_Y)

			'''
			if self.__detector.find_upgrade_shop_elements():
				for _ in range(10):
					# Default x, y for first element position
					self.__adb.click(DEFAULT_FIRST_ELEMENT_X, DEFAULT_FIRST_ELEMENT_Y)
				# Default x, y for closing upgrade shop
				self.__adb.click(DEFAULT_CLOSING_UPGRADE_X, DEFAULT_CLOSING_UPGRADE_Y)
		except Exception as e:
			print("Error GameAuto - click_upgrade_shop:", e)

	def handle_upgrade_shop(self):
		try:
			if not self.__detector:
				return False

			flag = self.__detector.find_upgrade_shop()

			if not flag:
				print("Khong tim thay nut upgrade shop")
				return False

			self.__adb.click(DEFAULT_UPGRADE_SHOP_X, DEFAULT_UPGRADE_SHOP_Y)
			print("Da tim thay mui ten upgrade shop")
			'''
			for x,y in points:
				self.__adb.click(x, y)
				print("Da tim thay mui ten upgrade shop")
				break
			'''
			self.click_upgrade_shop()

		except Exception as e:
			print("Error GameAuto - handle_upgrade_shop:", e)

	def click_boxes(self):
		try:
			if not self.__detector:
				return False

			points = self.__detector.find_boxes()

			if not points:
				print("Khong tim thay boxes nao!")
				return False

			for x, y in points:
				self.__adb.click(x, y)
				time.sleep(0.1)

			return True
		except Exception as e:
			print("Error GameAuto - click_boxes:", e)

	def swipe_button_coin(self):

		try:
			if not self.__detector:
				return False

			while True:
				points = self.__detector.find_button_coin()

				if not points:
					print("Khong tim thay button coin")
					# Click outside point to stop swiping
					self.__adb.click(DEFAULT_OUTSIDE_X, DEFAULT_OUTSIDE_Y)
					print("outside:", DEFAULT_OUTSIDE_X, DEFAULT_OUTSIDE_Y)
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
			if not self.__detector:
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
			if not self.__detector:
				return False

			flag = self.__detector.find_open_button()

			if not flag:
				print("Khong tim thay nut open")
				return False

			self.__adb.click(DEFAULT_OPEN_BTN_X, DEFAULT_OPEN_BTN_Y)

		except Exception as e:
			print("Error GameAuto - click_open_new_map:", e)

	def handle_nothing_upgrade(self):

		try:
			flag = self.__detector.check_nothing_upgrade()

			while not flag:

				print("Phat hien khong con gi de upgrade")

				#self.click_boxes()
				self.__adb.click(DEFAULT_OUTSIDE_X, DEFAULT_OUTSIDE_Y)
				print("outside:", DEFAULT_OUTSIDE_X, DEFAULT_OUTSIDE_Y)

				x = self.__adb.screen_center_x
				y = self.__adb.screen_center_y

				# SWIPE UP OR DOWN (initially swipe DOWN for the first time)
				self.__adb.swipe(x, y, x, y + self.__adb.distanceToSwipe, duration=0.5)

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
					if self.__swipe_turn == self.__max_swipe_turn:
						print("DA XONG 1 TURN SWIPE")

						# Check if the game is finished ?
						#if self.click_finish_button():
						#	return
						#self.click_open_button()
				else:
					if checked is None:
						raise Exception("Khong the check max swipe")

					self.crop_swipe()

		except Exception as e:
			print("Error GameAuto - handle_nothing_upgrade:", e)


	def click_finish_button(self):
		try:
			if not self.__detector:
				return False

			flag = self.__detector.find_finish_button()

			if not flag:
				print("Khong tim thay nut finish")
				return False

			self.__adb.click(DEFAULT_FINISH_BTN_X, DEFAULT_FINISH_BTN_Y)
			time.sleep(1)
			self.__adb.click(DEFAULT_RENOVATE_X, DEFAULT_RENOVATE_Y)

		except Exception as e:
			print("Error GameAuto - click_finish_button:", e)
			return False

	def crop_swipe(self):
		try:
			# Top region
			left = 10 * self.__adb.scale_x
			top = 270 * self.__adb.scale_y
			right = 90 * self.__adb.scale_x
			bottom = 300 * self.__adb.scale_y

			# Bottom region
			new_top = 2080 * self.__adb.scale_x
			new_bottom = 2110 * self.__adb.scale_y

			#screenshot = self.__adb.screenshot(default="CORE")

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

				time.sleep(0.5)

		except KeyboardInterrupt:
			print("Auto stopped!")


if __name__ == '__main__':
	print("Run GameAuto.py")
else:
	print("Imported GameAuto.py")