#-*-coding:utf-8-*-
import numpy as np
import cv2 as cv
import PIL.Image as PI
from PyQt5 import QtCore

def display_image_on_label(image, label):
	height, width = image.shape[:2]
	max_edge_scale = min(label.width() / width, label.height() / height)
	height_scale, width_scale = height * max_edge_scale, width * max_edge_scale
	img = cv.resize(image, (int(width_scale), int(height_scale)))
	# img = image_pad(img, 540, 760)
	img = img[..., ::-1]
	img = PI.fromarray(img)
	img = img.toqpixmap()
	# img = img.scaled(width_scale, height_scale)
	
	label.setPixmap(img)
	label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
	return img

def image_pad(img, h_dim, w_dim):
	h, w = img.shape[:2]
	top_pad = (h_dim - h) // 2
	bottom_pad = h_dim - h - top_pad
	left_pad = (w_dim - w) // 2
	right_pad = w_dim - w - left_pad
	padding = [(top_pad, bottom_pad), (left_pad, right_pad), (0, 0)]
	img = np.pad(img, padding, mode='constant', constant_values=255)
	return img

# def cv_draw_polygon(img):
# 	cv.imshow("img", img)
# 	polys = []
# 	poly_points = []
#
# 	def draw_poly(event, x, y, flags, param):
# 		global ix, iy, rect, close_flag
#
# 		if event == cv.EVENT_LBUTTONDOWN:
# 			cv.circle(img, (x, y), 5, (0, 0, 255), 4)
# 			if len(poly_points) != 0:
# 				cv.line(img, poly_points[-1], (x, y), (0, 255, 0), 2)
# 			if len(poly_points) != 0 and -5 < x - poly_points[0][0] < 5 and -5 < y - poly_points[0][1] < 5:
# 				poly_points.append(poly_points[0])
# 				polys.append(poly_points.copy())
# 				poly_points.clear()
# 				print(polys)
# 			else:
# 				poly_points.append((x, y))
#
# 		elif event == cv.EVENT_MOUSEMOVE:
# 			if len(poly_points) != 0:
# 				img1 = img.copy()
# 				if -5 < x-poly_points[0][0] < 5 and -5 < y-poly_points[0][1] < 5:
# 					cv.circle(img1, poly_points[0], 10, (0, 255, 0), 8)
# 				cv.line(img1, poly_points[-1], (x, y), (0, 0, 0), 2)
# 				cv.imshow("img", img1)
#
# 	cv.setMouseCallback("img", draw_poly)
# 	return poly_points
