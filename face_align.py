# coding=utf-8

import cv2
import numpy as np
from mtcnn import MTCNN
import os
import time
import random


class Alignment:
    def align_face(self, img, faceKeyPoint):

        # 根据两个鼻子和眼睛进行3点对齐
        eye1 = faceKeyPoint["left_eye"]
        eye2 = faceKeyPoint["right_eye"]
        noise = faceKeyPoint["nose"]
        source_point = np.array(
            [eye1, eye2, noise], dtype=np.float32
        )


        eye1_noraml = [40.2946, 51.6963]
        eye2_noraml = [75.5318, 51.5014]
        noise_normal = [60.0252, 71.7366]
        # 设置的人脸标准模型

        dst_point = np.array(
            [eye1_noraml,
             eye2_noraml,
             noise_normal],
            dtype=np.float32)

        tranform = cv2.getAffineTransform(source_point, dst_point)

        imagesize = tuple([112, 112])
        img_new = cv2.warpAffine(img, tranform, imagesize)
        # cv2.imshow('video', img_new)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return img_new
        # new_image = os.path.abspath("./web/alignface/")
        # new_image = new_image + '/' + '%d_%d.png' % (time.time(), random.randint(0, 100))
        # if cv2.imwrite(new_image, img_new):
        #     return new_image
        # return None


if __name__ == '__main__':
    pic = '/home/yang/Desktop/align.png'
    dector = MTCNN()
    img = cv2.imread(pic)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = dector.detect_faces(gray)
    if len(result):
        align = Alignment()
        align.align_face(img, result[0]['keypoints'])
        # print('align face: ' + )
    else:
        print('not found face')
