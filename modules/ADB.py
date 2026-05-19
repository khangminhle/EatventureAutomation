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

	def click(self, x, y):
		if self.__core:
			self.__core.click(x * self.scale_x, y * self.scale_y)

	def swipe(self, fx, fy, tx, ty, duration=3.0):
		if self.__core:
			fx = fx * self.scale_x
			fy = fy * self.scale_y
			tx = tx * self.scale_x
			ty = ty * self.scale_y
			self.__core.swipe(fx, fy, tx, ty, duration)


	def screenshot(self, mode="BGR", default=""):

		if not self.__core:
			print("Not connected to ADB yet")
			return

		if default == "CORE":
			return self.__core.screenshot()

		"""Tối ưu hóa lấy ảnh bằng screencap qua stdout"""
		cmd = ["adb", "exec-out", "screencap"]
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		stdout, _ = process.communicate()

		width = int.from_bytes(stdout[0:4], byteorder='little')
		height = int.from_bytes(stdout[4:8], byteorder='little')
		expected_size = width * height * 4

		frame = np.frombuffer(stdout, dtype=np.uint8, count=expected_size, offset=12)
		frame = frame.reshape((height, width, 4))

		if mode == "BGR":
		    return cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

		if mode == "GRAY":
		    return cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)

		return None

	def save_screenshot(self, mode="BGR"):
		if not self.__core:
			print("Not connected to ADB yet")
			return

		image = self.screenshot(mode)
		cv2.imwrite("screenshot.png", image)
		print("Saved screenshot.png")