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
win_x = int(win32api.GetSystemMetrics(win32con.SM_CXSCREEN)/4)
win_y = int(win32api.GetSystemMetrics(win32con.SM_CYSCREEN))

win = tk.Tk()
win.overrideredirect(True)
win.geometry(str(win_x)+'x'+str(win_y)+'+0+0')
win.configure(bg='black')

# 创建画布
canvas = tk.Canvas(win, width=win_x, height=win_y, background='red')
canvas.pack()


def draw_stars(star_return):
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
    padding = 40
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
        if ((win_x-padding*2)/(win_y-padding*2)) > (_max_dist_x/_max_dist_y):
            universe_scale = _max_dist_y*2/(win_y-padding*2)
        else:
            universe_scale = _max_dist_x*2/(win_x-padding*2)
    else:
        universe_scale = 1
    # 绘制天体
    print(universe_scale)
    radius_scale = 80
    for star in star_return['star_list']:
        x = (star['position']['x'] - center_coord['x']) / \
            universe_scale + win_x/2
        y = (star['position']['y'] - center_coord['y']) / \
            universe_scale + win_y/2
        canvas.create_oval(
            x-star['radius']*radius_scale/2,
            y-star['radius']*radius_scale/2,
            x+star['radius']*radius_scale/2,
            y+star['radius']*radius_scale/2,
            fill='white')

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
