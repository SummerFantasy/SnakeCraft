# -*- coding:utf-8 -*-

""" 工具函数模块 """



# 自带模块
import os

# 第三方模块
import pygame
from pygame.locals import RLEACCEL



# 加载图片
def load_image(name, colorkey = None):
	fullname = os.path.join('data', 'image', name)
	image    = pygame.image.load(fullname).convert()
	if colorkey:
		image.set_colorkey(colorkey, RLEACCEL)
	return image

# 批量加载图片
def batch_load_image(image_data):
	surface_data = {}
	for name, images in image_data.items():
		i = []
		for image in images:
			image_name, colorkey = image
			image_surface = load_image(image_name, colorkey)
			i.append(image_surface)
		surface_data[name] = i
	return surface_data

# 加载声音
def load_sound(name):
	fullname = os.path.join('data', 'sound', name)
	sound    = pygame.mixer.Sound(fullname)
	return sound

# 批量加载声音
def batch_load_sound(sound_data):
	sound = {}
	for name, sound_name in sound_data.items():
		sound[name] = load_sound(sound_name)
	return sound

# 设置声音的音量为0
def set_sound_off(sounds):
	for sound in sounds.values():
		sound.set_volume(0.0)

# 设置声音的音量为1
def set_sound_on(sounds):
	for sound in sounds.values():
		sound.set_volume(1.0)

# 加载音乐
def load_music(name):
	fullname = os.path.join('data', 'music', name)
	pygame.mixer.music.load(fullname)

# 加载字体
def load_font(name, size):
	fullname = os.path.join('data', 'font', name)
	font     = pygame.font.Font(fullname, size)
	return font

# 贪吃蛇图片生成
def get_snake_images():
	colors = ['red', 'green', 'blue']
	parts  = ['head', 'body', 'lost']
	num    = 10

	snake_images = {}
	for color in colors:
		images = []
		for part in parts:
			part_images = []
			for i in xrange(num):
				name  = color + '_' + part + '_' + str(i) + '.png'
				image = load_image(name, (0, 0, 0))
				part_images.append(image)
			images.append(part_images)
		snake_images[color] = images

	return snake_images

# 模块测试函数
def test():
	"test function"
	pass

if __name__ == '__main__':
	test()