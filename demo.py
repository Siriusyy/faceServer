from mtcnn import MTCNN
import cv2
import time
#video = "http://admin:admin@192.168.0.100:8081"
# 开启摄像头
cap = cv2.VideoCapture(0)
ret=cap.set(3,160)
ret=cap.set(4,160)
ok = cap.isOpened()

dector = MTCNN()

while ok:
    # 读取摄像头中的图像，ok为是否读取成功的判断参数
    ok, img = cap.read()
    # 转换成灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    start = time.time()
    res = dector.detect_faces(gray)
    print(time.time()-start)

    if len(res) > 0:
        for temp in res:
            x = temp["box"][0]
            y = temp["box"][1]
            w = temp["box"][2]
            h = temp["box"][3]

            # 画矩形
            # for (x, y, w, h) in res[0]["box"]:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            # res[0]["keypoints"]["left_eye"]

            cv2.circle(img, temp["keypoints"]["left_eye"],0,(255,255,0),2)
            cv2.circle(img, temp["keypoints"]["right_eye"],0,(255,255,0),2)
            cv2.circle(img, temp["keypoints"]["mouth_left"],0,(255,255,0),2)
            cv2.circle(img, temp["keypoints"]["mouth_right"],0,(255,255,0),2)
            cv2.circle(img, temp["keypoints"]["nose"],0,(255,255,0),2)
            # cv2.circle(img,)

            # for (ex, ey, ew, eh) in result:
            #     cv2.rectangle(img, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

    cv2.imshow('video', img)

    k = cv2.waitKey(1)
    if k == 27:    # press 'ESC' to quit
        break

cap.release()
cv2.destroyAllWindows()