# -*- coding:utf-8 -*-

""" 游戏模块 """



# 自带模块
import os
import sys

# 第三方模块
import pygame
from pygame.locals import QUIT

# 自定义模块
import scene_start
from config import (SCREEN_SIZE, FPS, MUSIC, SOUND)



class Game(object):
	def __init__(self):
		# 游戏窗口初始化
		pygame.init()
		self.screen         = pygame.display.set_mode(SCREEN_SIZE)

		# 游戏时间初始化
		self.clock          = pygame.time.Clock()

		# 游戏帧率
		self.fps            = FPS

		# 游戏循环标志
		self.loop           = True

		# 游戏音乐和音效控制
		self.music          = MUSIC
		self.sound          = SOUND

		# 游戏监听事件
		self.event_listener = {}

		# 游戏场景
		self.scene          = scene_start.Scene_Start(self)

	# 设置游戏监听事件
	def set_event_listener(self, event_listener):
		self.event_listener = event_listener

	# 设置游戏场景
	def set_scene(self, scene):
		self.scene          = scene

	# 保持配置
	def save_config(self):
		# 读模式打开配置文件，读取所有内容，保存配置内容
		filename = os.path.join('lib', 'config.py')
		config   = open(filename, 'r')
		lines    = config.readlines()
		num      = len(lines)
		for i in xrange(num):
			if 'MUSIC' in lines[i]:
				if self.music:
					lines[i] = 'MUSIC       = True\n'
				else:
					lines[i] = 'MUSIC       = False\n'
			elif 'SOUND' in lines[i]:
				if self.sound:
					lines[i] = 'SOUND       = True\n'
				else:
					lines[i] = 'SOUND       = False\n'
		config.close()

		# 写模式打开配置，将修改后的配置内容写入
		config = open(filename, 'w')
		config.writelines(lines)
		config.close()

	# 游戏运行
	def run(self):
		while self.loop:
			self.clock.tick(self.fps)
			for event in pygame.event.get():

				# 关闭窗口时保存对游戏配置的修改
				if event.type == QUIT:
					self.save_config()
					sys.exit()
				elif event.type in self.event_listener.keys():
					self.event_listener[event.type](event)
			self.scene.draw(self.screen)
			self.scene.update()
			pygame.display.update()

		# 退出游戏时保存对游戏配置的游戏
		self.save_config()
		sys.exit()