# -*- coding:utf-8 -*-

""" Button模块 """



# 自带模块
import random

# 自定义模块
from config import (MAP_SIZE, SCREEN_SIZE)



class Food_Node(object):
	def __init__(self, image, map_pos, food, map, add_length, add_queue_num, renewable):
		# 绑定食物、图片、坐标
		self.food           = food
		self.image          = image
		self.map            = map
		self.map_pos        = map_pos
		self.visible        = False
		self.screen_pos     = None

		self.rect           = image.get_rect()
		self.w              = self.rect.width
		self.h              = self.rect.height
		self.radius         = self.w // 2

		# 食物图片在屏幕上可见的最小左上角的屏幕坐标和在地图上不越界的最大左上角的地图坐标
		self.min_screen_pos = (- self.w, - self.h)
		self.max_map_pos    = (MAP_SIZE[0] - self.w, MAP_SIZE[1] - self.h)

		# 绑定吃该食物可增加的长度和额外队列数量
		self.add_length    = add_length
		self.add_queue_num = add_queue_num

		# 是否可再生
		self.renewable = renewable

	def update(self):
		x1, y1          = self.map.map_pos
		x2, y2          = self.map_pos
		x,  y           = x2 - x1, y2 - y1
		min_x, min_y    = self.min_screen_pos
		invisible       = x < min_x or y < min_y or x > SCREEN_SIZE[0] or y > SCREEN_SIZE[1]
		self.screen_pos = (x, y)
		self.visible    = not invisible



class Base_Food(Food_Node):
	# 基础食物，可再生
	def __init__(self, image, map_pos, food, map):
		super(Base_Food, self).__init__(image, map_pos, food, map, 6, 2, True)



class Extra_Food(Food_Node):
	# 额外食物，不可再生
	def __init__(self, image, map_pos, food, map):
		super(Extra_Food, self).__init__(image, map_pos, food, map, 12, 4, False)



class Food(object):
	def __init__(self, images, num, map):
		# 绑定地图、图片，初始化图片数据
		self.map            = map
		self.images         = images
		self.max_img_index  = len(self.images) - 1
		self.num            = num

		w, h                = self.images[0].get_rect().size
		self.max_map_pos    = (MAP_SIZE[0] - w, MAP_SIZE[1] - h)

		# 初始化食物队列
		self.queue          = self.creat_queue()

	# 渲染
	def draw(self, screen):
		# 如果食物屏幕可见则绘制否则跳过
		for food in self.queue:
			if food.visible:
				screen.blit(food.image, food.screen_pos)

	# 更新
	def update(self):
		for food in self.queue:
			food.update()

	# 食物再生
	def spawn(self, index):
		if self.queue[index].renewable:
			self.queue[index] = self.creat_base_food()
		else:
			self.num         -= 1
			self.queue.pop(index)

	# 增加额外食物
	def add_extra_food(self, image, positions):
		queue     = [Extra_Food(image, pos, self, self.map) for pos in positions]
		num       = len(queue)
		self.num += num
		self.queue.extend(queue)

	# 创建新食物
	def creat_base_food(self):
		image   = self.random_image()
		map_pos = self.random_pos()
		food    = Base_Food(image, map_pos, self, self.map)
		return food

	# 制造食物队列
	def creat_queue(self):
		queue = [self.creat_base_food() for i in xrange(self.num)]
		return queue

	# 随机图片
	def random_image(self):
		index = random.randint(0, self.max_img_index)
		image = self.images[index]
		return image

	# 随机坐标
	def random_pos(self):
		x = random.randint(0, self.max_map_pos[0])
		y = random.randint(0, self.max_map_pos[1])
		return (x, y)