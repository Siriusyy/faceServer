import configparser

from embedding import Facedetection
from embedding import facenetEmbedding
import threading
import socket
import cv2
from scipy import misc
from face_annoy import face_annoy
import dbsql
import os
import numpy


def getEm(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    bboxes, landmarks_list = dec.detect_face(gray, "height")
    for box in bboxes:
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]

        cropped = gray[y:h, x:w, :]

        # 画矩形
        # for (x, y, w, h) in res[0]["box"]:
        # cv2.rectangle(img, (x, y), (w, h), (255, 255, 0), 2)

    resize = misc.imresize(cropped, (160, 160), interp='bilinear')
    embedding = em.get_embedding(resize)
    return embedding.tolist()[0]


def faceReg(sc, addr):
    try:
        infor = sc.recv(1024)  # 首先接收一段数据，这段数据包含文件的长度和文件的名字，使用|分隔，具体规则可以在客户端自己指定
        length, file_name = infor.decode().split('|')
        if length and file_name:
            sc.send(b'ok')  # 表示收到文件长度和文件名
            file = b''
            total = int(length)
            get = 0
            while get < total:  # 接收文件
                data = sc.recv(1024)
                file += data
                get = get + len(data)
            if file:
                data = numpy.frombuffer(file, numpy.uint8)  # 将获取到的字符流数据转换成1维数组
                decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
                sc.send(b'copy')  # 告诉完整的收到文件了
            embedding = getEm(decimg)
            res = face_annoy().query_vector(embedding)
            print(res[1][0])
            if len(res) > 0 and res[1][0] < 0.8:
                name = dbsql.getPriprietoById(res[0][0])
                sc.send("success:".encode("utf-8") + name.encode("utf-8"))
                dbsql.insertVlogs(addr[0],name.encode("utf-8"),'1')
            else:
                sc.send("fail:unknow".encode("utf-8"))
                dbsql.insertVlogs(addr[0], '未识别', '0')

    except IOError as e:
        print(e.strerror)

    finally:
        sc.close()


def createEm(sc):
    try:
        infor = sc.recv(1024)  # 首先接收一段数据，这段数据包含文件的长度和文件的名字，使用|分隔，具体规则可以在客户端自己指定
        id, path = infor.decode().split('|')
        if id and path:
            img = cv2.imread(path)
            embedding = getEm(img)
            res = dbsql.insertOrUpdateEm(id, embedding)
            if res > 0:
                sc.send(b'ok')
            else:
                sc.send(b'fail')

    except IOError as e:
        print(e.strerror)

    finally:
        sc.close()


def service1():
    """
    服务1,处理客户端请求，人脸识别
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((cf.get("ip", "host"), 2020))
    s.listen(10)
    while True:
        c, addr = s.accept()  # 一直等待客户端的连接
        threading.Thread(target=faceReg, args=(c, addr)).start()


def service2():
    """
    服务2,添加业主时生成人脸特征
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((cf.get("ip", "host"), 2021))
    s.listen(10)
    while True:
        c, addr = s.accept()  # 一直等待客户端的连接
        threading.Thread(target=createEm, args=(c,)).start()


def service3():
    """
    服务3,更新特征索引
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((cf.get("ip", "host"), 2022))
    s.listen(10)
    while True:
        c, addr = s.accept()  # 一直等待客户端的连接
        # c.recv(1024)
        try:
            face_annoy().create_index_from_lmdb()
            face_annoy().reload()
            c.send(b'ok')
        except IOError as e:
            print(e.strerror)


print("==============>人脸识别模块载入中...")
dec = Facedetection()
em = facenetEmbedding(os.path.expanduser('~') + "/acs/models/facedetect/20180408-102900")
print("==============>人脸识别模块载入完成")
cf = configparser.ConfigParser()
cf.read(os.path.expanduser('~') + "/acs/config.ini")
if __name__ == '__main__':
    threading.Thread(target=service1, args=()).start()
    threading.Thread(target=service2, args=()).start()
    threading.Thread(target=service3, args=()).start()
