import pandas as pd
import numpy as np

from fastapi import FastAPI
import uvicorn

import tkinter as tk
import win32api
import win32con

import math
import _thread

from random import randint

# 服务器创建
app = FastAPI()

# 打开PDF
df = pd.read_csv('./../RawData/hygdata_v3.csv')
df.fillna(0, inplace=True)

# 初始化tk窗体
win_x = int(win32api.GetSystemMetrics(win32con.SM_CXSCREEN)/3)
win_y = int(win32api.GetSystemMetrics(win32con.SM_CYSCREEN))

win = tk.Tk()
win.overrideredirect(True)
win.geometry(str(win_x)+'x'+str(win_y)+'+0+0')
win.configure(bg='black')

# 创建画布
canvas = tk.Canvas(win, width=win_x, height=win_y, background='red')
canvas.pack()

star_radius_scale = 40
planet_radius_scale = 20
planet_orbit_scale = 5
universe_scale = 1
win_padding = 40
g_constant = 0.1


star_list = []
planet_list = []


class Star:
    def __init__(self, data):
        self.data = data

    def draw(self, canvas, center_coord):
        center_star_x = self.data['position']['x'] - center_coord['x']
        center_star_y = self.data['position']['y'] - center_coord['y']
        draw_circle(canvas, center_star_x, center_star_y,
                    self.data['radius']*star_radius_scale, universe_scale, 'white')


class Planet:
    def __init__(self, data, center_star):
        self.data = data
        self.center_star = center_star

    def draw(self, canvas, center_coord):
        center_star_x = self.center_star.data['position']['x'] - \
            center_coord['x']
        center_star_y = self.center_star.data['position']['y'] - \
            center_coord['y']
        planet_x = center_star_x + \
            math.sin(self.data['start_angle']) * \
            self.data['orbit_radius']*planet_orbit_scale
        planet_y = center_star_y - \
            math.cos(self.data['start_angle']) * \
            self.data['orbit_radius']*planet_orbit_scale
        draw_circle(canvas, planet_x, planet_y,
                    self.data['radius']*planet_radius_scale, universe_scale, 'white')


def draw_stars(star_return):
    global universe_scale
    global win_x, win_y
    # 绘制天体
    canvas.create_rectangle(0, 0, win_x, win_y, fill='black')
    # 遍历天体列表确定中心点坐标
    center_coord = {'x': 0, 'y': 0}
    _total_coord = {'x': 0, 'y': 0}
    for star in star_return['star_list']:
        _total_coord['x'] += star['position']['x']
        _total_coord['y'] += star['position']['y']
    center_coord['x'] = _total_coord['x']/len(star_return['star_list'])
    center_coord['y'] = _total_coord['y']/len(star_return['star_list'])
    # 计算缩放比例
    if len(star_return['star_list']) != 1:
        _max_dist_x = 0
        _max_dist_y = 0
        for i in range(len(star_return['star_list'])):
            c_star = star_return['star_list'][i]
            _delta_x = abs(c_star['position']['x']-center_coord['x'])
            _delta_y = abs(c_star['position']['y']-center_coord['y'])
            if _delta_x > _max_dist_x:
                _max_dist_x = _delta_x
            if _delta_y > _max_dist_y:
                _max_dist_y = _delta_y
        if ((win_x-win_padding*2)/(win_y-win_padding*2)) > (_max_dist_x/_max_dist_y):
            universe_scale = _max_dist_y*2/(win_y-win_padding*2)
        else:
            universe_scale = _max_dist_x*2/(win_x-win_padding*2)
    else:
        universe_scale = 1

    # 绘制天体
    star_list = []
    planet_list = []
    for star in star_return['star_list']:
        center_star = Star(star)
        star_list.append(center_star)
        for planet in star['planet']:
            planet_list.append(Planet(planet, center_star))

    for star_obj in star_list:
        star_obj.draw(canvas, center_coord)

    for planet_obj in planet_list:
        planet_obj.draw(canvas, center_coord)


# 画圆
def draw_circle(canvas, x, y, radius, scale, fill_color):
    draw_x = x/scale+win_x/2
    draw_y = y/scale+win_y/2
    canvas.create_oval(draw_x-radius, draw_y-radius, draw_x +
                       radius, draw_y+radius, fill=fill_color)


# 监听请求
@app.get("/getStars/{posx}/{posy}/{posz}/{dist}")
def get_stars(posx: float, posy: float, posz: float, dist: float):
    global df
    print('pos:\t', posx, posy, posz)
    df['distance'] = np.sqrt((df['x'] - posx) ** 2 +
                             (df['y'] - posy) ** 2 + (df['z'] - posz) ** 2)
    star_list = df[df['distance'] <= dist].values.tolist()

    while len(star_list) == 0:
        dist = dist + 0.1
        star_list = df[df['distance'] <= dist].values.tolist()

    star_return = {'star_list': [{
        'id': star[0],
        'distToSun': star[9],
        'abs_mag': star[14],
        'spect': star[15],
        'color_index': star[16],
        'position': {
            'x': star[17],
            'y': star[18],
            'z': star[19]
        },
        'radius': (20-float(star[14]))/20,
        'velocity': {
            'vx': star[20],
            'vy': star[21],
            'vz': star[22]
        },
        'planet': [{
            'orbit_radius': randint(100, 300)/1500,
            'start_angle': randint(0, 1000),
            'p_angle': randint(0, 1000),
            'radius': randint(150, 300)/1000
        } for i in range(0, randint(4, 6))]
    } for star in star_list]}

    # 打印输出
    for star in star_return['star_list']:
        print(' ')
        print('STAR')
        print('starId:\t'+str(star['id']))
        print('dist:\t'+str(star['distToSun']))
        print('absMag:\t'+str(star['abs_mag']))
        print('radius:\t'+str(star['radius']))
        for planet in star['planet']:
            print(' ')
            print('\tPLANET')
            print('\torbit_raiuds:\t'+str(planet['orbit_radius']))
            print('\tstart_angle:\t'+str(planet['start_angle']))
            print('\tp_angle:\t'+str(planet['p_angle']))
            print('\tradius:\t\t'+str(planet['radius']))

    print(' ')

    draw_stars(star_return)

    return star_return

# 线程


def run_server():
    # 加上这个就可以在运行main.py文件时，就运行uvicorn服务
    uvicorn.run(app=app, host="127.0.0.1", port=4999)


if __name__ == '__main__':
    _thread.start_new_thread(run_server, ())
    win.mainloop()

    while 1:
        pass
