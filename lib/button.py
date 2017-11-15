# -*- coding:utf-8 -*-

""" Button模块 """



class Button(object):
	def __init__(self, images, pos, sound, event = None):
		self.images      = images
		self.sound       = sound
		self.pos         = pos
		self.rect        = images[0].get_rect(topleft = self.pos)
		self.active      = False
		self.event       = event

	def draw(self, screen):
		img = self.images[self.active]
		screen.blit(img, self.pos)

	def update(self, pos, click):
		# 如果鼠标停留在按钮上，设置按钮为激活态
		if self.mouse_over(pos):
			self.set_active()
			# 如果鼠标同时按下左键，播放点击音效，执行按钮内被设置的事件
			if click == 1:
				self.sound['mouse_click'].play()
				self.event()
		# 如果鼠标未停留在按钮上，设置按钮为未激活态
		else:
			self.set_inactive()

	def mouse_over(self, pos):
		over = self.rect.collidepoint(pos)
		return over

	def set_active(self):
		# 如果按钮已经处于激活态，则返回
		if self.active:
			return
		# 如果按钮处于未激活态，则变为激活态，播放激活音效
		else:
			self.active = True
			self.sound['mouse_over'].play()

	def set_inactive(self):
		# 如果按钮处于激活态，则变为未激活态
		if self.active:
			self.active = False
		# 如果按钮已经处于未激活态，则返回
		else:
			return

	def set_event(self, event):
		self.event = event

# 跳转按钮
class Go_Button(Button):
	def __init__(self, images, pos, sound, event = None):
		super(Go_Button, self).__init__(images, pos, sound, event)

# 设置按钮
class Set_Button(Button):
	def __init__(self, images, pos, sound, flag, event = None):
		super(Set_Button, self).__init__(images, pos, sound, event)

		# 按钮渲染默认为off的图像，如果flag为true，交换图像，即设置渲染为on的图像
		if flag:
			self.exchange_images()

	def exchange_images(self):
		img1, img2, img3, img4 = self.images
		self.images = [img3, img4, img1, img2]