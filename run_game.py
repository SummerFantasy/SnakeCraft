# -*- coding:utf-8 -*-

""" 游戏引导模块 """



# 自带模块
import os
import sys



# 将lib和scene目录加入搜索路径
dir_name  = os.path.dirname(os.path.abspath(__file__))
lib_dir   = os.path.join(dir_name, 'lib')
scene_dir   = os.path.join(dir_name, 'scene')
sys.path.insert(0, scene_dir)
sys.path.insert(0, lib_dir)



# 加载游戏
import game

# 初始化游戏
game = game.Game()

# 运行游戏
game.run()