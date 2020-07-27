#-*-coding:utf-8-*-

# 标准库
import os
import sys
import random
import json_lib
import time
import threading
import warnings
warnings.filterwarnings("ignore")

# 三方库
import PyQt5
from PyQt5.Qt import QStandardItemModel, QStandardItem, QTreeWidgetItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon, QPainter, QPen, QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, QPoint, QRect
from PyQt5 import QtGui, QtCore, QtWidgets
import PIL.Image as PI
import PIL.ImageDraw as PID
import numpy as np
import skimage.io
import cv2 as cv

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# 自建库
import main_ui
import watershed
from util import image_pad, display_image_on_label

class MainCode(QMainWindow, main_ui.Ui_MainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		main_ui.Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.initUI()

	def initUI(self):
		self.setWindowTitle("标注工具")
		from mylabel import MyLabel, SemiLabel
		
		# 将响应函数绑定在按钮上
		self.btn_open.clicked.connect(self.on_open_dir)
		self.btn_next.clicked.connect(self.on_next_image)
		self.btn_pre.clicked.connect(self.on_pre_image)
		self.btn_save.clicked.connect(self.on_save)
		
		# 目录树
		self.model = QStandardItemModel(0, 1, self)
		self.model.setHeaderData(0, Qt.Horizontal, "文件路径")
		self.treeView.setModel(self.model)
		self.treeView.clicked.connect(self.tree_clicked)
		
		# 全手动
		self.lb = MyLabel(self.tab_manu)
		self.lb.setGeometry(QRect(10, 10, 760, 540))
		self.radio_poly.setChecked(True)
		self.button_group = QtWidgets.QButtonGroup(self)
		self.button_group.addButton(self.radio_rect)
		self.button_group.addButton(self.radio_poly)

		# 半自动
		self.mylabel_rgb_semi = SemiLabel(self.tab_semi)
		self.mylabel_rgb_semi.setGeometry(QRect(30, 150, 320, 240))
		self.label_rgb_semi.setText("")
		self.label_mask_semi.setText("")
		self.label_curmarker_semi.setText("current_marker: " + "1")
		
		# 全自动
		self.label_rgbtfusion_auto.setText("")
		self.label_registered_auto.setText("")
		self.label_mask_auto.setText("")
		self.mylabel_registered_auto = SemiLabel(self.tab_auto)
		self.mylabel_registered_auto.setGeometry(QRect(40, 290, 320, 240))
		self.label_curmarker_auto.setText("current_marker: " + "1")
		self.boundary_points = []
		
		# self.radio_semi_auto.setChecked(True)
		# self.group_auto = QtWidgets.QButtonGroup(self)
		# self.group_auto.addButton(self.radio_semi_auto)
		# self.group_auto.addButton(self.radio_auto_auto)
	
		self.cur_img_ann = {}
		self.show()

	def on_open_dir(self):
		data_dir = QFileDialog.getExistingDirectory(self, "选取文件夹", "./")
		self.data_dir = data_dir

		test_data = os.listdir(data_dir)
		test_data.sort()
		self.test_data = test_data
		self.num_data = len(test_data)
		self.image_ids = list(range(self.num_data))
		self.image_id = 0
		self.label_img_info.setText("image_id: {}\nname: {}".format(self.image_id, self.test_data[self.image_id]))
		
		# 目录树显示
		path_data_name = self.model.invisibleRootItem()
		for i in range(len(test_data)):
			gos_data = QStandardItem(test_data[i])
			path_data_name.setChild(i, gos_data)
		
	def on_next_image(self):
		if self.image_id == self.num_data - 1:
			self.image_id = 0
		else:
			self.image_id += 1
		self.label_img_info.setText("image_id: {}\nname: {}".format(self.image_id, self.test_data[self.image_id]))
		
	def on_pre_image(self):
		if self.image_id == 0:
			self.image_id = self.num_data - 1
		else:
			self.image_id -= 1
		self.label_img_info.setText("image_id: {}\nname: {}".format(self.image_id, self.test_data[self.image_id]))
		
	def tree_clicked(self):
		index = self.treeView.currentIndex()
		self.image_id = index.row()
		self.label_img_info.setText("image_id: {}\nname: {}".format(self.image_id, self.test_data[self.image_id]))
		if self.tabWidget.currentIndex() == 0: # 全手动处理
			self.show_image_manu()
		elif self.tabWidget.currentIndex() == 1: # 半自动处理
			self.show_image_semi()
		elif self.tabWidget.currentIndex() == 2: # 全自动处理
			self.show_image_auto()
			
	# 全手动标注的处理函数
	def show_image_manu(self):
		self.lb.refresh()
		rgb_path = os.path.join(self.data_dir, self.test_data[self.image_id])
		rgb_image = cv.imread(rgb_path)
		# height, width = img.shape[:2]
		# max_edge_scale = min(self.lb.width() / width, self.lb.height() / height)
		# height_scale, width_scale = height * max_edge_scale, width * max_edge_scale
		# img = cv.resize(img, (int(width_scale), int(height_scale)))
		# img = image_pad(img, 540, 760)
		# img = img[..., ::-1]
		# img = PI.fromarray(img)
		# img = img.toqpixmap()
		#
		# self.lb.setPixmap(img)
		# self.lb.set_parameters(img, self.radio_rect, self.radio_poly)
		# self.lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		# self.lb.setCursor(Qt.CrossCursor) # 改变鼠标箭头形式
		
		rgb_pix_map = display_image_on_label(rgb_image, self.lb)
		self.lb.set_parameters(rgb_pix_map, self.radio_rect, self.radio_poly, self.cur_img_ann)
		self.lb.setCursor(Qt.CrossCursor)  # 改变鼠标箭头形式

	# 半自动标注的处理函数
	def show_image_semi(self):
		# 获取待显示结果的路径
		rgb_path = os.path.join(self.data_dir, self.test_data[self.image_id])
		rgb_image = cv.imread(rgb_path)
		rgb_pix_map = display_image_on_label(rgb_image, self.mylabel_rgb_semi)
		_ = display_image_on_label(rgb_image, self.label_mask_semi)
		self.mylabel_rgb_semi.set_parameters(rgb_image, rgb_pix_map,
		                                     self.label_mask_semi,
		                                     label_curmarker=self.label_curmarker_semi,
		                                     mask = self.boundary_points)   # 前景分割设置

	# 全自动标注的处理函数
	def show_image_auto(self):
		# 获取待显示结果的路径
		data_dir = self.data_dir.split('/')[:-1]
		result_dir = '/'.join(data_dir) + "/registration_results/"
		rgb_t_fusion_path = result_dir + "rgb_t_fusion/" + self.test_data[self.image_id]
		registered_path = result_dir + "registered/" + self.test_data[self.image_id]
		
		# 显示rgb_t_fusion图像和配准后的红外图像
		rgb_t_fusion_image = cv.imread(rgb_t_fusion_path)
		registered_image = cv.imread(registered_path)
		# if self.radio_semi_auto.isChecked():
		# 	_ = display_image_on_label(rgb_t_fusion_image, self.label_rgbtfusion_auto)
		# 	registered_pix_map = display_image_on_label(registered_image, self.mylabel_registered_auto)
		# 	_ = display_image_on_label(registered_image, self.label_mask_auto)
		# 	self.mylabel_registered_auto.set_parameters(registered_image, registered_pix_map,
		#                                                 self.label_mask_auto,
		#                                                 label_curmarker=self.label_curmarker_auto,
		#                                                 mask = self.boundary_points)   # 前景分割设置
		# elif self.radio_auto_auto.isChecked():
		_ = display_image_on_label(rgb_t_fusion_image, self.label_rgbtfusion_auto)
		registered_pix_map = display_image_on_label(registered_image, self.mylabel_registered_auto)
		mask, self.boundary_points = watershed.App(registered_image.copy()).start()
		_ = display_image_on_label(mask, self.label_mask_auto)

		# 将掩码边界存储起来
		# m = self.markers.copy()
		# cv.watershed(self.img, m)
		# overlay = self.colors[np.maximum(m, 0)]
		# vis = cv.addWeighted(self.img, 0.5, overlay, 0.5, 0.0, dtype=cv.CV_8UC3)
		# display_image_on_label(vis, self.label_mask_auto)
		# ol = overlay.astype(np.uint8)
		# mask_bool = ol[:, :, 2] == 255
		# nonb = mask_bool.nonzero()
		# all_points_y = nonb[0].tolist()
		# all_points_x = nonb[1].tolist()
		# self.mask.clear()
		# self.mask.append(all_points_x)
		# self.mask.append(all_points_y)
		
		self.mylabel_registered_auto.set_parameters(registered_image, registered_pix_map,
		                                            self.label_mask_auto,
		                                            label_curmarker=self.label_curmarker_auto,
		                                            mask=self.boundary_points)  # 前景分割设置
		
		# 添加先验标记和分水岭
		def pre_process():
			gray = cv.cvtColor(registered_image, cv.COLOR_BGR2GRAY)
		
	def on_save(self):
		# 是否进行了标注
		if self.boundary_points == []:
			print("请先进行标注")
			return

		# 转换标注的格式
		regions = []
		regions_item = {}
		name_shape_attributes = "polygon"
		regions_item["shape_attributes"] = {}
		regions_item["shape_attributes"]["name"] = name_shape_attributes
		regions_item["shape_attributes"]["all_points_x"] = self.boundary_points[0]
		regions_item["shape_attributes"]["all_points_y"] = self.boundary_points[1]
		region_attributes = {"type": "power"}
		regions_item["region_attributes"] = region_attributes
		regions.append(regions_item)
		
		img_name = self.test_data[self.image_id]
		self.cur_img_ann["filename"] = img_name
		self.cur_img_ann["size"] = random.randint(0, 1000)
		self.cur_img_ann["file_attributes"] = {}
		self.cur_img_ann["regions"] = regions

		# 保存标注结果
		save_path = "./results/"
		j = json_lib.JSON()
		j.JSONWrite(save_path + img_name[:-4] + ".json", self.cur_img_ann)
		print(img_name + "的标注已保存到" + save_path + img_name[:-4] + ".json")
		
	def water_shed(self, img):
		self.markers_vis = watershed.App(img).run()
		
	def keyPressEvent(self, event):
		ch = event.key()
		cur_marker = ch -  ord('0')
		if 0 < cur_marker < 7:
			if self.tabWidget.currentIndex() == 1:
				self.label_curmarker_semi.setText("current_marker: " + str(cur_marker))
			elif self.tabWidget.currentIndex() == 2:
				self.label_curmarker_auto.setText("current_marker: " + str(cur_marker))

if __name__ == '__main__':
	app = QApplication(sys.argv)
	md = MainCode()
	sys.exit(app.exec_())
