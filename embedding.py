import tensorflow as tf
import face_net.src.facenet as facenet
import face_net.src.align.detect_face as detect_face
import numpy as np
import cv2
from scipy import misc
import mydb
import lmdb


class Facedetection:
    def __init__(self):
        self.minsize = 20  # minimum size of face
        self.threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        self.factor = 0.709  # scale factor
        print('Creating networks and loading parameters')
        with tf.Graph().as_default():
            # gpu_memory_fraction = 1.0
            # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
            # sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            sess = tf.Session()
            with sess.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(sess, None)

    def detect_face(self, image, fixed=None):
        '''
        mtcnn人脸检测，
        PS：人脸检测获得bboxes并不一定是正方形的矩形框，参数fixed指定等宽或者等高的bboxes
        :param image:
        :param fixed:
        :return:
        '''
        bboxes, landmarks = detect_face.detect_face(image, self.minsize, self.pnet, self.rnet, self.onet,
                                                    self.threshold, self.factor)
        landmarks_list = []
        landmarks = np.transpose(landmarks)
        bboxes = bboxes.astype(int)
        bboxes = [b[:4] for b in bboxes]
        for landmark in landmarks:
            face_landmarks = [[landmark[j], landmark[j + 5]] for j in range(5)]
            landmarks_list.append(face_landmarks)
        if fixed is not None:
            bboxes, landmarks_list = self.get_square_bboxes(bboxes, landmarks_list, fixed)
        return bboxes, landmarks_list

    def get_square_bboxes(self, bboxes, landmarks, fixed="height"):
        '''
        获得等宽或者等高的bboxes
        :param bboxes:
        :param landmarks:
        :param fixed: width or height
        :return:
        '''
        new_bboxes = []
        for bbox in bboxes:
            x1, y1, x2, y2 = bbox
            w = x2 - x1
            h = y2 - y1
            center_x, center_y = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            if fixed == "height":
                dd = h / 2
            elif fixed == 'width':
                dd = w / 2
            x11 = int(center_x - dd)
            y11 = int(center_y - dd)
            x22 = int(center_x + dd)
            y22 = int(center_y + dd)
            new_bbox = (x11, y11, x22, y22)
            new_bboxes.append(new_bbox)
        return new_bboxes, landmarks


class facenetEmbedding:
    def __init__(self, model_path):
        self.sess = tf.InteractiveSession()
        self.sess.run(tf.global_variables_initializer())
        # Load the model
        facenet.load_model(model_path)
        # Get input and output tensors
        self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        self.tf_embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

    def get_embedding(self, images):
        prewhiten_face = facenet.prewhiten(images)
        feed_dict = {self.images_placeholder: [prewhiten_face], self.phase_train_placeholder: False}
        embedding = self.sess.run(self.tf_embeddings, feed_dict=feed_dict)
        return embedding

    def free(self):
        self.sess.close()


if __name__ == '__main__':
    img = cv2.imread("/home/yang/Desktop/test16.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    dec = Facedetection()
    bboxes, landmarks_list = dec.detect_face(gray, "height")
    print(landmarks_list)
    for box in bboxes:
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]

        cropped = gray[box[1]:box[3], box[0]:box[2], :]

        # 画矩形
        # for (x, y, w, h) in res[0]["box"]:
        cv2.rectangle(img, (x, y), (w, h), (255, 255, 0), 2)

    resize = misc.imresize(cropped, (160, 160), interp='bilinear')
    cv2.namedWindow('input_image', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('input_image', resize)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    em = facenetEmbedding("./models/facedetect/20180408-102900")
    embedding = em.get_embedding(resize)
    # print(embedding)
    # print(len(embedding))
    db = mydb.mLmdb()
    db.add_embed_to_lmdb("10006", embedding.tolist()[0])

    # 遍历
    evn = lmdb.open(db.db_file)
    wfp = evn.begin()
    for key, value in wfp.cursor():
        print(key, mydb.str_to_embed(value))
