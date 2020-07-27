#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 14:43:49 2018

@author: lab407
"""

'''
Watershed segmentation
=========
This program demonstrates the watershed segmentation algorithm
in OpenCV: watershed().
Usage
-----
watershed.py [image filename]
Keys
----
  1-7   - switch marker color
  SPACE - update segmentation
  r     - reset
  a     - toggle autoupdate
  ESC   - exit
'''



import numpy as np
import cv2 as cv
from common import Sketcher

class App:
    def __init__(self, fn):
        #self.img = cv.imread(fn)
        self.img = fn
        if self.img is None:
            raise Exception('Failed to load image file: %s' % fn)

        h, w = self.img.shape[:2]
        self.markers = np.zeros((h, w), np.int32)
        self.markers_vis = self.img.copy()
        self.cur_marker = 1
        self.colors = np.int32( list(np.ndindex(2, 2, 2)) ) * 255

        self.thresh_value = 50
        self.thresh_max = None

        self.auto_update = True
        self.preprocess(0)
        self.sketch = Sketcher('img', [self.markers_vis, self.markers], self.get_colors)

        self.boundary_points = []

    def change_thresh(self):
        self.thresh_value += 10
        if self.thresh_value > self.thresh_max:
            self.thresh_value = 10

    # 经过一系列图像处理得到一些前景和背景信息
    def preprocess(self, flag=0):
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        # cv.imshow("gray", gray)

        # ret:返回的阈值, thresh:返回的二值化图像
        if flag == 0:
            ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
            self.thresh_max = ret
        else:
            ret, thresh = cv.threshold(gray, self.thresh_value, 255, cv.THRESH_BINARY)
        # print("ret:", ret)
        # cv.imshow("thresh", thresh)

        # noise removal
        kernel = np.ones((3, 3), np.uint8)
        opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=2)
        # cv.imshow("opening", opening)

        # sure background area
        sure_bg = cv.dilate(opening, kernel, iterations=30)
        # cv.imshow("sure_bg", sure_bg)

        # Finding sure foreground area
        # distanceTransform用于计算每个非零像素距离与其最近的零点像素之间的距离，
        # 输出的是保存每一个非零点与最近零点的距离信息
        dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
        normalized_img = np.zeros(dist_transform.shape)
        normalized_img = cv.normalize(dist_transform, normalized_img, 0, 255, cv.NORM_MINMAX)
        normalized_img = np.uint8(normalized_img)
        # cv.imshow("normalize_img", normalized_img)
        # self.write_matrix_to_file(normalized_img)
        ret, sure_fg = cv.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        # cv.imshow("sure_fg", sure_fg)

        # Finding unknown region
        # unknown = cv.subtract(sure_bg, sure_fg)

        # Marker labelling
        # ret：一共有多少个区域,前景数+1(背景)
        # markers：为区域编号的矩阵,背景为0,前景依次为1,2,3
        ret, markers = cv.connectedComponents(sure_fg)

        # 前景标记为1，背景标记为2
        self.markers[markers[:, :] == 1] = 1
        self.markers[sure_bg[:, :] == 0] = 2
        # self.write_matrix_to_file(self.markers)

        overlay = self.colors[np.maximum(self.markers, 0)]
        alpha = np.zeros(overlay.shape)
        for a in range(3):
            # 这里im2[:,:,a]!=0生成一个bool型矩阵掩码
            alpha[overlay[:, :, a] != 0] = 0.5
        # self.markers_vis = cv.addWeighted(self.markers_vis, 0.5, overlay, 0.5, 0.0, dtype=cv.CV_8UC3)
        self.markers_vis[:] = overlay * alpha + self.markers_vis * (1 - alpha)
        self.markers_vis[:] = np.uint8(self.markers_vis)

    def reset(self):
        self.markers[:] = 0
        self.markers_vis[:] = self.img

    def get_colors(self):
        return list(map(int, self.colors[self.cur_marker])), self.cur_marker

    def watershed(self):
        m = self.markers.copy() # m.shape = (h, w)
        self.write_matrix_to_file(m)
        cv.watershed(self.img, m)
        overlay = self.colors[np.maximum(m, 0)]
        self.vis = cv.addWeighted(self.img, 0.5, overlay, 0.5, 0.0, dtype=cv.CV_8UC3)
        # cv.imshow('watershed', self.vis)

        ol = overlay.astype(np.uint8)
        mask_bool = ol[:, :, 2] == 255
        nonb = mask_bool.nonzero()
        all_points_y = nonb[0].tolist()
        all_points_x = nonb[1].tolist()
        self.boundary_points.clear()
        self.boundary_points.append(all_points_x)
        self.boundary_points.append(all_points_y)
        
    def start(self):
        self.watershed()
        return self.vis, self.boundary_points

    def run(self):
        self.watershed()
        while cv.getWindowProperty('img', 0) != -1 or cv.getWindowProperty('watershed', 0) != -1:
            ch = cv.waitKey(50)
            if ch == 27:
                break
            if ch >= ord('1') and ch <= ord('7'):
                self.cur_marker = ch - ord('0')
                print('marker: ', self.cur_marker)
            if self.sketch.dirty and self.auto_update:
                self.watershed()
                self.sketch.dirty = False
            if ch in [ord('a'), ord('A')]:
                self.auto_update = not self.auto_update
                print('auto_update if', ['off', 'on'][self.auto_update])
            if ch in [ord('r'), ord('R')]:
                self.markers[:] = 0
                self.markers_vis[:] = self.img
                self.sketch.show()
            if ch in [ord('q'), ord('Q'), ord(' ')]:
                # 清空标记和掩码
                self.reset()
                self.change_thresh()
                self.preprocess(1)
                self.watershed()
                # 显示带有先验的图片
                self.sketch.show()
        cv.destroyAllWindows()
        return self.vis

    def write_matrix_to_file(self, matrix):
        h, w = matrix.shape
        name = "haha.txt"
        f = open(name, "w")
        for i in range(h):
            for j in range(w):
                f.write(str(int(matrix[i][j])))
            f.write("\n")
        f.close()

if __name__ == '__main__':
    import sys
    try:
        fn = sys.argv[1]
    except:
        fn = 'insulator_00395.jpg'
    App(fn).run()
