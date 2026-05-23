import time
from typing import Optional
from enum import Enum, auto 

from .ADB import ADBController
from .GameDetector import GameDetector
from .Constants import GameMode, ImageColor
from .Constants import UICoordinates
from .Constants import SwipeConfig
from .Constants import TemplateConfig
from .Constants import GameStates

from .GameStateManager import StateFinish, StateFoodUpgrade, StateNothingUpgrade, StateShopUpgrade, StateUnbox, StateWatchingAds

class GameAuto:

	def __init__(self):
		try:
			self.__adb = None
			self.__detector = None
			self.__map = GameMode.NORMAL
			self.__currentState = GameStates.WATCHING_ADS
			self.__states = {}

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

			# Load GameStates
			self.__states[GameStates.FOOD_UPGRADE] = StateFoodUpgrade(self.__adb, self.__detector)
			self.__states[GameStates.SHOP_UPGRADE] = StateShopUpgrade(self.__adb, self.__detector)
			self.__states[GameStates.UNBOX] = StateUnbox(self.__adb, self.__detector)
			self.__states[GameStates.NOTHING_UPGRADE] = StateNothingUpgrade(self.__adb, self.__detector)
			self.__states[GameStates.FINISH] = StateFinish(self.__adb, self.__detector)
			self.__states[GameStates.WATCHING_ADS] = StateWatchingAds(self.__adb, self.__detector)

			return True

		except Exception as e:
			print("Erorr GameAuto - config():", e)
			return False


	def start(self):

		try:
			# SET UP CONFIG
			if not self.config():
				print("Khong the start auto")
				return False

			self.__adb.crop_swipe()


			print("Auto started!")
			while(True):

				print("\n----- New loop - ",self.__currentState)

				if self.__currentState == GameStates.WATCHING_ADS:

					state = self.__states[GameStates.WATCHING_ADS].start()

					if state is True:
						self.__currentState = GameStates.FOOD_UPGRADE
					print('state:', state)
					time.sleep(2)
					continue

				if self.__currentState == GameStates.EXIT:
					print("Da xay ra loi. Thoat game!")
					return False


				state = self.__states[self.__currentState].start()
				print('state:', state)

				if state is None:
					self.__states = GameStates.EXIT
					continue

				match self.__currentState:

					case GameStates.FOOD_UPGRADE:
						#if state is False:
						#self.__states[GameStates.UNBOX].start()
						#self.__states[GameStates.SHOP_UPGRADE].start()
						self.__currentState = GameStates.UNBOX

					case GameStates.SHOP_UPGRADE:
						#if state is False:
						self.__currentState = GameStates.NOTHING_UPGRADE

					case GameStates.UNBOX:
						#if state is False:
						self.__currentState = GameStates.SHOP_UPGRADE

					case GameStates.NOTHING_UPGRADE:
						self.__currentState = state
						'''
						if state is False:
							self.__currentState = GameStates.FOOD_UPGRADE
						elif state == 'finish':
							self.__currentState = GameStates.FINISH
						'''
					case GameStates.FINISH:
						self.__currentState = GameStates.WATCHING_ADS#GameStates.FOOD_UPGRADE

				print("Trang thai ke tiep:", self.__currentState)
				time.sleep(SwipeConfig.DELAY_EACH_STATE)

		except KeyboardInterrupt:
			print("Auto stopped!")


if __name__ == '__main__':
	print("Run GameAuto.py")
else:
	print("Imported GameAuto.py")