# -*- coding:utf-8 -*-

""" Menu模块 """



class Menu(object):
	def __init__(self, buttons = None):
		self.buttons = buttons

	def draw(self, screen):
		for button in self.buttons:
			button.draw(screen)

	def update(self, pos, click):
		for button in self.buttons:
			button.update(pos, click)