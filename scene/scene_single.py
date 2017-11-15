# -*- coding:utf-8 -*-

""" 游戏单人模式场景模块 """



# 自带模块
import random

# 第三方模块
import pygame
from pygame.locals import (MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE)

# 自定义模块
import snake
import food
import map
import minimap
import record
import menu
import button
import util
import scene_start
from config import (SCREEN_SIZE, BLACK)



# 场景图片数据
images = {'minimap':      [('minimap.png',        BLACK), ('red_goal.png',       BLACK),
                           ('green_goal.png',     BLACK), ('blue_goal.png',      BLACK)], 
          'basefood':     [('food0.png',          BLACK), ('food1.png',          BLACK),
                           ('food2.png',          BLACK), ('food3.png',          BLACK)],
          'setting':      [('setting_0.png',      BLACK), ('setting_1.png',      BLACK)],
          'music':        [('music_00.png',       BLACK), ('music_01.png',       BLACK),
                           ('music_10.png',       BLACK), ('music_11.png',       BLACK)],
          'sound':        [('sound_00.png',       BLACK), ('sound_01.png',       BLACK),
                           ('sound_10.png',       BLACK), ('sound_11.png',       BLACK)],
          'back_to_game': [('back_to_game_0.png', BLACK), ('back_to_game_1.png', BLACK)],
          'back_to_menu': [('back_to_menu_0.png', BLACK), ('back_to_menu_1.png', BLACK)],
          'revive':       [('revive_0.png',       BLACK), ('revive_1.png',       BLACK)],
          'restart':      [('restart_0.png',      BLACK), ('restart_1.png',      BLACK)],}

# 场景音效数据
sound  = {'mouse_over': 'mouse_over.ogg', 'mouse_click': 'mouse_click.ogg',
          'collide': 'collide.ogg', 'win': 'win.ogg', 'lose': 'lose.ogg'}

# 场景背景音乐数据
music  = ['music_0.ogg', 'music_1.ogg', 'music_2.ogg', 'music_3.ogg', 'music_4.ogg']



class Scene_Single(object):
	def __init__(self, game):
		# 绑定game，加载场景图片、音效，随机加载背景音乐
		self.game         = game
		self.images       = util.batch_load_image(images)
		self.snake_images = util.get_snake_images()
		self.sound        = util.batch_load_sound(sound)
		self.music        = music
		util.load_music(random.choice(self.music))

		# 如果游戏音乐为开，则循环播放场景背景音乐
		if self.game.music:
			pygame.mixer.music.play(-1)

		# 如果游戏音效为关，则设置音效的音量为0.0
		if not self.game.sound:
			util.set_sound_off(self.sound)

		# 初始化场景各要素： 地图、小地图。食物、贪吃蛇
		self.map          = map.Map()
		self.minimap      = minimap.MiniMap(self.images['minimap'])
		self.record       = record.Record()
		self.food         = food.Food(self.images['basefood'], 50, self.map)
		self.snake        = snake.Snake(self.snake_images['red'], 6, self.food, self.map, self)
		self.enemy_0      = snake.Enemy(self.snake_images['green'], 6, self.food, self.map, self)
		self.enemy_1      = snake.Enemy(self.snake_images['blue'], 6, self.food, self.map, self)

		self.snake.set_enemy([self.enemy_0, self.enemy_1])
		self.enemy_0.set_enemy([self.snake, self.enemy_1])
		self.enemy_1.set_enemy([self.snake, self.enemy_0])

		# 设置地图和小地图的追踪目标
		self.map.set_target(self.snake)
		self.minimap.add_member(self.minimap.me_image, self.snake)
		self.minimap.add_member(self.minimap.enemy_image_0, self.enemy_0)
		self.minimap.add_member(self.minimap.enemy_image_1, self.enemy_1)
		self.record.add_member(self.snake, (200, 0, 0))
		self.record.add_member(self.enemy_0, (0, 200, 0))
		self.record.add_member(self.enemy_1, (0, 0, 220))

		# 菜单初始化并将场景菜单设置为选项菜单
		self.menu_init()
		self.menu         = self.setting_menu

		# 鼠标点击状态设置为0，将场景事件设置为game的监听事件
		self.click        = 0
		self.play         = True
		self.events       = {MOUSEBUTTONDOWN: self.set_click, KEYDOWN: self.key_action}
		self.game.set_event_listener(self.events)

		# 长度大于该值时获胜
		self.win_length   = 1500

	# 场景渲染
	def draw(self, screen):
		screen.fill(BLACK)
		self.map.draw(screen)
		self.food.draw(screen)
		self.snake.draw(screen)
		self.enemy_0.draw(screen)
		self.enemy_1.draw(screen)
		self.minimap.draw(screen)
		self.record.draw(screen)
		self.menu.draw(screen)

	# 场景更新
	def update(self):
		mouse_pos  = pygame.mouse.get_pos()
		self.menu.update(mouse_pos, self.click)

		if self.play:
			# 贪吃蛇更新时将同步更新食物和地图，因此不再单独更新
			self.snake.update(mouse_pos)
			self.enemy_0.update()
			self.enemy_1.update()
			self.minimap.update()
			self.record.update()

			# 贪吃蛇长度大于1000的将获胜
			if self.snake.length > self.win_length:
				self.set_win()
			elif self.enemy_0.length > self.win_length:
				self.set_lose()
			elif self.enemy_1.length > self.win_length:
				self.set_lose()

		# 鼠标点击状态重置为0
		self.click = 0

	def menu_init(self):
		# 创建选项菜单，设置各按钮事件
		self.setting_menu    = Setting_Menu(self.images, self.sound)
		self.setting_menu.setting.set_event(self.set_pause)

		# 创建暂停菜单，设置各按钮事件
		self.pause_menu      = Pause_Menu(self.images, self.sound, self.game)
		self.pause_menu.music.set_event(self.flip_music)
		self.pause_menu.sound.set_event(self.flip_sound)
		self.pause_menu.back_to_game.set_event(self.set_play)
		self.pause_menu.back_to_menu.set_event(self.set_scene_start)

		# 创建终结菜单，设置各按钮事件
		self.terminated_menu = Terminated_Menu(self.images, self.sound)
		self.terminated_menu.revive.set_event(self.set_revive)
		self.terminated_menu.back_to_menu.set_event(self.set_scene_start)

		# 创建胜利菜单，设置各按钮事件
		self.win_menu = Win_Menu(self.images, self.sound)
		self.win_menu.restart.set_event(self.set_scene_single)
		self.win_menu.back_to_menu.set_event(self.set_scene_start)

		# 创建失败菜单，设置各按钮事件
		self.lose_menu = Lose_Menu(self.images, self.sound)
		self.lose_menu.restart.set_event(self.set_scene_single)
		self.lose_menu.back_to_menu.set_event(self.set_scene_start)

	# 空白按钮事件
	def blank(self):
		pass

	# 设置场景鼠标点击状态(未点击: 0，左键: 1, 滚轮键: 2, 右键: 3，滚轮向前: 4, 滚轮向后: 5)
	def set_click(self, event):
		self.click = event.button

	# 键盘动作事件
	def key_action(self, event):
		# 按下ESC键，如果游戏处于运行状态则进入暂停状态，反之进入运行状态
		if event.key == K_ESCAPE:
			if self.play:
				self.set_pause()
			else:
				self.set_play()

	# 设置游戏暂停状态
	def set_pause(self):
		self.play  = False
		self.menu  = self.pause_menu

	# 设置游戏运行状态
	def set_play(self):
		self.play  = True
		self.menu  = self.setting_menu

	def set_terminated(self):
		self.play  = False
		self.menu  = self.terminated_menu

	def set_revive(self):
		self.play  = True
		self.menu  = self.setting_menu
		self.snake.spawn()

	def set_win(self):
		pygame.mixer.music.stop()
		self.sound['win'].play()
		self.play  = False
		self.menu  = self.win_menu

	def set_lose(self):
		pygame.mixer.music.stop()
		self.sound['lose'].play()
		self.play  = False
		self.menu  = self.lose_menu

	# 反转游戏音乐设置
	def flip_music(self):
		if self.game.music:
			pygame.mixer.music.stop()
		else:
			pygame.mixer.music.play(-1)
		self.game.music = not self.game.music
		self.pause_menu.music.exchange_images()

	# 反转游戏音效设置
	def flip_sound(self):
		if self.game.sound:
			util.set_sound_off(self.sound)
		else:
			util.set_sound_on(self.sound)
		self.game.sound = not self.game.sound
		self.pause_menu.sound.exchange_images()

	def set_scene_start(self):
		# 创建游戏开始场景并设置为game的场景
		scene = scene_start.Scene_Start(self.game)
		self.game.set_scene(scene)

	def set_scene_single(self):
		# 创建游戏单人模式场景并设置为game的场景
		scene = Scene_Single(self.game)
		self.game.set_scene(scene)



class Setting_Menu(menu.Menu):
	# 选项菜单，点击后游戏暂停，进入暂停菜单
	def __init__(self, images, sound):
		setting_images    = images['setting']
		setting_w         = setting_images[0].get_rect().width
		self.setting      = button.Go_Button(setting_images, (SCREEN_SIZE[0] - setting_w, 0), sound)
		self.buttons      = [self.setting,]



class Pause_Menu(menu.Menu):
	# 暂停菜单包括音乐开关，音效开关，回到游戏，回到开始菜单四个按钮
	def __init__(self, images, sound, game):
		self.pause_title  = util.load_image('pause_title.png', BLACK)
		self.music        = button.Set_Button(images['music'], (231, 215), sound, game.music)
		self.sound        = button.Set_Button(images['sound'], (231, 260), sound, game.sound)
		self.back_to_game = button.Go_Button(images['back_to_game'], (231, 305), sound)
		self.back_to_menu = button.Go_Button(images['back_to_menu'], (231, 350), sound)
		self.buttons      = [self.music, self.sound, self.back_to_game, self.back_to_menu]

	def draw(self, screen):
		# 渲染菜单标题
		screen.blit(self.pause_title, (221, 150))
		for button in self.buttons:
			button.draw(screen)



class Terminated_Menu(menu.Menu):
	# 终结菜单包括复活、回到开始菜单两个按钮
	def __init__(self, images, sound):
		self.terminated_titile  = util.load_image('terminate.png', BLACK)
		self.revive             = button.Go_Button(images['revive'], (231, 215), sound)
		self.back_to_menu       = button.Go_Button(images['back_to_menu'], (231, 260), sound)
		self.buttons            = [self.revive, self.back_to_menu]

	def draw(self, screen):
		# 渲染菜单标题
		screen.blit(self.terminated_titile, (121, 150))
		for button in self.buttons:
			button.draw(screen)



class Win_Menu(menu.Menu):
	# 终结菜单包括复活、回到开始菜单两个按钮
	def __init__(self, images, sound):
		self.win_titile         = util.load_image('you_win.png', BLACK)
		self.restart            = button.Go_Button(images['restart'], (231, 215), sound)
		self.back_to_menu       = button.Go_Button(images['back_to_menu'], (231, 260), sound)
		self.buttons            = [self.restart, self.back_to_menu]

	def draw(self, screen):
		# 渲染菜单标题
		screen.blit(self.win_titile, (121, 150))
		for button in self.buttons:
			button.draw(screen)



class Lose_Menu(menu.Menu):
	# 终结菜单包括复活、回到开始菜单两个按钮
	def __init__(self, images, sound):
		self.lose_titile         = util.load_image('you_lose.png', BLACK)
		self.restart            = button.Go_Button(images['restart'], (231, 215), sound)
		self.back_to_menu       = button.Go_Button(images['back_to_menu'], (231, 260), sound)
		self.buttons            = [self.restart, self.back_to_menu]

	def draw(self, screen):
		# 渲染菜单标题
		screen.blit(self.lose_titile, (121, 150))
		for button in self.buttons:
			button.draw(screen)