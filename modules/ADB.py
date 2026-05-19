import adbutils
import subprocess
import cv2
import numpy as np
from .Constants import *

class ADBController:
	def __init__(self):
		self.__core = None
		self.screen_center_x = 0
		self.screen_center_y = 0
		self.scale_x = 1.0
		self.scale_y = 1.0
		self.upper_bound_y = 2120
		self.max_screen_x = 0
		self.max_screen_y = 0

		self.distanceToSwipe = 0


	def isReady(self):
		if self.__core is None:
			return False 
		else:
			return True

	def config(self):

		if self.isReady():
			info = self.__core.window_size()
			self.screen_center_x = info.width // 2
			self.screen_center_y = info.height // 2
			self.distanceToSwipe = -self.screen_center_y / 5
			self.scale_x = info.width / DEFAULT_TEMPLATE_WIDTH
			self.scale_y = info.height / DEFAULT_TEMPLATE_HEIGHT
			self.max_screen_x = info.width
			self.max_screen_y = info.height

	def connect(self):
		try:
			# Only connect to ADB when not connected
			if self.__core is None:
				adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
				print('Connect to device', adb.device())
				self.__core = adb.device()

				return True

		except Exception as e:
			print('Error ADBController - connect():', e)
			return False

	def click(self, x: int, y: int):
		if self.__core:
			self.__core.click(x * self.scale_x, y * self.scale_y)

	def swipe(self, fx: int, fy: int, tx: int, ty: int, duration=3.0):
		if self.__core:
			fx = int(fx * self.scale_x)
			fy = int(fy * self.scale_y)
			tx = int(tx * self.scale_x)
			ty = int(ty * self.scale_y)
			self.__core.swipe(fx, fy, tx, ty, duration)

	def __screencap(self):

		if not self.__core:
			print("Not connected to ADB yet")
			return

		try:
			"""Tối ưu hóa lấy ảnh bằng screencap qua stdout"""
			cmd = ["adb", "exec-out", "screencap"]
			process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
			stdout, _ = process.communicate()

			width = int.from_bytes(stdout[0:4], byteorder='little')
			height = int.from_bytes(stdout[4:8], byteorder='little')
			expected_size = width * height * 4

			if len(stdout) < expected_size + 12:
				print("Frame thieu byte")
				return None

			frame = np.frombuffer(stdout, dtype=np.uint8, count=expected_size, offset=12)
			frame = frame.reshape((height, width, 4))

			# Image RGBA
			return frame

		except Exception as e:
			print("Error screencap:", e)

	def crop_screen(self, position: tuple[int, int, int, int]):


		if len(position) < 4 or len(position) > 4:
			print("Du hoac thieu position")
			return None

		try:
			left, top, right, bottom = [int(coord) for coord in position]
		except Exception as e:
			print("Error ADB - crop_screen:", e)
			return None

		if left < 0 or top < 0 or right < 0 or bottom < 0:
			print("left, top, right, bottom khong duoc < 0")
			return None

		if left >= right or top >= bottom:
			print("Khong the crop vi left, top, right, bottom khong thoa")
			return None

		screenshot = self.__screencap()

		img =  screenshot[int(top):int(bottom), int(left):int(right)]

		# Image RGBA
		return img

	def screenshot(self, mode="BGR"):

		if not self.__core:
			print("Not connected to ADB yet")
			return None


		screenshot = self.__screencap()

		if screenshot is None:
			print("Khong the screenshot")
			return None

		if mode == "BGR":
		    return cv2.cvtColor(screenshot, cv2.COLOR_RGBA2BGR)

		if mode == "GRAY":
		    return cv2.cvtColor(screenshot, cv2.COLOR_RGBA2GRAY)

		return None

	def save_image(self, image: np.ndarray, name: str, mode: str = "BGR"):

		try:
			if isinstance(image, np.ndarray):
				if mode == "BGR":
					new_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
				if mode == "GRAY":
					new_image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
				cv2.imwrite(f'{name}.png', new_image)
				return True
			else:
				print("Input image khong hop le")
				return False

		except Exception as e:
			print("Error save_image:", e)

	def save_screenshot(self, mode="BGR"):
		if not self.__core:
			print("Not connected to ADB yet")
			return

		image = self.screenshot(mode)

		if image is not None:
			cv2.imwrite("screenshot.png", image)
			print("Saved screenshot.png")