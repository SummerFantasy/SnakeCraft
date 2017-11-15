# -*- coding:utf-8 -*-

""" 游戏开始场景模块 """



# 自带模块
import sys
import random

# 第三方模块
import pygame
from pygame.locals import MOUSEBUTTONDOWN

# 自定义模块
import menu
import button
import scene_single
import util
from config import BLACK



# 场景图片数据
images = {'single':       [('single_0.png',       BLACK), ('single_1.png',       BLACK)],
          'online':       [('online_0.png',       BLACK), ('online_1.png',       BLACK)],
		  'option':       [('option_0.png',       BLACK), ('option_1.png',       BLACK)],
          'end':          [('end_0.png',          BLACK), ('end_1.png',          BLACK)],
          'music':        [('music_00.png',       BLACK), ('music_01.png',       BLACK),
                           ('music_10.png',       BLACK), ('music_11.png',       BLACK)],
          'sound':        [('sound_00.png',       BLACK), ('sound_01.png',       BLACK),
                           ('sound_10.png',       BLACK), ('sound_11.png',       BLACK)],
          'back_to_menu': [('back_to_menu_0.png', BLACK), ('back_to_menu_1.png', BLACK)],}

# 场景音效数据
sound  = {'mouse_over': 'mouse_over.ogg', 'mouse_click': 'mouse_click.ogg',}

# 场景背景音乐数据
music  = ['music_0.ogg', 'music_1.ogg', 'music_2.ogg', 'music_3.ogg', 'music_4.ogg']



class Scene_Start(object):
	def __init__(self, game):
		# 绑定game，加载场景图片、音效，随机加载背景音乐
		self.game        = game
		self.images      = util.batch_load_image(images)
		self.sound       = util.batch_load_sound(sound)
		self.music       = music
		util.load_music(random.choice(self.music))

		# 如果游戏音乐为开，则循环播放场景背景音乐
		if self.game.music:
			pygame.mixer.music.play(-1)

		# 如果游戏音效为关，则设置音效的音量为0.0
		if not self.game.sound:
			util.set_sound_off(self.sound)

		# 加载场景背景图，菜单初始化并将场景菜单设置为开始菜单
		self.bg          = util.load_image('start_bg.png')
		self.bg_pos      = (0, 0)
		self.menu_init()
		self.set_start_menu()

		# 鼠标点击状态设置为0，将场景事件设置为game的监听事件
		self.click       = 0
		self.events      = {MOUSEBUTTONDOWN: self.set_click}
		self.game.set_event_listener(self.events)

	# 场景渲染
	def draw(self, screen):
		screen.blit(self.bg, self.bg_pos)
		self.menu.draw(screen)

	# 场景更新
	def update(self):
		mouse_pos   = pygame.mouse.get_pos()
		self.menu.update(mouse_pos, self.click)

		# 鼠标点击状态重置为0
		self.click  = 0

	def menu_init(self):
		# 创建开始菜单，设置各按钮事件
		self.start_menu  = Start_Menu(self.images, self.sound)
		self.start_menu.single.set_event(self.set_scene_single)
		self.start_menu.online.set_event(self.set_unfinished)
		self.start_menu.option.set_event(self.set_option_menu)
		self.start_menu.end.set_event(self.set_game_end)

		# 创建选项菜单，设置各按钮事件
		self.option_menu = Option_Menu(self.images, self.sound, self.game)
		self.option_menu.music.set_event(self.flip_music)
		self.option_menu.sound.set_event(self.flip_sound)
		self.option_menu.back_to_menu.set_event(self.set_start_menu)

		# 创建未完成菜单，设置按钮事件
		self.unfinished_menu = Unfinished_Menu(self.images, self.sound)
		self.unfinished_menu.back_to_menu.set_event(self.set_start_menu)

	# 空白按钮事件
	def blank(self):
		pass

	# 设置场景鼠标点击状态(未点击: 0，左键: 1, 滚轮键: 2, 右键: 3，滚轮向前: 4, 滚轮向后: 5)
	def set_click(self, event):
		self.click = event.button

	# 设置场景菜单为开始菜单
	def set_start_menu(self):
		self.menu  = self.start_menu

	# 设置场景菜单为选项菜单
	def set_option_menu(self):
		self.menu  = self.option_menu

	# 设置场景菜单为未完成菜单
	def set_unfinished(self):
		self.menu  = self.unfinished_menu

	# 设置游戏循环结束
	def set_game_end(self):
		self.game.loop = False

	# 反转游戏音乐设置
	def flip_music(self):
		if self.game.music:
			pygame.mixer.music.stop()
		else:
			pygame.mixer.music.play(-1)
		self.game.music = not self.game.music
		self.option_menu.music.exchange_images()

	# 反转游戏音效设置
	def flip_sound(self):
		if self.game.sound:
			util.set_sound_off(self.sound)
		else:
			util.set_sound_on(self.sound)
		self.game.sound = not self.game.sound
		self.option_menu.sound.exchange_images()

	def set_scene_single(self):
		# 创建单人模式场景并设置为game的场景
		scene = scene_single.Scene_Single(self.game)
		self.game.set_scene(scene)



class Start_Menu(menu.Menu):
	# 开始菜单包括单人，联机，选项菜单，结束四个按钮
	def __init__(self, images, sound):
		self.single       = button.Go_Button(images['single'], (281, 365), sound)
		self.online       = button.Go_Button(images['online'], (281, 410), sound)
		self.option       = button.Go_Button(images['option'], (281, 455), sound)
		self.end          = button.Button(images['end'], (281, 500), sound)
		self.buttons      = [self.single, self.online, self.option, self.end]



class Option_Menu(menu.Menu):
	# 选项菜单包括音乐开关，音效开关，回到开始菜单三个按钮
	def __init__(self, images, sound, game):
		self.music        = button.Set_Button(images['music'], (231, 365), sound, game.music)
		self.sound        = button.Set_Button(images['sound'], (231, 410), sound, game.sound)
		self.back_to_menu = button.Go_Button(images['back_to_menu'], (231, 455), sound)
		self.buttons      = [self.music, self.sound, self.back_to_menu]



class Unfinished_Menu(menu.Menu):
	# 未完成菜单，用于表示联机功能未完成，含有回到开始菜单按钮
	def __init__(self, images, sound):
		self.unfinished_titile  = util.load_image('unfinished.png', BLACK)
		self.back_to_menu       = button.Go_Button(images['back_to_menu'], (231, 410), sound)
		self.buttons            = [self.back_to_menu,]

	def draw(self, screen):
		# 渲染菜单标题
		screen.blit(self.unfinished_titile, (231, 365))
		for button in self.buttons:
			button.draw(screen)