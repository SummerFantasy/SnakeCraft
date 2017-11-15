# -*- coding:utf-8 -*-

""" MiniMap模块 """



# 自定义模块
from config import MAP_SIZE



class Member(object):
	def __init__(self, image, target, minimap):
		self.minimap    = minimap
		self.image      = image
		self.w, self.h  = image.get_rect().size
		self.half_w     = self.w // 2
		self.half_h     = self.h // 2
		self.target     = target
		self.screen_pos_update()

	# 屏幕坐标更新
	def screen_pos_update(self):
		# 求出目标在地图上的位置等比例映射到迷你地图上的屏幕坐标
		x1, y1 = self.target.map_pos
		x2, y2 = self.minimap.screen_pos
		x      = x2 + x1 / MAP_SIZE[0] * self.minimap.w - self.half_w
		y      = y2 + y1 / MAP_SIZE[1] * self.minimap.h - self.half_h
		self.screen_pos = (x, y)

class MiniMap(object):
	# 初始化
	def __init__(self, images):
		# 绑定图片，初始化底图及图片属性，屏幕坐标
		self.images        = images
		self.background    = images[0]
		self.w, self.h     = self.background.get_rect().size
		self.screen_pos    = (0, 0)

		# 设置玩家和敌人图标图片
		self.me_image      = images[1]
		self.enemy_image_0 = images[2]
		self.enemy_image_1 = images[3]
		self.queue         = []

	# 增加目标成员
	def add_member(self, image, target):
		member = Member(image, target, self)
		self.queue.append(member)

	# 渲染
	def draw(self, screen):
		screen.blit(self.background, self.screen_pos)
		for member in self.queue:
			if member.target.alive:
				screen.blit(member.image, member.screen_pos)

	# 更新
	def update(self):
		# 更新成员屏幕坐标
		for member in self.queue:
			member.screen_pos_update()