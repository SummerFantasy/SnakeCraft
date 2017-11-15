# -*- coding:utf-8 -*-

""" Record模块 """



import util



class Member(object):
	def __init__(self, font, target, screen_pos, color):
		self.font       = font
		self.target     = target
		self.screen_pos = screen_pos
		self.color      = color
		self.surface_update()

	def surface_update(self):
		self.content    = ' ' + str(self.target.length)
		self.surface    = self.font.render(self.content, True, self.color)

class Record(object):
	def __init__(self):
		self.font_height = 12
		self.font        = util.load_font('Haymaker.ttf', self.font_height)
		self.title_color = (0, 0, 0)
		self.title_pos   = (0, 63)
		self.title       = self.font.render((' WIN: 1500'), True, self.title_color)
		self.line_height = 15
		self.screen_pos  = (0, self.title_pos[1] + self.line_height)
		self.num         = 0
		self.queue       = []

	def add_member(self, target, color):
		x, y      = self.screen_pos
		y        += self.line_height * self.num
		member    = Member(self.font, target, (x, y), color)
		self.queue.append(member)
		self.num += 1

	def draw(self, screen):
		screen.blit(self.title, self.title_pos)
		for member in self.queue:
			screen.blit(member.surface, member.screen_pos)
	def update(self):
		for member in self.queue:
			member.surface_update()







