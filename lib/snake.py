# -*- coding:utf-8 -*-

""" Snake模块 """



# 自带模块
import math
import random

# 第三方模块
import pygame

# 自定义模块
from collections import deque
from config import (MAP_SIZE, SCREEN_SIZE)



class Snake_Node(object):
	#图片节点，用于储存贪吃蛇头部和身体图片的相关各类数据并提供图片缩放功能
	def __init__(self, images, index):
		#绑定图片
		self.images = images
		self.scale(index)

	# 因为位图缩放会失真，所以采用对应等级的图片替换来完成缩放这一操作
	def scale(self, index):
		self.image        = self.images[index]
		self.w, self.h    = self.image.get_rect().size
		self.half_w       = self.w // 2
		self.half_h       = self.h // 2



class Snake_Head(Snake_Node):
	def __init__(self, images, index):
		# 调用父类初始化
		super(Snake_Head, self).__init__(images, index)

	def scale(self, index):
		super(Snake_Head, self).scale(index)
		self.base         = self.image

	# 顺时针旋转
	def rotate(self, angle):
		self.image  = pygame.transform.rotate(self.base, angle)
		w, h        = self.image.get_rect().size
		self.half_w = w // 2
		self.half_h = h // 2



class Snake_Body(Snake_Node):
	def __init__(self, images, index):
		# 调用父类初始化
		super(Snake_Body, self).__init__(images, index)



class Snake(object):
	# 初始化
	def __init__(self, images, body_num, food, map, scene):
		# 绑定场景、食物、地图、图片，初始化图片数据
		self.scene               = scene
		self.food                = food
		self.map                 = map
		self.sound               = self.scene.sound

		# 初始化贪吃蛇头部、身体图片节点
		self.head                = Snake_Head(images[0], 0)
		self.body                = Snake_Body(images[1], 0)

		# 贪吃蛇头部节点图片中心点的地图坐标、屏幕绘制坐标
		self.map_pos             = self.random_map_pos()
		self.screen_pos          = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)

		# 头部进行碰撞检测的可视范围
		self.visual_range        = self.head.w * 2

		# 头部图片的中心点在地图上可出现的最大坐标
		self.head_max_map_pos    = (MAP_SIZE[0] - self.head.half_w, MAP_SIZE[1] - self.head.half_h)

		# 身体图片的左上角在屏幕上可出现的最小坐标
		self.body_min_screen_pos = (- self.body.w, -self.body.h)

		# 死亡后复活将损失的长度比例
		self.lost_rate           = 0.5
		self.lost_images         = images[2]
		self.alive               = True

		# 初始化速度、弧度和角度，逆时针为正，顺时针为负，与数学坐标系一致
		self.speed               = 3
		self.vx                  = 0
		self.vy                  = 0
		self.radian              = 0
		self.angle               = 0

		# 初始化贪吃蛇移动路径队列
		self.draw_start          = 0
		self.draw_step           = 4
		self.base_draw_step      = self.draw_step
		self.body_num            = body_num
		self.queue_num           = body_num * self.draw_step + 1
		self.queue               = deque([self.map_pos for i in xrange(self.queue_num)])

		# 每个路径点长度为速度的两倍，根据贪吃蛇的队列路径点数量计算其长度
		self.path_length         = self.speed * 2
		self.length              = self.queue_num * self.path_length

		# 初始化额外队列数量用于贪吃蛇长度调整
		self.extra_queue_num     = 0

		# 初始化体型等级用于贪吃蛇体型调整
		self.shape_factor        = 50
		self.shape_level         = self.queue_num // self.shape_factor
		self.max_shape_level     = 9
		self.min_shape_level     = 0

		# 绑定敌方
		self.enemies             = []

	# 贪吃蛇渲染
	def draw(self, screen):
		if self.alive:
			# 如果贪吃蛇身体队列绘制起始点大于等于绘制步长则减小起始点
			if self.draw_start >= self.draw_step:
				self.draw_start -= self.draw_step
			self.draw_body(screen)
			self.draw_head(screen)

	# 渲染身体
	def draw_body(self, screen):
		# 贪吃蛇身体节点的地图坐标减去背景的地图坐标，得到其屏幕绘制坐标
		x1, y1 = self.map.map_pos
		for i in xrange(self.draw_start, self.queue_num - 1, self.draw_step):
			x2, y2 = self.queue[i]
			x,  y  = x2 - x1, y2 - y1
			x     -= self.body.half_w
			y     -= self.body.half_h

			# 判断身体是否在屏幕内，如果是则进行绘制，否则跳过
			if self.screen_visible(x, y, self.body_min_screen_pos):
				screen.blit(self.body.image, (x, y))

	# 渲染头部
	def draw_head(self, screen):
		# 贪吃蛇头部节点图片的中心点的屏幕坐标减去图片半高和半宽，得到其屏幕绘制坐标
		x, y = self.screen_pos
		x   -= self.head.half_w
		y   -= self.head.half_h
		screen.blit(self.head.image, (x, y))

	# 贪吃蛇状态更新:体型 -> 弧度 -> 旋转 —> 速度 —> 坐标 —> 队列 -> 是否加速
	def update(self, mouse_pos):
		if self.alive:
			self.shape_update()
			self.radian_update(mouse_pos)
			self.rotate_update()
			self.speed_update()
			self.pos_update()
			self.queue_update()

			# 如果按住鼠标左键则加速，双倍坐标和队列更新
			mouse_left_click = pygame.mouse.get_pressed()[0]
			if self.alive and mouse_left_click and self.length > 300:
				self.length          -= 0.12
				self.extra_queue_num -= 0.04
				self.pos_update()
				self.queue_update()

	# 体型更新
	def shape_update(self):
		# 根据队列路径点数量调整当前体型等级
		shape_level = self.queue_num // self.shape_factor

		# 如果体型等级相等则跳过
		if self.shape_level == shape_level:
			pass

		# 如果体型等级小于当前体型等级且小于最大体型等级，则增大体型
		elif self.shape_level < shape_level:
			if self.shape_level < self.max_shape_level:
				self.shape_level += 1
				self.head.scale(self.shape_level)
				self.body.scale(self.shape_level)

				self.visual_range        = self.head.w * 2
				self.body_min_screen_pos = (- self.body.w, -self.body.h)

				# 节点图片尺寸变化引起身体节点间的距离变化，绘制参数相应改变以使视觉效果不变
				self.draw_step_update()

		# 如果体型等级大于当前体型等级且大于最小体型等级，则减小体型
		elif self.shape_level > shape_level:
			if self.shape_level > self.min_shape_level:
				self.shape_level -= 1
				self.head.scale(self.shape_level)
				self.body.scale(self.shape_level)

				self.visual_range        = self.head.w * 2
				self.body_min_screen_pos = (- self.body.w, -self.body.h)

				# 节点图片尺寸变化引起身体节点间的距离变化，绘制参数相应改变以使视觉效果不变
				self.draw_step_update()

	# 绘制步长更新
	def draw_step_update(self):
		# 体型等级每增加3级，绘制步长+1
		self.draw_step  = self.base_draw_step + self.shape_level // 3
		num             = self.queue_num - 1

		# 步长改变，绘制起始点相应调整
		self.draw_start = num - num // self.draw_step * self.draw_step

	# 弧度更新
	def radian_update(self, mouse_pos):
		# 根据鼠标和贪吃蛇头部图片的中心点之间坐标差，计算弧度
		x2, y2 = mouse_pos
		x1, y1 = self.screen_pos
		x,  y  = x2 - x1, y2 - y1
		self.radian = math.atan2(y, x)

	# 旋转更新
	def rotate_update(self):
		angle = math.degrees(self.radian)
		self.head.rotate(-angle)
		self.head_max_map_pos = (MAP_SIZE[0] - self.head.half_w, MAP_SIZE[1] - self.head.half_h)

	# 速度更新
	def speed_update(self):
		self.vx = math.cos(self.radian) * self.speed
		self.vy = math.sin(self.radian) * self.speed

	# 坐标更新
	def pos_update(self):
		x, y         = self.map_pos
		self.map_pos = (x + self.vx, y + self.vy)

		# 头部坐标更新以后第一时间更新地图，保证其他实例在使用地图坐标时为最新坐标
		self.map.update()

		# 地图更新后，食物的屏幕坐标和屏幕可见性也随之更新
		self.food.update()

	# 队列更新
	def queue_update(self):
		# 检查头部是否超越地图边界或者撞到了敌人，如果是播放碰撞音效，执行死亡然后返回
		if self.overflow() or self.collide_enemy():
			self.die()
			return

		# 执行吃食物
		self.eat()

		# 如果额外队列数量大于1则增加路径点数量
		if self.extra_queue_num >= 1:
			self.queue_num       += 1
			self.draw_start      += 1
			self.extra_queue_num -= 1

		# 如果额外队列数量小于-1则减少路径点数量
		elif self.extra_queue_num <= -1:
			self.queue_num       -= 1
			self.draw_start      -= 1
			if self.draw_start < 0:
				self.draw_start += self.draw_step
			self.extra_queue_num += 1
			self.queue.popleft()
			self.queue.popleft()

		# 否则保持路径点数量不变
		else:
			self.queue.popleft()

		# 无论如何，更新后的坐标总是加入队列
		self.queue.append(self.map_pos)

	# 吃
	def eat(self):
		x1, y1     = self.map_pos
		spawn_food = []
		for i in xrange(self.food.num):
			food   = self.food.queue[i]
			x2, y2 = food.map_pos
			x2    += food.radius
			y2    += food.radius

			# 如果食物出现在头部的可视范围内，则进行碰撞检测
			x, y = abs(x2 - x1), abs(y2 - y1)
			if x < self.visual_range and y < self.visual_range:
				max_distance = pow(food.radius + self.head.half_w, 2)
				distance = pow(x, 2) + pow(y, 2)

				# 如果发生了碰撞，将食物加入到待再生列表中，更新长度和额外队列
				if distance <= max_distance:
					spawn_food.append(i)
					self.length          += food.add_length
					self.extra_queue_num += food.add_queue_num

		# 如果待再生食物不为空，则再生里面的食物
		if spawn_food:
			for i in spawn_food:
				self.food.spawn(i)

	# 绑定敌人
	def set_enemy(self, enemies):
		self.enemies.extend(enemies)

	# 检测与敌人是否碰撞
	def collide_enemy(self):
		x1, y1 = self.map_pos

		# 只当敌人活着的时候检测碰撞
		for enemy in self.enemies:
			if enemy.alive:
				for i in xrange(enemy.draw_start, enemy.queue_num - 1, enemy.draw_step):
					x2, y2 = enemy.queue[i]
					x,  y  = abs(x2 - x1), abs(y2 - y1)
					if x < self.visual_range and y < self.visual_range:
						max_distance = pow(enemy.body.half_w + self.head.half_w, 2)
						distance = pow(x, 2) + pow(y, 2)
						if distance <= max_distance:
							return True

				x2, y2 = enemy.map_pos
				x,  y  = abs(x2 - x1), abs(y2 - y1)
				if x < self.visual_range and y < self.visual_range:
					max_distance = pow(enemy.head.half_w + self.head.half_w, 2)
					distance = pow(x, 2) + pow(y, 2)
					if distance <= max_distance:
						return True

		return False

	# 屏幕可见判断，x，y为图片左上角在屏幕中的坐标，min_screen_pos为该图片在屏幕可见的最小左上角坐标
	def screen_visible(self, x, y, min_screen_pos):
		min_x, min_y = min_screen_pos
		invisible = (x < min_x or x > SCREEN_SIZE[0] or y < min_y or y > SCREEN_SIZE[1])
		return not invisible

	# 地图过界判断
	def overflow(self):
		x,  y  = self.map_pos
		x1, y1 = self.head.half_w, self.head.half_h
		x2, y2 = self.head_max_map_pos
		over   = x < x1 or y < y1 or x > x2 or y > y2
		return over

	# 死亡
	def die(self):
		if self.alive:
			self.sound['collide'].play()
			self.alive = False

			# 死亡将留下额外食物
			postions      = []
			step          = self.draw_step * 2
			for i in xrange(self.draw_start, self.queue_num - 1, step):
				x, y = self.queue[i]
				x   -= self.body.half_w
				y   -= self.body.half_h
				postions.append((x, y))

			self.food.add_extra_food(self.lost_images[self.shape_level], postions)
			self.scene.set_terminated()

	# 重生将损失一定比例的长度和体型等级
	def spawn(self):
		# 根据损失比例重置身体节点数量
		body_num             = (self.queue_num - self.draw_start - 1) // self.draw_step
		self.body_num        = int(body_num * self.lost_rate // 1)

		# 如果重生次数过多，身体节点数过少，保证最少将维持在三个节点
		if self.body_num <= 3:
			self.body_num    = 3

		# 重置路径点数量、体型等级、长度和剩余队列数量
		self.queue_num       = self.body_num * self.draw_step + 1
		self.shape_level     = self.queue_num // self.shape_factor
		self.length          = self.queue_num * self.path_length
		self.extra_queue_num = 0

		# 重置后进行体型更新和绘制步长更新
		self.shape_update()
		self.draw_step_update()

		# 重置可视范围、头部不越界最大地图坐标和身体屏幕可见最小坐标
		self.visual_range        = self.head.w * 2
		self.head_max_map_pos    = (MAP_SIZE[0] - self.head.half_w, MAP_SIZE[1] - self.head.half_h)
		self.body_min_screen_pos = (- self.body.w, -self.body.h)

		# 重置速度、弧度和角度
		self.speed               = 3
		self.vx                  = 0
		self.vy                  = 0
		self.radian              = 0
		self.angle               = 0

		# 重置坐标和队列
		self.map_pos         = self.random_map_pos()
		self.queue           = deque([(self.map_pos) for i in xrange(self.queue_num)])

		# 重置贪吃蛇生命状态
		self.alive           = True

	# 随机产生地图坐标
	def random_map_pos(self):
		x1, y1 = MAP_SIZE[0] // 6, MAP_SIZE[1] // 6
		x2, y2 = MAP_SIZE[0] - x1, MAP_SIZE[1] - y1
		x,  y  = random.randint(x1, x2), random.randint(y1, y2)
		return (x, y)



class Enemy(Snake):
	# 初始化
	def __init__(self, images, body_num, food, map, scene):
		super(Enemy, self).__init__(images, body_num, food, map, scene)

		# 初始化状态保持量和状态更新方式
		self.state_keep       = 0
		self.state_update     = self.forage_update

		# 游戏难度等于搜索食物和敌人的范围，该值越大代表敌人越强
		self.find_food_difficulty  = 150
		self.find_enemy_difficulty = 50

		# 初始化寻找敌人的范围和寻找到的敌人坐标
		self.find_enemy_range = self.find_enemy_difficulty
		self.find_enemy_pos   = None

		# 初始化寻找食物的范围和寻找到的食物坐标
		self.find_food_range  = self.find_food_difficulty
		self.find_food_pos    = None

		# 初始化发现四周边界的信号
		self.find_left        = False
		self.find_right       = False
		self.find_up          = False
		self.find_down        = False

		# 速度初始化
		self.speed_update()

	# 重载头部渲染方法
	def draw_head(self, screen):
		# 计算头部中心点的屏幕坐标再图片的半高和半宽，得到其屏幕绘制坐标
		x1, y1 = self.map.map_pos
		x2, y2 = self.map_pos
		x,  y  = x2 - x1, y2 - y1
		x     -= self.head.half_w
		y     -= self.head.half_h
		if self.screen_visible(x, y, (-self.head.w, -self.head.h)):
			screen.blit(self.head.image, (x, y))

	# 重载状态更新方法
	def update(self):
		self.state_update()

	# 觅食状态
	def forage_update(self):
		# 发现敌人将移动方向调整为敌人方向的反方向，调整速度和头部图片旋转角度，状态更改为逃离状态
		if self.find_enemy():
			self.state_keep   = 0
			self.radian_update(self.find_enemy_pos, 1)
			self.speed_update()
			self.rotate_update()
			self.state_update = self.escape_update

		# 发现食物将移动方向调整为指向食物，调整速度和头部图片旋转角度，状态更改为进食状态
		if self.find_food():
			self.state_keep   = 0
			self.radian_update(self.find_food_pos)
			self.speed_update()
			self.rotate_update()
			self.state_update = self.feed_update

		# 发现墙，将朝向发现的墙前进的速度反向，根据反向后的速度调整弧度和头部图片旋转方向，状态改为回避状态
		elif self.find_wall():
			self.state_keep   = 0
			if self.find_left or self.find_right:
				self.vx       = - self.vx
			if self.find_up or self.find_down:
				self.vy       = - self.vy
			self.adjust_radian_from_speed()
			self.rotate_update()
			self.state_update = self.avoid_update

		# 如果状态保持量大于512，则随机改变一次移动方向，否则状态保持量+1
		if self.state_keep > 512:
			self.state_keep = 0
			self.radian_update(self.random_map_pos())
			self.speed_update()
			self.rotate_update()
		else:
			self.state_keep += 1

		self.shape_update()
		self.pos_update()
		self.queue_update()

	def find_enemy(self):
		# 判断是否发现敌人的头部
		x1, y1 = self.map_pos
		for enemy in self.enemies:
			x2, y2 = enemy.map_pos
			x,  y  = abs(x2 - x1), abs(y2 - y1)
			if x < self.find_enemy_range and y < self.find_enemy_range:
				self.find_enemy_pos = (x2, y2)
				return True

			# 判断是否发现敌人的身体
			for i in xrange(enemy.draw_start, enemy.queue_num - 1, enemy.draw_step):
				x2, y2 = enemy.queue[i]
				x,  y  = abs(x2 - x1), abs(y2 - y1)
				if x < self.find_enemy_range and y < self.find_enemy_range:
					self.find_enemy_pos = (x2, y2)
					return True

		return False

	# 逃离状态
	def escape_update(self):
		# 如果依然发现敌人，继续调整为跟敌人方向相反的移动方向
		if self.find_enemy():
			self.radian_update(self.find_enemy_pos, 1)
			self.speed_update()
			self.rotate_update()

		# 否则说明脱离危险，重置寻找到的敌人坐标，状态更改为觅食状态
		else:
			self.find_enemy_pos = None
			self.state_update   = self.forage_update

		self.shape_update()
		self.pos_update()
		self.queue_update()

	# 发现食物：检测食物是否出现在可视范围内
	def find_food(self):
		x1, y1     = self.map_pos
		for i in xrange(self.food.num):
			food   = self.food.queue[i]
			x2, y2 = food.map_pos
			x2    += food.radius
			y2    += food.radius
			x,  y  = abs(x2 - x1), abs(y2 - y1)
			if x < self.find_food_range and y < self.find_food_range:
				self.find_food_pos = food.map_pos
				return True
		return False

	# 检测目标食物是否存在
	def food_exist(self):
		x1, y1     = self.map_pos
		for food in self.food.queue:
			if self.find_food_pos == food.map_pos:
				return True
		return False

	# 进食状态
	def feed_update(self):
		# 检测目标食物是否存在，如果不存在，说明食物已经被吃，重置搜寻的食物坐标，状态更改为觅食状态
		if self.find_food_pos:
			if self.food_exist():
				pass
			else:
				self.find_food_pos = None
				self.state_update  = self.forage_update
		else:
			self.state_update = self.forage_update

		self.shape_update()
		self.pos_update()
		self.queue_update()

	# 通过速度调整弧度
	def adjust_radian_from_speed(self):
		self.radian = math.atan2(self.vy, self.vx)

	# 发现墙
	def find_wall(self):
		x,  y  = self.map_pos
		x1, y1 = x - self.visual_range, y - self.visual_range
		x2, y2 = x + self.visual_range, y + self.visual_range

		self.find_left  = self.vx < 0 and x1 < 0
		self.find_right = self.vx > 0 and x2 > MAP_SIZE[0]
		self.find_up    = self.vy < 0 and y1 < 0
		self.find_down  = self.vy > 0 and y2 > MAP_SIZE[1]

		return self.find_left or self.find_right or self.find_up or self.find_down

	# 回避状态
	def avoid_update(self):
		# 如果发现墙消失，则说明已经远离边界，状态更改为觅食状态
		if not self.find_wall():
			self.state_update = self.forage_update

		self.shape_update()
		self.pos_update()
		self.queue_update()

	# 重载弧度更新方法
	def radian_update(self, map_pos, reverse = 0):
		# 根据传入的地图坐标参数和头部中心点的地图坐标之间的坐标差，计算弧度
		x1, y1 = self.map_pos
		x2, y2 = map_pos

		# 如果反向标志为真，则计算从目标点到头部方向的弧度，否则计算头部到目标点方向的弧度
		if reverse:
			x, y = x1 - x2, y1 - y2
		else:
			x, y = x2 - x1, y2 - y1

		self.radian = math.atan2(y, x)

	# 重载体型更新方法
	def shape_update(self):
		# 根据队列路径点数量计算当前体型等级
		shape_level = self.queue_num // self.shape_factor

		# 如果体型等级相等则跳过
		if self.shape_level == shape_level:
			pass

		# 如果体型等级小于当前体型等级且小于最大体型等级，则增大体型
		elif self.shape_level < shape_level:
			if self.shape_level < self.max_shape_level:
				self.shape_level += 1
				self.head.scale(self.shape_level)
				self.body.scale(self.shape_level)
				self.rotate_update()

				# 图片变大，使得身体之间距离变小，为使视觉效果看起来不发生太大变化，需要相应调整节点绘制的参数
				self.draw_step_update()

		# 如果体型等级大于当前体型等级且大于最小体型等级，则减小体型
		elif self.shape_level > shape_level:
			if self.shape_level > self.min_shape_level:
				self.shape_level -= 1
				self.head.scale(self.shape_level)
				self.body.scale(self.shape_level)
				self.rotate_update()

				# 图片变小，使得身体之间距离变大，为使视觉效果看起来不发生太大变化，需要相应调整节点绘制的参数
				self.draw_step_update()

	# 重载坐标更新方法
	def pos_update(self):
		x, y         = self.map_pos
		self.map_pos = (x + self.vx, y + self.vy)

	# 重载死亡方法
	def die(self):
		if self.alive:
			self.alive = False

			# 死亡将留下额外食物
			postions      = []
			step          = self.draw_step * 2
			for i in xrange(self.draw_start, self.queue_num - 1, step):
				x, y = self.queue[i]
				x   -= self.body.half_w
				y   -= self.body.half_h
				postions.append((x, y))
			self.food.add_extra_food(self.lost_images[self.shape_level], postions)

			# 随后立即重生
			self.spawn()

	# 重载重生方法
	def spawn(self):
		super(Enemy, self).spawn()

		# 初始化状态保持量和状态更新方式
		self.state_keep       = 0
		self.state_update     = self.forage_update

		# 初始化寻找到敌人的坐标，寻找到的食物坐标
		self.find_enemy_pos   = None
		self.find_food_pos    = None

		# 初始化发现四周边界的信号
		self.find_left        = False
		self.find_right       = False
		self.find_up          = False
		self.find_down        = False

		# 速度初始化
		self.speed_update()