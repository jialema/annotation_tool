import json
import pprint
import random
import cv2 as cv
import numpy as np

class JSON:
    def __init__(self):
        pass

    def JSONRead(self, path):
        with open(path, 'r') as json_f:
            data = json.load(json_f)
        return data

    def JSONWrite(self, path, dict_info):
        with open(path,'w') as json_f:
            json.dump(dict_info, json_f)


def main():
    j = JSON()
    h = j.JSONRead('./json_dir_large/tran_00001.json')

    img = cv.imread("/home/lab407/MyWork/picture_segmentation/Mask_RCNN/datasets/data/rgb_large/tran_00001.jpg")
    mask = np.zeros([img.shape[0], img.shape[1], img.shape[2]], dtype=np.uint8)
    x = h["regions"][0]["shape_attributes"]["all_points_x"]
    y = h["regions"][0]["shape_attributes"]["all_points_y"]
    mask[y, x, 2] = 255
    img = cv.addWeighted(img, 0.5, mask, 0.5, 0.0, dtype=cv.CV_8UC3)
    cv.imshow("1.jpg", img)
    cv.waitKey(0)

    # pprint.pprint(h["regions"][0]["shape_attributes"].keys())
    # # pprint.pprint(h)
    #
    # data = {}
    #
    # filename = "1.jpg"
    # size = random.randint(0, 1000)
    # file_attributes = {}
    #
    # regions = []
    # regions_item = {}
    # name_shape_attributes = "polygon"
    # all_points_x = []
    # all_points_y = []
    # regions_item["shape_attributes"] = {}
    # regions_item["shape_attributes"]["name"] = name_shape_attributes
    # regions_item["shape_attributes"]["all_points_x"] = all_points_x
    # regions_item["shape_attributes"]["all_points_y"] = all_points_y
    # region_attributes = {"type": "balloon"}
    # regions_item["region_attributes"] = region_attributes
    # regions.append(regions_item)
    #
    #
    # data["filename"] = filename
    # data["size"] = size
    # data["regions:"] = regions
    # data["file_attributes"] = file_attributes
    #
    # j = JSON()
    # j.JSONWrite("data.json", data)

if __name__ == "__main__":
    main()