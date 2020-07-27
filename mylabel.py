#-*-coding:utf-8-*-

# 第三方库
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import QRect, Qt, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QGuiApplication
import numpy as np
import cv2 as cv

# 自建库
from util import display_image_on_label

class MyLabel(QLabel):
	temp_pix = QPixmap()
	last_point = QPoint()
	end_point = QPoint()
	pix_map = None
	poly_points = []
	
	press_flag = False
	move_flag = False
	final_flag = False
	close_flag = False
	
	def set_parameters(self, pix_map, radio_rect, radio_poly, cur_img_ann, boundary_points=None):
		self.pix_map = pix_map
		self.radio_rect = radio_rect
		self.radio_poly = radio_poly
		self.cur_img_ann = cur_img_ann
		self.setMouseTracking(True) # 鼠标没有按下也能捕获鼠标移动

		self.boundary_points = boundary_points
	
	# 删除除了原图以外的绘图
	def refresh(self):
		self.temp_pix = None
		self.pix_map = None
		self.last_point = QPoint()
		self.end_point= QPoint()
		self.update()
	
	# 鼠标点击事件
	def mousePressEvent(self, event):
		"""
		按下鼠标左键后，将当前位置存储到起点中。
		"""
		if self.radio_rect.isChecked():
			if event.button() == Qt.LeftButton and self.pix_map!=None:
				self.last_point = event.pos()
		elif self.radio_poly.isChecked():
			if event.button() == Qt.LeftButton and self.pix_map!=None:
				if len(self.poly_points) != 0:
					self.pix_map = self.temp_pix.copy()
				point = event.pos()
				if len(self.poly_points) != 0 and \
					-5 < point.x() - self.poly_points[0].x() < 5 and \
					-5 < point.y() - self.poly_points[0].y() < 5:
					self.close_flag = True
				self.poly_points.append(point)
				# print(point)
				self.press_flag = True
				if self.close_flag:
					print("标注已闭合！")
					all_points_x = []
					all_points_y = []
					for point in self.poly_points:
						all_points_x.append(point.x())
						all_points_y.append(point.y())
					self.boundary_points.append(all_points_x)
					self.boundary_points.append(all_points_y)

				self.update()
			if event.button() == Qt.RightButton:
				self.poly_points.clear()
		
	# 鼠标释放事件
	def mouseReleaseEvent(self, event):
		"""
		松开鼠标左键后，将当前位置存储到终点中；绘制图案，并将缓存中的内容更新到self.pix_map中。
		"""
		if self.radio_rect.isChecked():
			self.end_point = event.pos()
			self.update()
			self.pix_map = self.temp_pix.copy()
		elif self.radio_poly.isChecked():
			self.pix_map = self.temp_pix.copy()
		
	# 鼠标移动事件
	def mouseMoveEvent(self, event):
		"""
		鼠标左键被按下且在滑动中，调用绘图函数，更新画布内容。
		"""
		if self.radio_rect.isChecked():
			if event.buttons() and Qt.LeftButton and self.pix_map!=None:  # 这里的写法非常重要
				self.end_point = event.pos()
				self.update()
		elif self.radio_poly.isChecked():
			if len(self.poly_points) != 0:
				self.end_point = event.pos()
				self.move_flag = True
				if -5 < self.end_point.x()-self.poly_points[0].x() < 5 and -5 < self.end_point.y()-self.poly_points[0].y() < 5:
					self.final_flag = True
				
				self.update()
				
	# 绘制事件
	def paintEvent(self, event):
		"""
		使用两个QPainter是为了解决：每次paintEvent之前的框消失（双缓冲绘图）
		使用self.temp_pix是为了解决：画框过长中的重影
		"""
		super().paintEvent(event)
		if self.pix_map != None:
			if self.radio_rect.isChecked():
				x = self.last_point.x()
				y = self.last_point.y()
				w = self.end_point.x() - x
				h = self.end_point.y() - y

				# 这段代码每次画框，之前的就消失了
				# rect = QRect(x, y, w, h)
				# painter = QPainter(self)
				# painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
				# painter.drawRect(rect)
			
				# 双缓冲绘图
				self.temp_pix = self.pix_map.copy()  # 如果直接赋值，两者的内存是相同的，因此这里需要调用copy。
				pp = QPainter(self.temp_pix)
				pp.setPen(QPen(Qt.red, 2, Qt.SolidLine))
				pp.drawRect(x, y, w, h)
				painter = QPainter(self)
				painter.drawPixmap(0, 0, self.temp_pix)
				
			elif self.radio_poly.isChecked():
				# 双缓冲绘图
				self.temp_pix = self.pix_map.copy()  # 如果直接赋值，两者的内存是相同的，因此这里需要调用copy。
				pp = QPainter(self.temp_pix)
				if len(self.poly_points) != 0:
					if self.press_flag:
						self.press_flag = False
						pp.setPen(QPen(Qt.red, 6, Qt.SolidLine))
						pp.drawPoint(self.poly_points[-1])
						if self.close_flag:
							self.close_flag = False
							self.cur_img_ann = self.poly_points.copy()
							self.poly_points.clear()
					elif self.move_flag:
						self.move_flag = False
						pp.setPen(QPen(Qt.green, 2, Qt.SolidLine))
						pp.drawLine(self.poly_points[-1], self.end_point)
						if self.final_flag:
							self.final_flag = False
							pp.setPen(QPen(Qt.green, 15, Qt.SolidLine))
							pp.drawPoint(self.poly_points[0])
							
					painter = QPainter(self)
					painter.drawPixmap(0, 0, self.temp_pix)

class SemiLabel(QLabel):

	pix_map = None
	fore_points = []
	back_points = []
	prev_pt = None
	
	press_flag = False
	move_flag = False
	
	def set_parameters(self, img, pix_map, label_mask_auto, label_curmarker=None, mask=None):
		self.img = img
		self.pix_map = pix_map
		self.label_mask_auto = label_mask_auto
		self.label_curmarker = label_curmarker
		self.mask = mask
		
		h, w = self.img.shape[:2]
		self.markers = np.zeros((h, w), np.int32)
		self.markers_vis = self.img.copy()
		self.cur_marker = 1
		self.colors = np.int32(list(np.ndindex(2, 2, 2))) * 255
		
	# 删除除了原图以外的绘图
	def refresh(self):
		self.temp_pix = None
		self.pix_map = None
		self.last_point = QPoint()
		self.end_point = QPoint()
		self.update()
		
	def get_colors(self):
		return list(map(int, self.colors[self.cur_marker])), self.cur_marker
	
	# 鼠标点击事件
	def mousePressEvent(self, event):
		"""
		按下鼠标左键后，将当前位置存储到起点中。
		"""
		if event.button() == Qt.LeftButton:
			point = event.pos()
			self.prev_pt = point
			self.press_flag = True
			# self.fore_seg()
			self.update()

	# 鼠标释放事件
	def mouseReleaseEvent(self, event):
		"""
		松开鼠标左键后，将当前位置存储到终点中；绘制图案，并将缓存中的内容更新到self.pix_map中。
		"""
		self.prev_pt = None
	
	# 鼠标移动事件
	def mouseMoveEvent(self, event):
		"""
		鼠标左键被按下且在滑动中，调用绘图函数，更新画布内容。
		"""
		if event.buttons() and Qt.LeftButton:
			self.cur_pt = event.pos()
			self.move_flag = True
			self.update()
	
	# 绘制事件
	def paintEvent(self, event):
		"""
		使用两个QPainter是为了解决：每次paintEvent之前的框消失（双缓冲绘图）
		使用self.temp_pix是为了解决：画框过长中的重影
		"""
		super().paintEvent(event)
		
		if self.pix_map:
			self.temp_pix = self.pix_map.copy()
			pp = QPainter(self.temp_pix)
			
			# 处理鼠标按下操作
			if self.press_flag:
				self.press_flag = False
				self.cur_marker = int(self.label_curmarker.text()[-1])
				if self.cur_marker == 1:
					pp.setPen(QPen(Qt.red, 6, Qt.SolidLine))
				elif self.cur_marker == 2:
					pp.setPen(QPen(Qt.green, 6, Qt.SolidLine))
				pp.drawPoint(self.prev_pt)
				
				# 分割标记
				prev_pt = (self.prev_pt.x(), self.prev_pt.y())
				cv.circle(self.markers, prev_pt, 1, self.cur_marker, 2)
				self.write_matrix_to_file(self.markers)
				self.fore_seg()
			
			# 处理鼠标移动操作
			if self.move_flag:
				self.move_flag = False
				self.cur_marker = int(self.label_curmarker.text()[-1])
				if self.cur_marker == 1:
					pp.setPen(QPen(Qt.red, 6, Qt.SolidLine))
				elif self.cur_marker == 2:
					pp.setPen(QPen(Qt.green, 6, Qt.SolidLine))
				try:
					pp.drawLine(self.prev_pt, self.cur_pt)
					
					# 分割标记
					prev_pt = (self.prev_pt.x(), self.prev_pt.y())
					cur_pt = (self.cur_pt.x(), self.cur_pt.y())
					cv.line(self.markers, prev_pt, cur_pt, self.cur_marker, 5)
					# self.write_matrix_to_file(self.markers)
					self.prev_pt = self.cur_pt
				except:
					print("self.prev_pt, self.cur_pt Error")
				
				self.fore_seg()
			painter = QPainter(self)
			painter.drawPixmap(0, 0, self.temp_pix)
			self.pix_map = self.temp_pix.copy()
	
	def write_matrix_to_file(self, matrix):
		h, w = matrix.shape
		name = "haha.txt"
		f = open(name, "w")
		for i in range(h):
			for j in range(w):
				f.write(str(int(matrix[i][j])))
			f.write("\n")
		f.close()

	def fore_seg(self):
		"""
		前景分割：主要调用分水岭算法
		"""
		m = self.markers.copy()
		cv.watershed(self.img, m)
		overlay = self.colors[np.maximum(m, 0)]
		vis = cv.addWeighted(self.img, 0.5, overlay, 0.5, 0.0, dtype=cv.CV_8UC3)
		display_image_on_label(vis, self.label_mask_auto)
		ol = overlay.astype(np.uint8)
		mask_bool = ol[:, :, 2] == 255
		nonb = mask_bool.nonzero()
		all_points_y = nonb[0].tolist()
		all_points_x = nonb[1].tolist()
		self.mask.clear()
		self.mask.append(all_points_x)
		self.mask.append(all_points_y)
	