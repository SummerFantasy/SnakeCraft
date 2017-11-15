# -*- coding:utf-8 -*-

""" Map模块 """



# 第三方模块
from pygame.locals import Rect

# 自定义模块
import util
from config import (SCREEN_SIZE, MAP_SIZE)



class Map(object):
	# 初始化
	def __init__(self):
		self.map_image     = util.load_image('map.png')
		self.center        = None
		self.screen_half_w = SCREEN_SIZE[0] // 2
		self.screen_half_h = SCREEN_SIZE[1] // 2
		self.map_pos       = None
		self.rect          = None
		self.image         = None
		self.screen_pos    = (0, 0)

	# 设置追踪目标
	def set_target(self, target):
		self.center        = target
		self.pos_update()
		self.rect_update()
		self.image_update()

	# 渲染
	def draw(self, screen):
		screen.blit(self.image, self.screen_pos)

	# 更新
	def update(self):
		self.pos_update()
		self.rect_update()
		self.image_update()
		self.screen_pos_update()

	# 地图坐标更新
	def pos_update(self):
		x, y = self.center.map_pos
		x -= self.screen_half_w
		y -= self.screen_half_h
		self.map_pos  = (x, y)

	# 地图区域更新
	def rect_update(self):
		x, y = self.map_pos
		w, h = SCREEN_SIZE
		if x < 0:
			w += x
			x = 0
		if x > MAP_SIZE[0] - w:
			w = MAP_SIZE[0] - x
		if y < 0:
			h += y
			y = 0
		if y > MAP_SIZE[1] - h:
			h = MAP_SIZE[1] - y
		self.rect = Rect(x, y, w, h)

	# 地图图片更新
	def image_update(self):
		self.image = self.map_image.subsurface(self.rect)

	# 地图屏幕坐标更新
	def screen_pos_update(self):
		x, y = self.map_pos
		if 0 <= x <= MAP_SIZE[0] and 0 <= y <= MAP_SIZE[1]:
			self.screen_pos = (0, 0)
		elif x < 0 and y < 0:
			self.screen_pos = (-x, -y)
		elif x < 0 and 0 <= y <= MAP_SIZE[1]:
			self.screen_pos = (-x, 0)
		elif y < 0 and 0 <= x <= MAP_SIZE[0]:
			self.screen_pos = (0, -y)