from .ADB import ADBController
from .GameDetector import GameDetector
import time

class GameAuto:

	def __init__(self):
		try:
			self.__adb = None
			self.__detector = None

		except Exception as e:
			print("Error GameAuto():", e)

	def config(self):
		try:
			self.__adb = ADBController()
			if not self.__adb.isReady():
				self.__adb.connect()
				self.__adb.config()

			self.__detector = GameDetector(self.__adb)
		except Exception as e:
			print("Erorr GameAuto - config():", e)

	def click_upgrade_shop(self):
		try:
			if not self.__detector:
				return False

			flag = self.__detector.find_upgade_shop_elements()

			if not flag:
				print("Khong tim thay cac elements trong shop")
				return False 

			for _ in range(10):
				# Default x, y for first element position
				self.__adb.click(850, 950)
				time.sleep(0.1)

			# Default x, y for closing upgrade shop
			self.__adb.click(920, 800)
			time.sleep(0.1)
			self.click_upgrade_shop()

		except Exception as e:
			print("Error GameAuto - click_upgrade_shop:", e)

	def handle_upgrade_shop(self):
		try:
			if not self.__detector:
				return False

			points = self.__detector.find_upgrade_shop()

			if not points:
				print("Khong tim thay nut upgrade shop")
				return False

			for x,y in points:
				self.__adb.click(x, y)
				print("Da tim thay mui ten upgrade shop")
				break

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

			points = self.__detector.find_button_coin()

			if not points:
				print("Khong tim thay button coin")
				# Click outside point to stop swiping
				self.__adb.click(550, 400) 
				return False

			for x, y in points:
				self.__adb.click(x, y)
				self.__adb.swipe(x, y, x, y)
				break

			self.swipe_button_coin()

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

			for x, y in points:
				self.__adb.click(x, y)
				print(f'Da click vao vi tri {x} {y}')
				self.swipe_button_coin()
				time.sleep(0.1)
		except Exception as e:
			print("Error GameAuto - handle_upgrade_food:", e)

	def handle_nothing_upgrade(self):

		flag = self.__detector.check_nothing_upgrade()

		while not flag:

			print("Phat hien khong con gi de upgrade")

			x = self.__adb.screen_center_x
			y = self.__adb.screen_center_y

			# VIET HAM XU LY SWIPE LEN XUONG, TIM UPPER VA LOWER BOUND
			self.__adb.swipe(x, y, x, y + self.__adb.distanceToSwipe, duration=0.5)
			# VIET THEM HAM XU LY
			flag = self.__detector.check_nothing_upgrade()

	def start(self):
		# SET UP CONFIG
		self.config()

		try:
			while(True):
				print("Auto started!")
				self.handle_upgrade_food()
				self.click_boxes()
				self.handle_upgrade_shop()

				self.handle_nothing_upgrade()

				time.sleep(0.5)
		except KeyboardInterrupt:
			print("Auto stopped!")


if __name__ == '__main__':
	print("Run GameAuto.py")
else:
	print("Imported GameAuto.py")